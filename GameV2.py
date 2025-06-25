from random import Random

import ChessboardV2


class Game:
    def __init__(self):
        """creates a default chess game, position holder is for getting moves faster"""
        self.board: ChessboardV2.Board = ChessboardV2.Board()
        self.turn: bool = True
        self.moves: list[str] = []

    def check_stalemate(self):
        return len(self.get_legal_moves()) == 0

    def check_check(self):
        return self.board.check_check(self.turn,self.moves, False)

    def check_checkmate(self):
        return self.check_check() and self.check_stalemate()

    def get_legal_moves(self):
        """returns legal moves"""
        return self.board.get_legal_moves(self.turn, self.moves)

    def play_move(self, move: str) -> bool:
        """returns true and plays move if the move was legal, else doesn't play the move"""
        legal_moves = self.get_legal_moves()
        for legal_move in legal_moves:
            #if we are moving the same way in move and legal move
            if move[:2] == legal_move[:2]:
                #if we are promoting in the legal move
                if legal_move[2].lower() in ["q","b","r","n"]:
                    #figure out what the player wants to promote to and set legal move to that
                    if move[2] == "♛":
                        legal_move = move[:2] + ("Q" if self.turn else "q")
                    if move[2] == "♞":
                        legal_move = move[:2] + ("N" if self.turn else "n")
                    if move[2] == "♝":
                        legal_move = move[:2] + ("B" if self.turn else "b")
                    if move[2] == "♜":
                        legal_move = move[:2] + ("R" if self.turn else "r")
                #play the legal move
                self.board.play_move(legal_move)
                self.turn = not self.turn
                self.moves.append(legal_move)
                #return true to tell the program we have promoted
                return True
        return False

    def __copy__(self):
        copy = Game()
        copy.board.board = self.board.board
        copy.turn = self.turn
        copy.moves = self.moves.copy()
        return copy

    def sim_game(self, move: str):
        """creates a simulation of the current game where move has been played"""
        sim = self.__copy__()
        sim.play_move(move)
        return sim

    def game_end(self):
        return self.check_checkmate() or self.check_stalemate()

class Bot_V1:
    def evaluate(self, game:Game):
        board: ChessboardV2.Board = game.board
        score: float = 0.0
        for index in range(0,len(board.board)):
            tile = board.board[index]
            if not tile == "_":
                #rook
                if tile == "R":
                    score += (5 + (ChessboardV2.index_row(index)/ 7))
                if tile == "r":
                    score -= (5 + ((8-ChessboardV2.index_row(index))/7))
                #knight
                if tile == "N":
                    score += (3 + (ChessboardV2.index_row(index)/ 7))
                if tile == "n":
                    score -= (3 + ((8-ChessboardV2.index_row(index))/7))
                #Bishop
                if tile == "B":
                    score += (3.5 + (ChessboardV2.index_row(index)/ 7))
                if tile == "b":
                    score -= (3.5 + ((8-ChessboardV2.index_row(index))/7))
                #rook
                if tile == "Q":
                    score += (8 + (ChessboardV2.index_row(index)/ 7))
                if tile == "q":
                    score -= (8 + ((8-ChessboardV2.index_row(index))/7))
                #rook
                if tile == "K":
                    score += 100
                if tile == "k":
                    score -= 100
                #Pawn
                if tile == "P":
                    score += (1 + (ChessboardV2.index_row(index)/ 7))
                if tile == "p":
                    score -= (1 + ((8-ChessboardV2.index_row(index))/7))

        return round(score, 3)

    def play_move(self,depth: int, game: Game):
        tree: TreeNode = TreeNode(game)
        tree.generate_moves(self, depth, 0, -99999, 99999, "")
        score = tree.score
        moves = []
        r = Random()
        for move in tree.children:
            if move.score == score:
                print(score)
                return move.move
        if len(moves) == 0:
            raise Exception("FUCK YOU BALTIMORE (there were no moves)")
        return moves[r.randrange(0, len(moves))]

class TreeNode:
    def __init__(self, game: Game):
        self.game: Game = game
        self.children: list[TreeNode] = []
        self.score: float = None
        self.move = ""

    def generate_moves(self, bot, depth, extend, alpha, beta, move):
        self.move = move
        if (depth + extend) == 0 or (extend == 3):
            self.score = bot.evaluate(self.game)
            return self.score
        legal_moves = self.game.get_legal_moves()
        if self.game.check_stalemate():
            return 0
        #max
        if self.game.turn:
            self.score = -99999
            for move in legal_moves:
                new_node = TreeNode(self.game.sim_game(move))
                self.score = max(new_node.generate_moves(bot, depth - 1, extend, alpha, beta, move), self.score)
                alpha = max(self.score, alpha)
                if beta <= alpha:
                    break
                self.children.append(new_node)
            return self.score
        #min
        else:
            self.score = 99999
            for move in legal_moves:
                new_node = TreeNode(self.game.sim_game(move))
                self.score = min(new_node.generate_moves(bot, depth - 1, extend, alpha, beta, move), self.score)
                beta = min(self.score, beta)
                if beta <= alpha:
                    break
                self.children.append(new_node)
            return self.score