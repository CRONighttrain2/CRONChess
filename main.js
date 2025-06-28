let move = "";
let promotion_piece = "♛";
let move_number = 0;
let game_type = "";
let color = "";
//helper functons
const getTile = (coord) => {return document.querySelector(`[data-index="${coord}"]`);}
const getElement = (elemClass) => {return document.querySelector(`.${elemClass}`);}
const indexToBoardCoordinates = (index) =>{return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@".at(index);}
const boardCoordinatesToIndex = (coordinate) => {return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@".indexOf(coordinate);}
const indexColumn = (index) =>{return index % 8;}
const indexRow = (index) => {return Math.floor(index/8);}
const createDiv = (className)=>{
	let div = document.createElement("div");
	div.className = className;
	return div;
}
const createAElement = (className, divClassName ,href,innerText) =>{
	let new_div = createDiv(divClassName);
	let a_element = document.createElement("a");
	a_element.className = className;
	a_element.href = href;
	a_element.innerText = innerText;
	new_div.append(a_element);
	return new_div;
}

const createEndOfGameActions = (end_text) =>{
	let b = document.querySelector(".body");
	//end text box creation
	let end_text_box = createDiv("after_game_actions");
	let end_text_div = createDiv("action white_piece");
	end_text_div.innerText = end_text;
	end_text_box.append(end_text_div);
	//new game button creation
	end_text_box.append(createAElement("new", "action",`/CRONChess/?do=${(game_type == "jvp"?"pvj":game_type)}`,"New Game"));
	//main menu button creation
	end_text_box.append(createAElement("new","action", `/CRONChess/`,"Main Menu"));
	b.append(end_text_box);

} 

function getWebSocketServer() {
  if (window.location.host === "cronighttrain2.github.io") {
    return "wss://open-caitlin-cronight-56ae1cd5.koyeb.app/";
  } else if (window.location.host === "localhost:8000") {
    return "ws://localhost:8001/";
  } else {
    throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const linkElement = document.createElement("link");
  linkElement.href = import.meta.url.replace(".js", ".css");
  linkElement.rel = "stylesheet";
  document.head.append(linkElement);
	const params = new URLSearchParams(window.location.search);
	if(params.has("do")){
		createGame();
	}else{
		createMainMenu();
	}
});

function createMainMenu(){
	let b = document.querySelector(".body");
	let menu_grid = createDiv("main_menu_grid");
	let new_game_button = createAElement("new_game_button", "new_game_button_div", '/CRONChess/?do=pvp',"New PVP Game");
	let new_join_game_button = createAElement("new_game_button", "new_game_button_div", '/CRONChess/?do=pvj',"New Joinable Game");
	menu_grid.append(new_game_button);
	menu_grid.append(new_join_game_button);
	b.append(menu_grid);
}

function createGame(){
	let b = document.querySelector(".body");
	let board_div = createDiv("board");
	b.append(board_div);
	let moves_display_div = createDiv("moves_display");
	b.append(moves_display_div);
	const websocket = new WebSocket(getWebSocketServer());
	const board = getElement("board");
	startGame(websocket);
	setupReceiveEvent(board, websocket);
	setupPlayEvent(board, websocket);
	let promotion_selector_div = createDiv("promotion_selector");
	b.append(promotion_selector_div);
	const promotion_selector = getElement("promotion_selector");
	setupPromotionSelector(promotion_selector);
}

function onStalemate (websocket){
	websocket.close(1000);
	createEndOfGameActions(b, `Stalemate!`);
}

function onWin (winner, websocket){
	websocket.close(1000);
	createEndOfGameActions(`${winner == "W"?"White":"Black"} + Wins!`);
}

function setupPromotionSelector(promotion_selector){
	const promotion_pieces = ["♛", "♞", "♜", "♝"];
	for(let index = 0; index < promotion_pieces.length; index++){
		let selector_element = document.createElement("div");
		selector_element.innerText = promotion_pieces[index];
		selector_element.className = (index == 0? "promotion_select": "promotion_square") + " white_piece"
		promotion_selector.append(selector_element);
	}
	promotion_selector.addEventListener("click", ({target}) => {
		let piece = target.innerText;
		if (piece == undefined || piece == promotion_piece){return;}
		let new_select = Array.of(document.querySelectorAll('.promotion_square')).find(piece);
		let old_select = getElement("promotion_select");
		old_select.className = "promotion_square" + old_select.className.substring(16);
		new_select.className = "promotion_select" + new_select.className.substring(16);
		promotion_piece = piece;
	});
}

function setupReceiveEvent(board, websocket){
	websocket.addEventListener("message", ({ data }) => {
		const ev = JSON.parse(data);
		switch(ev.type){
			case "play":
				playMove(board, ev.move);
				break;
			case "mate":
				onWin(ev.player, websocket);
				break;
			case "init":
				color = ev.color;
				createBoard(board);
				if (ev.join != undefined){
					let b = getElement("body");
					let join_link = createAElement("join_link","join_div",`/CRONChess/?do=jvp&join=${ev.join}`,"Join link");
					b.append(join_link);
				}
				if (ev.watch != undefined){
					let b = getElement("body");
					let watch_link = createAElement("join_link","join_div",`/CRONChess/?do=watch&watch=${ev.watch}`,"Watch link");
					b.append(watch_link);
				}
				break;
			case "error":
				window.setTimeout(() => window.alert(ev.message), 50);
				websocket.close(1000);
				break;
			case "stalemate":
				onStalemate(websocket);
				break;
				
		}
	});
}

function displayMove(move){
	let display_elem = getElement("moves_display");
	let move_display = document.createElement("div");
	move_display.innerText = move;
	move_display.className = "move_display_square black black_move";
	if(move_number % 2 == 0){
		let number_display = createDiv("move_number_square");
		number_display.innerText = (move_number/2) + 1;
		display_elem.append(number_display);
		move_display.className = "move_display_square white";
	}
	display_elem.append(move_display);
	move_number++;
}

function makeMoveReadable(move){
	const move_x = indexColumn(boardCoordinatesToIndex(move.at(1)));
	const move_y = indexRow(boardCoordinatesToIndex(move.at(1))+1);
	const piece = getTile(move.at(0)).innerText;
	return `${piece}${"abcdefgh".at(move_x)}${move_y}`
}

function playMove(move){
	const start_coord = move.at(0);
	const end_coord = move.at(1);
	displayMove(makeMoveReadable(move));
	swapTiles(start_coord, end_coord);
	let rook_coord = 0;
	let rook_move_coord=0;
	switch (move.at(2)){
		case "_":
			break;
		case "e":
			clearTile(indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 1));
			break;
		case "E":
			clearTile(indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 1));
			break;
		case "c":
			rook_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 3);
			rook_move_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 1);
		case "C":
			rook_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 4);
			rook_move_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 1);
			swapTiles(rook_coord, rook_move_coord);
			break;
		default:
			let end_tile = getTile(end_coord);
			end_tile.innerText = promotion_piece;
			break;
	}
}

function clearTile(tile_coord){
	let tile = document.querySelector('[data-index="'+tile_coord+'"]');
	tile.innerHTML = "";
	tile.className = tile.className.substring(0,10);
}



function swapTiles(start_coord, end_coord){
	let start_tile = getTile(start_coord);
	let end_tile = getTile(end_coord);
	end_tile.className = end_tile.className.substring(0,10) + pieceColorAtCoordinate(start_coord);
	start_tile.className = start_tile.className.substring(0,10);
	end_tile.innerText = start_tile.innerText;
	start_tile.innerText = "";
}

function pieceColorAtCoordinate(coordinate){
	let index_class = getTile(coordinate).className;
	if (index_class.length > 10){
		return index_class.substring(10);
	}
	return "";
}

function createBoard(board){
	let tile_list = [];
	let tileColorFlip = true;
	for (let index = 0; index < 64; index++){
		if (index % 8 == 0){
			tile_list.push([]);
			tileColorFlip = !tileColorFlip;
		}
		let cname = index % 2 == Number(tileColorFlip)?"white tile":"black tile";
    	const tileElement = document.createElement("div");
		tileElement.innerText = getPieceAtIndex(index, cname, tileElement);
    	tileElement.dataset.index = indexToBoardCoordinates(index);
		tile_list[tile_list.length - 1].push(tileElement);
    }
	if (color == "W"){tile_list = tile_list.reverse();}
	tile_list = tile_list.flat()
	tile_list.forEach((elem) => board.append(elem))
}

function getPieceAtIndex(index, cname, tileElement){
	if (index < 16){
		tileElement.className = cname + " white_piece";
	}else if(index > 47){
		tileElement.className = cname + " black_piece";
	}else{
		tileElement.className = cname;
		return "";
	}
	if(index == 0 || index == 7 || index == 56 || index == 63){
		return "♜";
	}
	if(index == 1 || index == 6 || index == 57 || index == 62){
		return "♞";
	}
	if(index == 2 || index == 5 || index == 58 || index == 61){
		return "♝";
	}
	if(index == 3 || index == 59){
		return "♛";
	}
	if(index == 4 || index == 60){
		return "♚";
	}
	if (index < 16 || index > 47){
		return "♟"
	}
}

function setupPlayEvent(board, websocket){
	board.addEventListener("click", ({target}) =>{
		const index = target.dataset.index;
		if (index == undefined){
			return;
		}
		if (move == ""){
			if(target.innerText !== "" && pieceColorAtCoordinate(index).includes("white")?"W"==color:"B"==color){
				move = index;
			}
		}else{
			const ev = {
				type: "play",
				move: (move + index + promotion_piece),
			}
			websocket.send(JSON.stringify(ev))
			move = ""
		}
	});
}

function startGame(websocket){
	websocket.addEventListener("open", () => {
		const params = new URLSearchParams(window.location.search);
		const ev = {
			type: "init",
		}
		if(params.has("do")){
			game_type = params.get("do");
			ev.game_type = params.get("do");
		}
		if(params.has("join")){
			ev.join = params.get("join");
		}
		if(params.has("watch")){
			ev.watch = params.get("watch");
		}
		websocket.send(JSON.stringify(ev));
	});
}
