import numpy as np


class Agent:
    def __init__(self, weights=None):
        self.weights = (
            weights
            if weights
            else {
                "holes": -10.0,
                "bumpiness": -2.0,
                "block_in_well": -8.0,
                "incomplete_clear": -5.0,
                "tetris": 15.0,
            }
        )
        # INFO: Se puede cambiar el poso y probar cual es el mejor
        self.well_column = 9
        self.rows = 20
        self.cols = 10

    def evaluate_move(self, board, cleared_lines):
        holes = self._count_holes(board)
        bumpiness = self._calculate_bumpiness(board)
        blocks_in_well = self._count_blocks_in_well(board)

        is_tetris = 1 if cleared_lines >= 4 else 0
        incomplete_clear = cleared_lines if 0 < cleared_lines < 4 else 0

        score = (
            (self.weights["holes"] * holes)
            + (self.weights["bumpiness"] * bumpiness)
            + (self.weights["block_in_well"] * blocks_in_well)
            + (self.weights["incomplete_clear"] * incomplete_clear)
            + (self.weights["tetris"] * is_tetris)
        )

        return score

    # INFO: Funciones para calcular la combinacion lineal:

    def _count_holes(self, board):
        accumulated_blocks = np.maximum.accumulate(board, axis=0)
        holes = (board == 0) & (accumulated_blocks == 1)
        return np.sum(holes)

    def _calculate_bumpiness(self, board):
        col_has_blocks = board.any(axis=0)
        heights = np.zeros(self.cols, dtype=int)
        heights[col_has_blocks] = self.rows - board.argmax(axis=0)[col_has_blocks]
        bumpiness = np.sum(np.abs(np.diff(heights)))
        return bumpiness

    def _count_blocks_in_well(self, board):
        return np.sum(board[:, self.well_column])
