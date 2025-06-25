let move = "";
let promotion_piece = "♛";
let move_number = 0;
let game_type = "";
let color = "";

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
	let menu_grid = newDiv("main_menu_grid");
	
	let new_game_div = newDiv("new_game_button_div");
	let new_game_button = create_a_element("new_game_button", '/?do=pvp',"New PVP Game");
	new_game_div.append(new_game_button);
	menu_grid.append(new_game_div);
	
	let new_bot_game_div = newDiv("new_game_button_div");
	let new_bot_game_button = create_a_element("new_game_button", '/?do=pvb',"New Bot Game");
	new_bot_game_div.append(new_bot_game_button);
	menu_grid.append(new_bot_game_div);
	
	
	let new_join_game_div = newDiv("new_game_button_div");
	let new_join_game_button = create_a_element("new_game_button", '/?do=pvj',"New Joinable Game");
	new_join_game_div.append(new_join_game_button);
	menu_grid.append(new_join_game_div);
	
	b.append(menu_grid);
}


function createGame(){
	let b = document.querySelector(".body");
	let board_div = newDiv("board");
	b.append(board_div);
	let moves_display_div = newDiv("moves_display");
	b.append(moves_display_div);
	let promotion_selector_div = newDiv("promotion_selector");
	b.append(promotion_selector_div);
	const websocket = new WebSocket("ws://localhost:8001/");
	const board = document.querySelector(".board");
	startGame(websocket);
	setupReceiveEvent(board, websocket);
	setupPlayEvent(board, websocket);
	const promotion_selector = document.querySelector(".promotion_selector");
	setupPromotionSelector(promotion_selector);
}

function create_a_element(className,href,innerText){
	let a_element = document.createElement("a");
	a_element.className = className;
	a_element.href = href;
	a_element.innerText = innerText;
	return a_element;
}

function newDiv(className){
	let div = document.createElement("div");
	div.className = className;
	return div;
}

function onWin (winner, websocket){
	websocket.close(1000);
	let b = document.querySelector(".body");
	//end text box creation
	let end_text_box = newDiv("after_game_actions");
	let end_text = newDiv("action white_piece");
	end_text.innerText = (winner == "W"?"White":"Black") + " Wins!";
	end_text_box.append(end_text);
	//new game button creation
	let new_game_div = newDiv("action");
	let new_game_button = create_a_element("new",`/?do=${(game_type == "jvp"?"pvj":game_type)}`,"New Game");
	new_game_div.append(new_game_button);
	end_text_box.append(new_game_div);
	//main menu button creation
	let main_menu_div = newDiv("action");
	let main_menu_button = create_a_element("new",`/`,"Main Menu");
	main_menu_div.append(main_menu_button);
	end_text_box.append(main_menu_div);
	b.append(end_text_box);
}

function indexToBoardCoordinates(index){
	return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@".at(index);
}

function boardCoordinatesToIndex(coordinate){
	return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@".indexOf(coordinate);
}

function indexColumn(index){
	return index % 8;
}

function indexRow(index){
	return Math.floor(index/8);
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
		if (piece == undefined || piece == promotion_piece){
			return;
		}
		let new_select = filterForInnerText(document.querySelectorAll('.promotion_square'),piece);
		let old_select = document.querySelector('.promotion_select');
		console.log(new_select);
		console.log(old_select);
		old_select.className = "promotion_square" + old_select.className.substr(16);
		new_select.className = "promotion_select" + new_select.className.substr(16);
		promotion_piece = piece;
	});
}

function filterForInnerText(element_array, text_to_search_for){
	for(let i = 0; i < element_array.length; i++){
		if(element_array[i].innerText == text_to_search_for){
			return element_array[i];
		}
	}
	return null;
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
					let b = document.querySelector(".body");
					let join_div = newDiv("join_div");
					let join_link = create_a_element("join_link",`/?do=jvp&join=${ev.join}`,"Join link")
					join_div.append(join_link);
					b.append(join_div);
				}
				if (ev.watch != undefined){
					let b = document.querySelector(".body");
					let watch_div = newDiv("join_div");
					let watch_link = create_a_element("join_link",`/?do=watch&watch=${ev.watch}`,"Watch link")
					watch_div.append(watch_link);
					b.append(watch_div);
				}
				break;
			case "error":
				window.setTimeout(() => window.alert(ev.message), 50);
				websocket.close(1000);
		}
	});
}

function displayMove(move){
	let display_elem = document.querySelector(".moves_display");
	let move_display = document.createElement("div");
	move_display.innerText = move;
	if(move_number % 2 == 0){
		let number_display = newDiv("move_number_square");
		number_display.innerText = (move_number/2) + 1;
		display_elem.append(number_display);
		move_display.className = "move_display_square white";
		display_elem.append(move_display);
	}else{
		move_display.className = "move_display_square black black_move";
		display_elem.append(move_display);
	}
	move_number++;
}

function makeMoveReadable(move){
	const move_x = indexColumn(boardCoordinatesToIndex(move.at(1)));
	const move_y = indexRow(boardCoordinatesToIndex(move.at(1))+1);
	const piece = document.querySelector('[data-index="'+move.at(0)+'"]').innerText;
	return `${piece}${"abcdefgh".at(move_x)}${move_y}`
}

function playMove(board, move){
	const start_coord = move.at(0);
	const end_coord = move.at(1);
	displayMove(makeMoveReadable(move));
	switch (move.at(2)){
		case "_":
			swapTiles(start_coord, end_coord);
			break;
		case "e":
			swapTiles(start_coord, end_coord);
			clearTile(indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 1));
			break;
		case "E":
			swapTiles(start_coord, end_coord);
			clearTile(indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 1));
			break;
		case "c":
			let right_rook_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 3);
			let right_rook_move_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) + 1);
			swapTiles(start_coord, end_coord);
			swapTiles(right_rook_coord, right_rook_move_coord);
			break;
		case "C":
			let left_rook_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 4);
			let left_rook_move_coord = indexToBoardCoordinates(boardCoordinatesToIndex(start_coord) - 1);
			swapTiles(start_coord, end_coord);
			swapTiles(left_rook_coord, left_rook_move_coord);
			break;
		default:
			swapTiles(start_coord, end_coord);
			let end_tile = document.querySelector('[data-index="'+end_coord+'"]');
			end_tile.innerText = promotion_piece;
			break;
	}
}

function clearTile(tile_coord){
	let tile = document.querySelector('[data-index="'+tile_coord+'"]');
	tile.innerHTML = "";
	tile.className = tile.className.substr(0,10);
}

function swapTiles(start_coord, end_coord){
	let start_tile = document.querySelector('[data-index="'+start_coord+'"]');
	let end_tile = document.querySelector('[data-index="'+end_coord+'"]');
	end_tile.className = end_tile.className.substr(0,10) + pieceColorAtCoordinate(start_coord);
	start_tile.className = start_tile.className.substr(0,10);
	end_tile.innerText = start_tile.innerText;
	start_tile.innerText = "";
}

function pieceColorAtCoordinate(coordinate){
	let index_class = document.querySelector('[data-index="'+coordinate+'"]').className;
	if (index_class.length > 10){
		return index_class.substr(10);
	}
	return "";
}

function createBoard(board){
	let tile_list = [];
	let tileColorFlip = false;
	for (let index = 0; index < 64; index++){
		let cname = ""
    const tileElement = document.createElement("div");
		if (index % 8 == 0){
			tile_list.push([]) ;
			if (tileColorFlip){
				tileColorFlip = false
			}else{
				tileColorFlip = true;
			}
		}
		if (tileColorFlip){
			if (index % 2 == 0){
				cname = "white tile";
			}
			else{
				cname = "black tile";
			}
		}else{
			if (index % 2 == 1){
				cname = "white tile";
			}
			else{
				cname = "black tile";
			}
		}
		tileElement.innerText = getPieceAtIndex(index, cname, tileElement);
    tileElement.dataset.index = indexToBoardCoordinates(index);
		tile_list[tile_list.length - 1].push(tileElement);
  }
	if (color == "W"){
		tile_list = tile_list.reverse();
	}
	tile_list.forEach(function(list){list.forEach(function(tile){board.append(tile)})})
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