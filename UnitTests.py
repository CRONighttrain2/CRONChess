import unittest
import ChessboardV2


class BoardTests(unittest.TestCase):
    """tests the functions in the ChessboardV2 class"""
    def test_init(self):
        b = ChessboardV2.Board()
        self.assertEqual(b.board, "RNBQKBNRPPPPPPPP________________________________pppppppprnbqkbnr")
        self.assertEqual(len(b.board), 64)

    def test_move_encode(self):
        self.assertEqual(ChessboardV2.movement_square_encoder(4), "e")
        with self.assertRaises(Exception) as cm:
            ChessboardV2.movement_square_encoder(65)
            self.assertEqual(type(cm.exception), IndexError)
        with self.assertRaises(Exception) as cm:
            ChessboardV2.movement_square_encoder(-24)
            self.assertEqual(type(cm.exception), IndexError)

    def test_move_decode(self):
        self.assertEqual(ChessboardV2.movement_square_decoder("a"), 0)
        self.assertEqual(ChessboardV2.movement_square_decoder("5"), 57)
        with self.assertRaises(Exception) as cm:
            ChessboardV2.movement_square_decoder("&")
            self.assertEqual(type(cm.exception), ValueError)

    def test_pawn_move_generation(self):
        b = ChessboardV2.Board()
        b.board = "_K________P____________________________________________________k"
        moves = b.get_legal_moves(True, [])
        moves_check = ["kA_","ks_", "ba_", "bc_", "bi_", "bj_"]
        for move in moves_check:
            self.assertTrue(move in moves)

    def test_same_color(self):
        """tests the same color function"""
        self.assertTrue(ChessboardV2.same_color("A","A"))
        self.assertFalse(ChessboardV2.same_color("A","a"))
        self.assertFalse(ChessboardV2.same_color("a","A"))
        self.assertTrue(ChessboardV2.same_color("a","a"))

if __name__ == '__main__':
    unittest.main()
