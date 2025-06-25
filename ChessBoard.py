class ChessBoard:
    def __init__(self):
        #note that this is flipped due to how arrays work
        self.board: list = [["♜","♞","♝","♛","♚","♝","♞","♜"],
                      ["♟","♟","♟","♟","♟","♟","♟","♟"],
                      ["","","","","","","",""],
                      ["","","","","","","",""],
                      ["","","","","","","",""],
                      ["","","","","","","",""],
                      ["♙","♙","♙","♙","♙","♙","♙","♙"],
                      ["♖","♘","♗","♕","♔","♗","♘","♖"]]
        #used to prevent infinite loops
        self.simmed_move = False

    def to_text(self):
        """
        | converts board matrix into a string of text.
        | the numbers indicate spaces between pieces
        | Format:
        | "row1|row2|row3|row4|row5|row6|row7|row8|"
        """
        output = ""
        for row in self.board:
            space_count = 0
            for tile in row:
                if tile == "":
                    space_count += 1
                else:
                    if space_count != 0:
                        output += str(space_count)
                        space_count = 0
                    output += tile
            if space_count != 0:
                output += str(space_count)
            output += "|"
        return output

    def from_text(self, text: str):
        """
        | opposite of to_text function
        """
        self.board = [[]]
        row = 0
        for character in text:
            try:
                for i in range(0, int(character)):
                    self.board[row].append("")
            except ValueError:
                if character == "|":
                    row += 1
                    self.board.append([])
                else:
                    self.board[row].append(character)
        self.board.pop(len(self.board) - 1)

    def display_board(self):
        print("---------------------")
        for row in range(0, len(self.board)):
            row_out = ""
            for tile in self.board[7-row]:
                row_out += "|"
                if tile == "":
                    row_out += " "
                else:
                    row_out += tile
            row_out += "|"
            print(row_out)
            print("---------------------")

    @staticmethod
    def same_color(piece1, piece2) -> bool:
        """
        checks if two pieces are the same color
        """
        #uses char numbers ♔ = 9812 ♕ = 9813 ♖ = 9814 ♗ = 9815 ♘ = 9816 ♙ = 9817 || ♚ = 9818 ♛ = 9819 ♜ = 9820 ♝ = 9821 ♞ = 9822 ♟ = 9823
        return ((ord(piece1) < 9818 and ord(piece2) < 9818) or
                (ord(piece1) > 9817 and ord(piece2) > 9817))

    def check_check(self, turn, played_moves) -> bool:
        """checks board to see if any enemy pieces can capture a king"""
        moves = self.get_moves(not turn, played_moves)
        for move in moves:
            if move[len(move) - 1] == "♚" or move[len(move) - 1] == "♔":
                return True
        return False

    @staticmethod
    def gen_move_str(x_start: int, y_start: int, x_end: int, y_end: int, piece: str):
        return piece + str(x_start) + str(y_start) + str(x_end) + str(y_end)

    def check_line(self, x_start: int, y_start: int, x_offset: int, y_offset: int, piece: str):
        """
        generates all moves a piece can make along a given line (including attacks)
        :param x_start: x position to start from
        :param y_start: y position to start from
        :param x_offset: how far int the x to jump per iteration
        :param y_offset: how far int the y to jump per iteration
        :param piece: piece that is using this
        :return: moves that the piece can make
        """
        output = []
        for i in range(1, 8):
            x = x_start + x_offset * i
            y = y_start + y_offset * i
            if y < 0 or x < 0:
                return output
            try:
                tile = self.board[y][x]
                if tile == "":
                    output.append(self.gen_move_str(x_start, y_start, x, y, piece))
                else:
                    if not self.same_color(tile, piece):
                        output.append(self.gen_move_str(x_start, y_start, x, y, piece) + tile)
                    return output
            except IndexError:
                return output
        return output

    #made so that I can clean up the get_moves function
    def get_piece_moves(self, x: int, y: int, piece: str, turn: bool, played_moves: list[str]):
        """
        gets all the possible moves regardless of check/ checkmate
        """
        output = []
        #rook
        if (piece == "♜" and turn) or (piece == "♖" and not turn):
            output += self.search_rook(x, y, piece)
        #bishop
        if (piece == "♝" and turn) or (piece == "♗" and not turn):
            output += self.search_bishop(x, y, piece)
        #queen
        if (piece == "♛" and turn) or (piece == "♕" and not turn):
            output += self.search_queen(x, y, piece)
        #king
        if (piece == "♚" and turn) or (piece == "♔" and not turn):
            output += self.search_king(x, y, piece, played_moves)
        #pawn
        if (piece == "♟" and turn) or (piece == "♙" and not turn):
            output += self.search_pawn(x, y, piece, played_moves)
        #knight
        if (piece == "♞" and turn) or (piece == "♘" and not turn):
            output += self.search_knight(x, y, piece)
        return output

    def search_rook(self, x: int, y: int, piece: str):
        """finds moves in an + shape"""
        output = []
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if abs(x_offset) != abs(y_offset):
                    output += self.check_line(x, y, x_offset, y_offset, piece)
        return output

    def search_bishop(self, x: int, y: int, piece: str):
        """finds moves in an x shape"""
        output = []
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if abs(x_offset) == abs(y_offset):
                    output += self.check_line(x, y, x_offset, y_offset, piece)
        return output

    def search_queen(self, x: int, y: int, piece: str):
        """finds moves in an * shape"""
        output = []
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                output += self.check_line(x, y, x_offset, y_offset, piece)
        return output

    def search_castle(self, turn: bool, piece: str, played_moves: list[str]):
        """searches for if castling can be done"""
        output = []
        if self.simmed_move:
            return output
        for move in played_moves:
            if piece in move:
                return output
        if self.same_color(piece, "♟"):
            if self.board[0][4] != "♚":
                return output
        else:
            if self.board[7][4] != "♔":
                return output
        #used for checking if right rook or left rook have moved
        left = True
        right = True
        if self.same_color(piece, "♟"):
            if self.board[0][0] != "♜":
                left = False
            if self.board[0][7] != "♜":
                right = False
        else:
            if self.board[7][0] != "♖":
                left = False
            if self.board[7][7] != "♖":
                right = False
        if left:
            if self.same_color(piece, "♟"):
                if self.board[0][0] == "♜" and self.board[0][1] == "" and self.board[0][2] == "" and self.board[0][3] == "" and not self.simulate_move("♚4030").check_check(turn, played_moves) and not self.simulate_move("♚4020").check_check(turn, played_moves):
                    output.append("♚o-o-o")
            else:
                if self.board[7][0] == "♖" and self.board[7][1] == "" and self.board[7][2] == "" and self.board[7][3] == "" and not self.simulate_move("♔4737").check_check(turn, played_moves) and not self.simulate_move("♔4727").check_check(turn, played_moves):
                    output.append("♔o-o-o")
        if right:
            if self.same_color(piece, "♟"):
                if self.board[0][7] == "♜" and self.board[0][5] == "" and self.board[0][6] == "" and not self.simulate_move("♚4050").check_check(turn, played_moves) and not self.simulate_move("♚4060").check_check(turn, played_moves):
                    output.append("♚o-o")
            else:
                if self.board[7][7] == "♖" and self.board[7][5] == "" and self.board[7][6] == "" and not self.simulate_move("♔4757").check_check(turn, played_moves) and not self.simulate_move("♔4767").check_check(turn, played_moves):
                    output.append("♔o-o")
        return output


    def search_king(self, x:int, y:int, piece: str, played_moves: list[str]):
        """finds all moves within one tile"""
        output = []
        output += self.search_castle(self.same_color(piece, "♟"), piece, played_moves)
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if (0 <= x + x_offset <= 7) and (0 <= y + y_offset <= 7):
                    tile = self.board[y + y_offset][x + x_offset]
                    if tile == "":
                        output.append(self.gen_move_str(x, y, x + x_offset, y + y_offset, piece))
                    else:
                        if not self.same_color(tile, piece):
                            output.append(self.gen_move_str(x, y, x + x_offset, y + y_offset, piece) + tile)
        return output

    def search_enpassant(self, x:int, y:int, piece: str, played_moves: list[str]):
        """searches for one of the chess moves of all time"""
        output = []
        if self.simmed_move or len(played_moves) == 0:
            return output
        if piece == "♟":
            if y == 4:
                if played_moves[len(played_moves) - 1][0] == "♙" and played_moves[len(played_moves) - 1][4] == "4" and played_moves[len(played_moves) - 1][2] == "6":
                    if played_moves[len(played_moves) - 1][3] == str(x - 1):
                        output.append(self.gen_move_str(x, y, x - 1, y + 1, piece) + "p")
                    if played_moves[len(played_moves) - 1][3] == str(x + 1):
                        output.append(self.gen_move_str(x, y, x + 1, y + 1, piece) + "p")
        else:
            if y == 3:
                if played_moves[len(played_moves) - 1][0] == "♟" and played_moves[len(played_moves) - 1][4] == "3" and played_moves[len(played_moves) - 1][2] == "1":
                    if played_moves[len(played_moves) - 1][3] == str(x - 1):
                        output.append(self.gen_move_str(x, y, x - 1, y - 1, piece) + "p")
                    if played_moves[len(played_moves) - 1][3] == str(x + 1):
                        output.append(self.gen_move_str(x, y, x + 1, y - 1, piece) + "p")

        return output

    def search_pawn(self, x:int, y:int, piece: str, played_moves: list[str]):
        """finds pawn movement (search it up)"""
        output = []
        output += self.search_enpassant(x, y, piece, played_moves)
        #tells the pawn which way to go
        direction = 1 if piece == "♟" else -1
        new_y = y + direction
        #split these into categories as pawns are the only pieces to have separate movement and attacking
        #movement and promotion
        if self.board[new_y][x] == "":
            if new_y == 0 or new_y == 7:
                        if self.same_color("♜", piece):
                            output.append(self.gen_move_str(x, y, x, new_y, "♛"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♜"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♞"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♝"))
                        else:
                            output.append(self.gen_move_str(x, y, x, new_y, "♕"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♖"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♘"))
                            output.append(self.gen_move_str(x, y, x, new_y, "♗"))
            else:
                output.append(self.gen_move_str(x, y, x, new_y, piece))
                if piece == "♟":
                    if y == 1:
                        if self.board[new_y + direction][x] == "": output.append(self.gen_move_str(x, y, x, new_y + direction, piece))
                else:
                    if y == 6:
                        if self.board[new_y + direction][x] == "": output.append(self.gen_move_str(x, y, x, new_y + direction, piece))
        #attacks
        for x_offset in range(-1,2,2):
            attack_x = x + x_offset
            if 0 <= attack_x <= 7:
                attacked_tile = self.board[new_y][attack_x]
                if attacked_tile != "" and not self.same_color(piece, attacked_tile):
                    if new_y == 0 or new_y == 7:
                        if self.same_color("♜", piece):
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♛") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♜") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♞") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♝") + attacked_tile)
                        else:
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♕") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♖") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♘") + attacked_tile)
                            output.append(self.gen_move_str(x, y, attack_x, new_y, "♗") + attacked_tile)

                    else:
                        output.append(self.gen_move_str(x, y, attack_x, new_y, piece) + attacked_tile)
        return output

    def search_knight(self, x: int, y: int, piece: str):
        """finds moves for knights (L shape)"""
        output = []
        offset_list = [[1,2],[2,1],[2,-1],[1,-2],[-1,-2],[-2,-1],[-2,1],[-1,2]]
        for offset in offset_list:
            new_x = x + offset[0]
            new_y = y + offset[1]
            if (0 <= new_x <= 7) and (0 <= new_y <= 7):
                tile = self.board[new_y][new_x]
                if tile == "":
                    output.append(self.gen_move_str(x, y, new_x, new_y, piece))
                elif not self.same_color(piece, tile):
                    output.append(self.gen_move_str(x, y, new_x, new_y, piece) + tile)
        return output

    def copy(self):
        """creates a copy of the board"""
        new_board = ChessBoard()
        new_board.from_text(self.to_text())
        return new_board

    #plays a move on the board
    def play_move(self, move: str):
        """plays a move on the board regardless of legality"""
        if "p" in move:
            x = int(move[1])
            y = int(move[2])
            x1 = int(move[3])
            y1 = int(move[4])
            self.board[y][x] = ""
            self.board[y][x1] = ""
            self.board[y1][x1] = move[0]
            return
        if "o" in move:
            if "o-o-o" in move:
                if self.same_color(move[0], "♝"):
                    self.board[0][4] = ""
                    self.board[0][2] = "♚"
                    self.board[0][0] = ""
                    self.board[0][3] = "♜"
                else:
                    self.board[7][4] = ""
                    self.board[7][2] = "♔"
                    self.board[7][0] = ""
                    self.board[7][3] = "♖"
            elif "o-o" in move:
                if self.same_color(move[0], "♝"):
                    self.board[0][4] = ""
                    self.board[0][6] = "♚"
                    self.board[0][7] = ""
                    self.board[0][5] = "♜"
                else:
                    self.board[7][4] = ""
                    self.board[7][6] = "♔"
                    self.board[7][7] = ""
                    self.board[7][5] = "♖"
            return
        piece = move[0]
        start_x = int(move[1])
        start_y = int(move[2])
        end_x = int(move[3])
        end_y = int(move[4])
        self.board[start_y][start_x] = ""
        self.board[end_y][end_x] = piece

    #creates a new board with the played move
    def simulate_move(self, move:str):
        """creates a copy of the current board then plays the move"""
        test_board = self.copy()
        test_board.play_move(move)
        test_board.simmed_move = True
        return test_board

    #gets all possible moves
    def get_moves(self, turn: bool, played_moves: list[str]):
        """gets all the moves that can happen regardless of checks"""
        output = []
        for row in range(0, len(self.board)):
            for column in range(0, len(self.board[row])):
                if self.board[row][column] != "":
                    output += self.get_piece_moves(column, row, self.board[row][column], turn, played_moves)
        return output

    #filters for legal moves, preferably used when check to reduce the amount of simulate move calls
    def legal_move_filter(self, moves: list, turn, played_moves: list[str]):
        """filters the moves to see which can block check"""
        new_moves = []
        for move in moves:
            if not self.simulate_move(move).check_check(turn, played_moves):
                new_moves.append(move)
        return new_moves

    def get_legal_moves(self, turn, played_moves: list[str]):
        """gets all legal moves"""
        moves = self.get_moves(turn, played_moves)
        #we have to run this on all moves to protect from pins fucking everything up
        moves = self.legal_move_filter(moves, turn, played_moves)
        return moves

    def check_stalemate(self, turn, played_moves: list[str]):
        return len(self.get_legal_moves(turn, played_moves)) == 0

    def check_checkmate(self, turn, played_moves: list[str]):
        return len(self.get_legal_moves(turn, played_moves)) == 0 and self.check_check(turn, played_moves)