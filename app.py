import json
import secrets
from contextlib import nullcontext
from random import Random

from websockets.asyncio.server import serve
import asyncio
import GameV2
import http
import os
import signal

JOIN = {}
WATCH = {}
GAMES = {}

async def bot_game(websocket):
    game: GameV2 = GameV2.Game()
    connected = {websocket}
    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected
    try:
        ev = {
            "type": "init",
            "color": "W",
            "watch": watch_key,
        }
        await websocket.send(json.dumps(ev))
        bot = GameV2.Bot_V1()
        async for message in websocket:
            event = json.loads(message)
            if event["type"] == "unload":
                ev = {
                    "type": "mate",
                    "player": "W"
                }
                for socket in connected:
                    await socket.send(json.dumps(ev))
            if game.turn:
                if event["type"] == "play":
                    if game.play_move(event["move"]):
                        await play_move(game.moves[len(game.moves) - 1], connected)
                        await check_game_end(game, connected)
                        bot_move = bot.play_move(3,game)
                        game.play_move(bot_move)
                        await play_move(bot_move, connected)
                        await check_game_end(game, connected)
    finally:
        del WATCH[watch_key]

async def pvp_game(websocket):
    game = None
    connected = None
    color = None
    join_key = secrets.token_urlsafe(12)
    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected
    if len(GAMES.keys()) == 0:
        game = GameV2.Game()
        connected = {websocket}
        r = Random()
        color = r.randint(0, 1)
        GAMES[join_key] = game, connected, not color, False
    else:
        try:
            join_key = get_pvp_game()
            game,connected,color,unused = GAMES[join_key]
            connected.add(websocket)
            await replay_moves(game, websocket)
        except KeyError:
            game = GameV2.Game()
            connected = {websocket}
            r = Random()
            color = r.randint(0, 1)
            GAMES[join_key] = game, connected, not color, False
    try:
        ev = {
            "type": "init",
            "color": "W" if color else "B",
            "watch":watch_key,
        }
        await websocket.send(json.dumps(ev))
        async for message in websocket:
            event = json.loads(message)
            if event["type"] == "unload":
                ev = {
                    "type": "mate",
                    "player": "B" if color else "W"
                }
                for socket in connected:
                    await socket.send(json.dumps(ev))
            if game.turn == color:
                if event["type"] == "play":
                    if game.play_move(event["move"]):
                        await play_move(game.moves[len(game.moves) - 1], connected)
                        await check_game_end(game, connected)
    finally:
        del GAMES[join_key]
        del WATCH[watch_key]




def get_pvp_game():
    for g in GAMES.keys():
        if not GAMES[g][3]:
            GAMES[g] = GAMES[g][0], GAMES[g][1], GAMES[g][2], True
            return g
    return None


async def joinable_game(websocket):
    r = Random()
    game = GameV2.Game()
    connected = {websocket}
    join_key = secrets.token_urlsafe(12)
    color = r.randint(0,1)==0
    JOIN[join_key] = game, connected, color
    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected
    try:
        ev = {
            "type": "init",
            "color": "W" if color else "B",
            "join": join_key,
            "watch":watch_key,
        }
        await websocket.send(json.dumps(ev))
        async for message in websocket:
            event = json.loads(message)
            if event["type"] == "unload":
                ev = {
                    "type": "mate",
                    "player": "B" if color else "W"
                }
                for socket in connected:
                    await socket.send(json.dumps(ev))
            if game.turn == color:
                if event["type"] == "play":
                    if game.play_move(event["move"]):
                        await play_move(game.moves[len(game.moves) - 1], connected)
                        await check_game_end(game, connected)
    finally:
        del JOIN[join_key]
        del WATCH[watch_key]

async def error(websocket, message):
    ev = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(ev))


async def join_game(websocket, join_key):
    game = None
    connected = None
    color = None
    try:
        game,connected,color = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found")
    connected.add(websocket)
    color = not color
    try:
        ev = {
            "type": "init",
            "color": "W" if color else "B",
        }
        await websocket.send(json.dumps(ev))
        await replay_moves(game, websocket)
        async for message in websocket:
            event = json.loads(message)
            if event["type"] == "unload":
                ev = {
                    "type": "mate",
                    "player": "B" if game.turn else "W"
                }
                for socket in connected:
                    await socket.send(json.dumps(ev))
            if game.turn == color:
                if event["type"] == "play":
                    if game.play_move(event["move"]):
                        await play_move(game.moves[len(game.moves) - 1], connected)
                        await check_game_end(game, connected)
    finally:
        connected.remove(websocket)

async def play_move(move, connected):
    ev = {
        "type": "play",
        "move": move,
    }
    for socket in connected:
        await socket.send(json.dumps(ev))

async def check_game_end(game, connected):
    if game.check_checkmate():
        ev = {
            "type": "mate",
            "player": "B" if game.turn else "W",
        }
        for socket in connected:
            await socket.send(json.dumps(ev))
    elif game.check_stalemate():
        ev = {
            "type": "stalemate",
        }
        for socket in connected:
            await socket.send(json.dumps(ev))


async def watch_game(websocket, watch_key):
    connected: set = None
    game: GameV2.Game = None
    try:
        game, connected = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Game not found")
    connected.add(websocket)
    try:
        ev = {
            "type": "init",
            "color": "W",
        }
        await websocket.send(json.dumps(ev))
        await replay_moves(game, websocket)
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)


async def replay_moves(game: GameV2.Game, socket):
    for move in game.moves:
        ev = {
            "type": "play",
            "move": move,
        }
        await socket.send(json.dumps(ev))

async def handler(websocket):
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"
    if event["game_type"]=='pvb':
        await bot_game(websocket)
    elif event["game_type"]=='pvj':
        await joinable_game(websocket)
    elif event["game_type"]=='jvp':
        await join_game(websocket,event["join"])
    elif event["game_type"]=='watch':
        await watch_game(websocket,event["watch"])
    elif event["game_type"]=='pvp':
        await pvp_game(websocket)

def health_check(connection, request):
    if request.path == "/healthz":
        return connection.respond(http.HTTPStatus.OK, "OK\n")

async def main():
    port = int(os.environ.get("PORT", "8001"))
    async with serve(handler, "", port, process_request=health_check) as server:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, server.close)
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())