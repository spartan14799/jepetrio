import unittest
import numpy as np
from agent import Agent, Move

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()
        # Mocking queue stuff to prevent multiprocessing issues during tests
        self.agent.queue_perceptions = None
        self.agent.queue_actions = None

    def test_clear_lines_none(self):
        board = np.zeros((20, 10), dtype=int)
        board[19, :] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0] # almost full
        
        new_board, cleared = self.agent._clear_lines(board)
        self.assertEqual(cleared, 0)
        self.assertTrue(np.array_equal(new_board, board))

    def test_clear_lines_one(self):
        board = np.zeros((20, 10), dtype=int)
        board[19, :] = 1 # full line
        board[18, 0] = 1 # some block above
        
        new_board, cleared = self.agent._clear_lines(board)
        self.assertEqual(cleared, 1)
        self.assertEqual(new_board[19, 0], 1)
        self.assertEqual(np.sum(new_board[19, :]), 1) # Only the block from line 18 should be here

    def test_clear_lines_multiple(self):
        board = np.zeros((20, 10), dtype=int)
        board[18, :] = 1
        board[19, :] = 1
        board[17, 5] = 1
        
        new_board, cleared = self.agent._clear_lines(board)
        self.assertEqual(cleared, 2)
        self.assertEqual(new_board[19, 5], 1)
        self.assertEqual(np.sum(new_board), 1)

    def test_count_holes(self):
        board = np.zeros((20, 10), dtype=int)
        board[18, 5] = 1
        board[19, 5] = 0 # this is a hole
        self.assertEqual(self.agent._count_holes(board), 1)

        board[17, 5] = 1 # block above block, still 1 hole
        self.assertEqual(self.agent._count_holes(board), 1)
        
        board[19, 6] = 0
        board[18, 6] = 1 # another hole
        self.assertEqual(self.agent._count_holes(board), 2)

    def test_calculate_bumpiness(self):
        board = np.zeros((20, 10), dtype=int)
        # All columns 0 height: bumpiness 0
        self.assertEqual(self.agent._calculate_bumpiness(board), 0)
        
        board[19, 0] = 1 # col 0 height 1
        # heights: 1, 0, 0, ... bumpiness: |1-0| + 0 + ... = 1
        self.assertEqual(self.agent._calculate_bumpiness(board), 1)

        board[18, 1] = 1
        board[19, 1] = 1 # col 1 height 2
        # heights: 1, 2, 0, 0, ... bumpiness: |1-2| + |2-0| + 0 = 1 + 2 = 3
        self.assertEqual(self.agent._calculate_bumpiness(board), 3)

    def test_check_collision(self):
        board = np.zeros((20, 10), dtype=int)
        
        # Test out of bounds (left)
        self.assertTrue(self.agent._check_collision(board, np.array([0]), np.array([0]), -1, 10))
        # Test out of bounds (right)
        self.assertTrue(self.agent._check_collision(board, np.array([0]), np.array([0]), 10, 10))
        # Test out of bounds (bottom)
        self.assertTrue(self.agent._check_collision(board, np.array([0]), np.array([0]), 5, 20))
        
        # Test collision with block
        board[19, 5] = 1
        self.assertTrue(self.agent._check_collision(board, np.array([0]), np.array([0]), 5, 19))
        self.assertFalse(self.agent._check_collision(board, np.array([0]), np.array([0]), 5, 18))

    def test_get_drop_position(self):
        board = np.zeros((20, 10), dtype=int)
        # Drop a 1x1 block at col 5
        drop_pos = self.agent._get_drop_position(board, np.array([0]), np.array([0]), 5)
        self.assertEqual(drop_pos, 19)

        board[19, 5] = 1
        drop_pos = self.agent._get_drop_position(board, np.array([0]), np.array([0]), 5)
        self.assertEqual(drop_pos, 18)

    def test_generate_all_moves(self):
        board = np.zeros((20, 10), dtype=int)
        moves = self.agent._generate_all_moves(board, "O")
        # O piece is 2x2. Columns from -3 to 10? Actually let's just see if it generates moves without crashing
        self.assertTrue(len(moves) > 0)
        for move in moves:
            self.assertEqual(type(move), Move)
            self.assertEqual(move.board.shape, (20, 10))

    def test_evaluate_move(self):
        board = np.zeros((20, 10), dtype=int)
        score = self.agent.evaluate_move(board, 0, "")
        self.assertEqual(score, 0)
        
        score_tetris = self.agent.evaluate_move(board, 4, "")
        self.assertTrue(score_tetris > 1000)

if __name__ == '__main__':
    unittest.main()
