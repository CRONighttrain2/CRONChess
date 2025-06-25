import time
from random import Random
import ChessBoard


def ord_sort(moves):
    """used to sort by order"""
    return ord(moves[0])

class Game:
    def __init__(self):
        self.board = ChessBoard.ChessBoard()
        self.turn = True
        self.moves: list[str] = []
        #to see if 50 move rule has happened
        self.move_rule_counter = 0
        #for threefold rep
        self.positions_count = dict()
        self.player1 = None
        self.player2 = None

    @staticmethod
    def get_player():
        choice = input("choose player: [current selection: RandomBot, PlayerBot, FirstBot,LastBot]: ")
        if choice.lower().strip() == "randombot":
            return RandomBot()
        if choice.lower().strip() == "playerbot":
            return PlayerBot()
        if choice.lower().strip() == "firstbot":
            return FirstBot()
        if choice.lower().strip() == "lastbot":
            return LastBot()
        return None

    def setup_game(self):
        board = input("input board leave blank for regular: ")
        self.board.from_text(board)
        turn = input("input turn [t for white, f for black]: ")
        self.turn = turn == "t" or turn == ""
        self.player1 = self.get_player()
        self.player2 = self.get_player()
        return True

    def play_game(self):
        print(self.game_end())
        print(self.board.display_board())
        print(self.move_rule_counter >= 50)
        print(self.threefold_rep_check())
        while not self.game_end():
            if self.turn:
                self.play_move(self.player1.play_move(self))
            else:
                self.play_move(self.player2.play_move(self))
            self.board.display_board()
            print(len(self.moves))
            print(self.turn)
            print("--------------------------------------------------------------------")
            time.sleep(4)

    def game_end(self):
        """checks if the game has ended in any way"""
        #     |  checks for check mate                            |checks if there are no legal moves to play and no mate| 50 move rule             | threefold repetition rule
        return self.board.check_checkmate(self.turn, self.moves) or self.board.check_stalemate(self.turn, self.moves) or self.move_rule_counter >= 50 or self.threefold_rep_check() or (len(self.moves) > 2 and self.moves[len(self.moves) - 1] == self.moves[len(self.moves) - 2])

    def threefold_rep_check(self):
        """checks if a position has repeated 3 times"""
        for key in self.positions_count.keys():
            if self.positions_count[key] > 2:
                return True
        return False

    def play_move(self, move):
        """
        :param move: move to try to play
        :return: if the move was played successfully
        """
        if move in self.board.get_legal_moves(self.turn, self.moves):
            #plays the move
            self.board.play_move(move)
            #checks for threefold repetition
            pos_as_text = self.board.to_text()
            if pos_as_text not in self.positions_count.keys():
                self.positions_count[pos_as_text] = 0
            self.positions_count[pos_as_text] = self.positions_count[pos_as_text] + 1
            #sets it so the other player plays
            self.turn = not self.turn
            #adds the move to the move list
            self.moves.append(move)
            self.move_rule_counter += 1
            #resets 50 move rule checker if there is a capture
            if "o" not in move and len(move) == 6:
                self.move_rule_counter = 0
            return True
        return False

    def from_moves(self, moves_str: str):
        """generate a game from a string of moves"""
        moves = moves_str.split(",")
        for move in moves:
            self.play_move(move)

    def __copy__(self):
        g = Game()
        g.from_moves(self.get_played_moves())
        return g

    def simulate_move(self, move):
        """returns a copy of the current game with"""
        sim = self.__copy__()
        sim.play_move(move)
        return sim

    def get_played_moves(self):
        """
        | returns the move array as a string with the format:
        | "move1,move2,move3"
        """
        if len(self.moves) == 0: return ""
        output = ""
        for move in self.moves:
            output += move + ","
        return output[:len(output)-1]

    def playable_move_sorter(self, moves: list):
        """sorts the playable moves to be in a 'better' order"""
        moves = sorted(moves, key= ord_sort)
        moves = sorted(moves, key=len)
        moves.reverse()
        return moves

    def get_playable_moves(self):
        """gets the moves that can be played on this turn"""
        return self.playable_move_sorter(self.board.get_legal_moves(self.turn, self.moves))

# ====================== the bots =============================== (cause I tried to make my own class and it looped imports)[gonna fix later] <- never gonna happen :3
class RandomBot:
    def __init__(self):
        """plays a random move"""
        self.rand = Random()
        self.search_depth = 0

    def play_move(self, game:Game, depth: int):
        moves = game.get_playable_moves()
        return moves[self.rand.randint(0, len(moves) - 1)]

class PlayerBot:
    def __init__(self):
        self.search_depth = 0

    def play_move(self, game:Game, depth: int):
        moves = game.get_playable_moves()
        print(moves)
        move = ""
        while move not in moves:
            move = input("choose a move to play: ")
        return move

class FirstBot:
    def __init__(self):
        self.search_depth = 0

    def play_move(self, game:Game, depth: int):
        return game.get_playable_moves()[0]

class LastBot:
    def __init__(self):
        self.search_depth = 0

    def play_move(self, game:Game, depth: int):
        moves = game.get_playable_moves()
        return moves[len(moves) - 1]

#requested by a friend
class LongDickBot:
    def evaluate(self, board: ChessBoard.ChessBoard):
        checker_board = board.board.copy()
        checker_board = [["_" if len(piece) == 0 else ("w" if board.same_color(piece, "♟") else "b") for piece in  row] for row in checker_board]
        score = 0
        #white score:
        for row_index in range(0, len(checker_board)):
            last_chars = ""
            for column_index in range(0, len(checker_board[0])):
                if len(last_chars) < 3:
                    last_chars += checker_board[row_index][column_index]
                else:
                    last_chars = last_chars[1:] + checker_board[row_index][column_index]
                    if last_chars == "w_w":
                        score += 1
                        for length_check in range(row_index + 1, 8 - row_index):
                            if checker_board[length_check][column_index - 1] == "w":
                                score += 5
                            else:
                                break
        #black score:
        for row_index in range(len(checker_board) - 1, -1, -1):
            last_chars = ""
            for column_index in range(len(checker_board[0]) - 1, -1, -1):
                if len(last_chars) < 3:
                    last_chars += checker_board[row_index][column_index]
                else:
                    last_chars = last_chars[1:] + checker_board[row_index][column_index]
                    if last_chars == "b_b":
                        score -= 1
                        for length_check in range(7 - row_index, row_index, -1):
                            if checker_board[length_check][column_index - 1] == "b":
                                score -= 5
                            else:
                                break
        return score

    def play_move(self, game:Game, depth: int):
        head = TreeNode("",game)
        head.generate_children_alpha_beta(self,depth, -99999, 99999)
        return head.suggested_move()

#requested by a friend
class ShortDickBot:
    def evaluate(self, board: ChessBoard.ChessBoard):
        checker_board = board.board.copy()
        checker_board = [["_" if len(piece) == 0 else ("w" if board.same_color(piece, "♟") else "b") for piece in  row] for row in checker_board]
        score = 0
        #white evaluation:
        for row_index in range(0, len(checker_board) - 2):
            for column_index in range(0, len(checker_board[0]) - 2):
                dick_detection_white = checker_board[row_index][column_index] + checker_board[row_index][column_index + 1] + checker_board[row_index][column_index + 2] + checker_board[row_index + 1][column_index + 1] + checker_board[row_index + 2][column_index + 1]
                dick_detection_black = checker_board[row_index][column_index + 1] + checker_board[row_index + 1][column_index + 1] + checker_board[row_index + 2][column_index] + checker_board[row_index + 2][column_index + 1] + checker_board[row_index + 2][column_index + 2]
                if dick_detection_white == "w_www":
                    score += 3
                if dick_detection_black == "bbb_b":
                    score -= 3
        return score

    def play_move(self, game:Game, depth: int):
        head = TreeNode("",game)
        head.generate_children_alpha_beta(self,depth, -99999, 99999)
        return head.suggested_move()

class AttackBot:
    def evaluate(self, board: ChessBoard.ChessBoard):
        score: float = 0
        for row_index in range(0, len(board.board)):
            for tile in board.board[row_index]:
                # rook
                if tile == "♜" or tile == "♖":
                    score += 5 * (1 if tile == "♜" else -1) + round((float(row_index)/7 if tile == "♜" else (float(row_index)-7)/7),3)
                # bishop
                if tile == "♝" or tile == "♗":
                    score += 3.5 * (1 if tile == "♝" else -1) + round((float(row_index)/7 if tile == "♝" else (float(row_index)-7)/7),3)
                # queen
                if tile == "♛" or tile == "♕":
                    score += 8 * (1 if tile == "♛" else -1)
                # king
                if tile == "♚" or tile == "♔":
                    score += 100 * (1 if tile == "♚" else -1)
                # pawn
                if tile == "♟" or tile == "♙":
                    score += 1 * (1 if tile == "♟" else -1) + 2 * (round((float(row_index)/7 if tile == "♟" else (float(row_index)-7)/7),3))
                # knight
                if tile == "♞" or tile == "♘":
                    score += 3 * (1 if tile == "♞" else -1) + round((float(row_index)/7 if tile == "♞" else (float(row_index)-7)/7),3)
        return round(score, 3)

    def play_move(self, game:Game, depth: int):
        head = TreeNode("",game)
        print("score = " + str(head.generate_children_alpha_beta(self,depth, -99999, 99999)))
        return head.suggested_move()



class TreeNode:
    def __init__(self, move, game: Game):
        """Creates a new tree which holds the data for a board"""
        self.game = game
        # made so I can see the legal moves for each board for debugging
        self.moves = []
        # the move made on this board, made for debugging
        self.move = move
        self.children: list[TreeNode] = []
        # used so the bots can calculate the best moves
        self.score: float = None

    def suggested_move(self):
        """get a random move out of all of the best moves"""
        r = Random()
        suggested_moves = []
        for node in self.children:
            if node.score == self.score:
                suggested_moves.append(node.move)
        return suggested_moves[r.randint(0, len(suggested_moves) -1)]

    def generate_children_alpha_beta(self, bot, depth, alpha, beta):
        """create a tree using alpha beta"""
        if depth == 0 or self.game.game_end():
            self.score = bot.evaluate(self.game.board)
            return self.score
        legal_moves = self.game.get_playable_moves()
        if self.game.turn:
            self.score = -99999
            for move in legal_moves:
                new_game: Game = self.game.simulate_move(move)
                new_node = TreeNode(move, new_game)
                self.score = max(new_node.generate_children_alpha_beta(bot, depth - 1, alpha, beta), self.score)
                alpha = max(alpha, self.score)
                if beta <= alpha:
                    break
                self.children.append(new_node)
            return self.score
        else:
            self.score = 99999
            for move in legal_moves:
                new_game: Game = self.game.simulate_move(move)
                new_node = TreeNode(move, new_game)
                self.score = min(new_node.generate_children_alpha_beta(bot, depth - 1, alpha, beta), self.score)
                beta = min(beta, self.score)
                if beta <= alpha:
                    break
                self.children.append(new_node)
            return self.score

    def display_below(self, depth):
        """prints the moves that can occur for this node and all nodes below it"""
        self.display(depth)
        if len(self.children) > 0:
            for node in self.children:
                node.display_below(depth + 1)

    def display(self, depth):
        """prints the moves that can occur on this node"""
        print("\t" * depth + self.move + "->" + str(
            ["[" + node.move + "," + str(node.score) + "]" for node in self.children]) + " score: " + str(self.score))
