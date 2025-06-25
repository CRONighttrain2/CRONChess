def movement_square_encoder(move_index: int) -> str:
    """turns the index of a move into a character for storage"""
    if move_index < 0: raise IndexError("move index less than 0")
    return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@"[move_index]

def movement_square_decoder(move_letter:str) -> int:
    """converts from above method back into a index number"""
    index = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@".find(move_letter)
    if index < 0: raise ValueError("move_letter not in accepted letters")
    return index

def display_square_codes():
    b: list[str] = ["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@"[x:(x + 8)] for x in range(0, 64, 8)]
    b.reverse()
    for row in b:
        print(row)

def index_column(index: int)-> int:
    """returns the column that the inputted index would be on, used to find how far to the left/ right edge of the board"""
    return index % 8

def index_row(index: int) -> int:
    """returns the row that the inputted index would be on, used to find how far to the top/ bottom edge of the board"""
    return int(str(index/8)[0])

def same_color(piece1: str, piece2: str) -> bool:
    """returns true if both inputs are uppercase or both inputs are lowercase (thus the same color)"""
    return not ((piece1.upper() == piece1) ^ (piece2.upper() == piece2))

def coordinates_to_index(x:int, y:int):
    """converts from row and column to index in board"""
    return x + (y * 8)

def generate_move(start_index: int, end_index: int, special: str):
    return movement_square_encoder(start_index) + movement_square_encoder(end_index) + special

class Board:
    def __init__(self):
        self.board = "RNBQKBNRPPPPPPPP________________________________pppppppprnbqkbnr"
        #used to prevent infinite loops
        self.sim = False

    def __copy__(self):
        new_board = Board()
        new_board.board = self.board
        return new_board

    def replace_index(self, index: int, piece: str):
            self.board = self.board[:index] + piece + self.board[(index+1):]

    def play_move(self, move:str):
        start_index = movement_square_decoder(move[0])
        end_index = movement_square_decoder(move[1])
        #normal movement
        if move[2] == "_":
            self.replace_index(end_index,self.board[start_index])
            self.replace_index(start_index,"_")
        #en-passant
        elif move[2].lower() == "e":
            # E == left enpassant
            self.replace_index(start_index + (-1 if move[2] == "E" else 1), "_")
            self.replace_index(end_index, self.board[start_index])
            self.replace_index(start_index, "_")
        #castling
        elif move[2].lower() == "c":
            # C == left castle
            if move[2] == "C":
                rook_index = start_index - 4
                self.replace_index(start_index - 2, self.board[start_index])
                self.replace_index(start_index - 1, self.board[rook_index])
                self.replace_index(start_index, "_")
                self.replace_index(rook_index, "_")
            else:
                rook_index = start_index + 3
                self.replace_index(start_index + 2, self.board[start_index])
                self.replace_index(start_index + 1, self.board[rook_index])
                self.replace_index(start_index, "_")
                self.replace_index(rook_index, "_")
        #promotion
        else:
            self.replace_index(start_index,"_")
            self.replace_index(end_index,move[2])

    def simulate_move(self, move):
        board = self.__copy__()
        board.play_move(move)
        board.sim = True
        return board

    def display(self):
        b:list[str] = [self.board[x:(x+8)] for x in range(0,64,8)]
        b.reverse()
        for row in b:
            print(row)

    def get_moves_in_row(self, start_index: int, x_offset: int, y_offset: int, piece: str, one_move: bool) -> list[str]:
        """returns all the available moves along a line defined by x_offset and y_offset"""
        output: list[str] = []
        start_x = index_column(start_index)
        start_y = index_row(start_index)
        #offset starts at one so we don't detect the piece we are starting from
        for offset_amount in range(1, 2 if one_move else 8):
            new_x = start_x + (x_offset * offset_amount)
            new_y = start_y + (y_offset * offset_amount)
            #if we are out of bounds break
            if new_x > 7 or new_x < 0 or new_y > 7 or new_y < 0:
                break
            new_index = coordinates_to_index(new_x, new_y)
            tile = self.board[new_index]
            if tile == "_":
                output.append(generate_move(start_index,new_index,"_"))
            else:
                if not same_color(tile, piece):
                    output.append(generate_move(start_index,new_index,"_"))
                #always break when hitting a piece
                break
        return output

    def check_check(self, turn: bool, played_moves: list[str], checking_check: bool) -> bool:
        """checks if the king is in check"""
        if checking_check:
            return False
        if (self.board.find("K") if turn else self.board.find("k")) == -1:
            return True
        king_index = movement_square_encoder(self.board.find("K") if turn else self.board.find("k"))
        potential_moves = self.get_moves(not turn, played_moves, True)
        for move in potential_moves:
            if king_index in move[1]:
                return True
        return False

    def search_castle(self, index: int, piece: str, played_moves: list[str], checking_check: bool) -> list[str]:
        """searches for castling (look it up)"""
        output = []
        turn = same_color(piece, "A")
        #if we are in a simulated board return so no infinite loop (also panic cause reality is a lie)
        if self.sim or self.check_check(turn, played_moves, checking_check):
            return output
        #if the king isn't in the correct spot
        if not (index == 4 or index == 60):
            return output
        #indexes for the rooks so we aren't calling movement_square_encoder over and over
        left_rook_index = movement_square_encoder(index - 4)
        right_rook_index = movement_square_encoder(index + 3)
        left = True
        right = True
        #checks if the rooks haven't moved and aren't taken
        for move in played_moves:
            if left and (left_rook_index in move):
                left = False
            if right and (right_rook_index in move):
                right = False
            if not left and not right:
                #return early if both rooks have moved/ been taken
                return output
        #if there is a rook left
        if left:
            for offset in range(1,4):
                search_index = index-offset
                #only the tiles that the king is passing over matter for checks
                if offset < 3:
                    #create a new simulated board and hope it's inhabitants don't panic
                    sim = self.simulate_move(generate_move(index, search_index,"_"))
                    if sim.check_check(turn, played_moves, False):
                        left = False
                        #return early if we can't castle to the right as we cannot castle left either
                        if not right:
                            return output
                        break
                tile = self.board[search_index]
                if not tile == "_":
                    left = False
                    #return early if we can't castle to the right as we cannot castle left either
                    if not right:
                        return output
                    break
        #if we can castle left add it to the list of possible moves
        if left:
            output.append(generate_move(index,index - 2,"C"))
        for offset in range(1, 3):
            search_index = index + offset
            #create a new simulated board and hope it's inhabitants don't panic
            sim = self.simulate_move(generate_move(index, search_index, "_"))
            #only the tiles that the king is passing over matter for checks
            if sim.check_check(turn, played_moves, False):
                #return early if we can't castle to the right as left has been checked
                return output
            tile = self.board[search_index]
            if not tile == "_":
                #return early if we can't castle to the right as left has been checked
                return output
        #if we can castle right add it to the list of possible moves
        if right:
            output.append(generate_move(index,index + 2,"c"))
        return output

    def search_rook(self, index: int, piece: str, one_move: bool) -> list[str]:
        """searches for moves in a cross"""
        output: list[str] = []
        offset_list = [[1,0], [-1,0], [0,1], [0,-1]]
        for offset in offset_list:
            output += self.get_moves_in_row(index,offset[0],offset[1],piece,one_move)
        return output

    def search_bishop(self, index: int, piece: str, one_move: bool) -> list[str]:
        """searches for moves in an x"""
        output: list[str] = []
        offset_list = [[1,1], [-1,1], [-1,-1], [1,-1]]
        for offset in offset_list:
            output += self.get_moves_in_row(index,offset[0],offset[1],piece,one_move)
        return output

    def search_knight(self, index: int, piece: str, one_move: bool) -> list[str]:
        """searches for funky knight movement"""
        output: list[str] = []
        offset_list = [[1,2],[2,1],[-1,2],[-2,1],[-1,-2],[-2,-1],[1,-2],[2,-1]]
        for offset in offset_list:
            output += self.get_moves_in_row(index,offset[0],offset[1],piece,one_move)
        return output

    def search_pawn(self, index: int, piece: str)-> list[str]:
        """just look up pawn movement to understand this mess (this was written before the function was made :3)"""
        output = []
        color = same_color(piece, "A")
        #checks if the pawn is on the first rank
        first_move = index < 16 if color else index > 46
        #sets which way the pawn is going due to how pawns work (fuck pawns)[do not the pawns]
        direction = 1 if color else -1
        start_x = index_column(index)
        start_y = index_row(index)
        new_y = start_y + direction
        tile = self.board[coordinates_to_index(start_x,new_y)]
        #pawns movement and attacks are different, also promotion exists :(
        if tile == "_":
            if (start_y == 6 and color) or (start_y == 1 and not color):
                #promotion
                output.append(generate_move(index, coordinates_to_index(start_x,new_y), "Q" if color else "q"))
                output.append(generate_move(index, coordinates_to_index(start_x,new_y), "N" if color else "n"))
                output.append(generate_move(index, coordinates_to_index(start_x,new_y), "B" if color else "b"))
                output.append(generate_move(index, coordinates_to_index(start_x,new_y), "R" if color else "r"))
            else:
                output.append(generate_move(index, coordinates_to_index(start_x,new_y), "_"))
            #pawns can move twice on the first move
            if first_move:
                tile = self.board[coordinates_to_index(start_x,new_y + direction)]
                if tile == "_":
                    output.append(generate_move(index, coordinates_to_index(start_x,new_y + direction), "_"))
        new_y = start_y + direction
        for offset in range(-1,2,2):
            new_x = start_x + offset
            if -1 < new_x < 8:
                tile = self.board[coordinates_to_index(new_x, new_y)]
                if (not tile == "_") and (not same_color(piece, tile)):
                    if (start_y == 6 and color) or (start_y == 1 and not color):
                        #promotion
                        output.append(generate_move(index, coordinates_to_index(new_x,new_y), "Q" if color else "q"))
                        output.append(generate_move(index, coordinates_to_index(new_x,new_y), "N" if color else "n"))
                        output.append(generate_move(index, coordinates_to_index(new_x,new_y), "B" if color else "b"))
                        output.append(generate_move(index, coordinates_to_index(new_x,new_y), "R" if color else "r"))
                    else:
                        output.append(generate_move(index, coordinates_to_index(new_x,new_y), "_"))
        return output

    def search_en_passant(self, index: int, piece: str, played_moves: list[str])-> list[str]:
        """search this up for an explanation """
        output = []
        start_x = index_column(index)
        turn = same_color(piece, "A")
        #if we haven't played anything exit
        if len(played_moves) < 1:
            return output
        #checks if we are on the correct row
        if turn:
            if not index_row(index) == 4:
                return output
        else:
            if not index_row(index) == 3:
                return output
        #left en passant
        least_move = played_moves[len(played_moves) - 1]
        if start_x - 1 >= 0:
            search_index_encoded = movement_square_encoder(index - 1)
            if least_move[1] == search_index_encoded and (index_row(movement_square_decoder(least_move[0])) == 1 if not turn else index_row(movement_square_decoder(least_move[0])) == 6) and not same_color(piece, self.board[index - 1]) and self.board[index - 1].lower() == "p":
                output.append(generate_move(index, coordinates_to_index(start_x - 1, index_row(index) + (1 if turn else -1)), "E"))
        #right en passant
        if start_x + 1 < 8:
            search_index_encoded = movement_square_encoder(index + 1)
            if least_move[1] == search_index_encoded and (index_row(movement_square_decoder(least_move[0])) == 1 if not turn else index_row(movement_square_decoder(least_move[0])) == 6) and not same_color(piece, self.board[index + 1]) and self.board[index + 1].lower() == "p":
                output.append(generate_move(index, coordinates_to_index(start_x + 1, index_row(index) + (1 if turn else -1)), "e"))
        return output



    def get_moves(self, turn: bool, played_moves: list[str], checking_check: bool)-> list[str]:
        """gets all possible moves not accounting for checks"""
        output = []
        for index in range(0, 64):
            tile = self.board[index]
            #rook
            if (turn and tile == "R") or (not turn and tile == "r"):
                output += self.search_rook(index, tile, False)
            #bishop
            if (turn and tile == "B") or (not turn and tile == "b"):
                output += self.search_bishop(index, tile, False)
            #queen (queens combine rook and bishop movement)
            if (turn and tile == "Q") or (not turn and tile == "q"):
                output += self.search_rook(index, tile, False)
                output += self.search_bishop(index, tile, False)
            #knight
            if (turn and tile == "N") or (not turn and tile == "n"):
                output += self.search_knight(index, tile, True)
            #king (moves like a king but in one tile increments)
            if (turn and tile == "K") or (not turn and tile == "k"):
                output += self.search_rook(index, tile, True)
                output += self.search_bishop(index, tile, True)
                output += self.search_castle(index, tile, played_moves, checking_check)
            #pawn (look it up)
            if (turn and tile == "P") or (not turn and tile == "p"):
                output += self.search_pawn(index, tile)
                output += self.search_en_passant(index, tile, played_moves)
        return output

    def get_legal_moves(self, turn: bool, played_moves: list[str])-> list[str]:
        """gets all legal moves for the current board state"""
        moves = self.get_moves(turn, played_moves, False)
        new_moves = []
        for move in moves:
            sim = self.simulate_move(move)
            if not sim.check_check(turn, played_moves, False):
                new_moves.append(move)
        return new_moves