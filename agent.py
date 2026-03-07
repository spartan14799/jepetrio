import numpy as np
import time
import pyautogui
from dataclasses import dataclass, field
from typing import List


# INFO: Estructura usada para la comunicacion entre los niveles del arbol
# Usamos  slots=True para hacerla mas rapida que un diccionario
@dataclass(slots=True)
class Move:
    board: np.ndarray
    cleared_lines: int
    actions: List[str] = field(default_factory=list)
    score: float = float("-inf")

    def __lt__(self, other):
        return self.score < other.score


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

        self.well_column = 9
        self.rows = 20
        self.cols = 10

        self.piezas_mapeo = {
            "I": [
                [(0, 0), (0, 1), (0, 2), (0, 3)],
                [(0, 2), (1, 2), (2, 2), (3, 2)],
                [(0, 0), (0, 1), (0, 2), (0, 3)],
                [(0, 2), (1, 2), (2, 2), (3, 2)],
            ],
            "J": [
                [(0, 0), (1, 0), (1, 1), (1, 2)],
                [(0, 1), (0, 2), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (1, 2), (2, 2)],
                [(0, 1), (1, 1), (2, 0), (2, 1)],
            ],
            "L": [
                [(0, 2), (1, 0), (1, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (2, 2)],
                [(1, 0), (1, 1), (1, 2), (2, 0)],
                [(0, 0), (0, 1), (1, 1), (2, 1)],
            ],
            "O": [
                [(0, 0), (0, 1), (1, 0), (1, 1)]  # El cubo no cambia al rotar
            ],
            "S": [[(0, 1), (0, 2), (1, 0), (1, 1)], [(0, 1), (1, 1), (1, 2), (2, 2)]],
            "T": [
                [(0, 1), (1, 0), (1, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (1, 2)],
                [(1, 0), (1, 1), (1, 2), (2, 1)],
                [(0, 1), (1, 1), (2, 1), (1, 0)],
            ],
            "Z": [[(0, 0), (0, 1), (1, 1), (1, 2)], [(0, 2), (1, 1), (1, 2), (2, 1)]],
        }

    def percept(self, queue_outputs):
        pass

    def compute(self, queue_inputs, queue_outputs):
        pass

    def action(self, queue_outputs):
        keys = {
            "left": "left",
            "right": "right",
            "soft_drop": "down",
            "hard_drop": "space",
            "rotate_countercw": "z",
            "rotate_cw": "up",
            "hold": "c",
            "rotate_180": "a",
        }

        while True:
            comand = queue_outputs.get()

            if comand == "^":
                break

            if comand in keys:
                key = keys[comand]

                pyautogui.keyDown(key)
                time.sleep(0.02)
                pyautogui.keyUp(key)

            else:
                print(f"Movimiento no reconocido: {comand}")

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

    # INFO: Metodos para alcanzar el mejor movimiento.

    def get_best_move(self, incoming_queue, current_board, max_depth=3):
        best_score = float("-inf")
        best_move = None

        if not incoming_queue:
            return None

        current_piece = incoming_queue[0]
        possible_moves = self._generate_all_moves(current_board, current_piece)

        for move in possible_moves:
            score = self._dfs_search(
                board=move.board,
                incoming_queue=incoming_queue[1:],
                depth=max_depth - 1,
                # TODO: Arregalar el tetris fantasma, si limpia 4 lineas en diferentes niveles, cotara como tetris cuando no lo es.
                accumulated_lines=move.cleared_lines,
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _dfs_search(self, board, incoming_queue, depth, accumulated_lines) -> float:
        if depth == 0 or not incoming_queue:
            return self.evaluate_move(board, accumulated_lines)

        current_piece = incoming_queue[0]
        possible_moves = self._generate_all_moves(board, current_piece)

        if not possible_moves:
            return float("-inf")

        best_score_in_branch = float("-inf")

        for move in possible_moves:
            total_lines = accumulated_lines + move.cleared_lines

            score = self._dfs_search(
                board=move.board,
                incoming_queue=incoming_queue[1:],
                depth=depth - 1,
                accumulated_lines=total_lines,
            )

            if score > best_score_in_branch:
                best_score_in_branch = score

        return best_score_in_branch

    # TODO: Crear la funcion
    def _generate_all_moves(self, board, piece_name) -> list[Move]:
        """
        Funcion que pide una pieza y el tablero y devolver una lista de Move
        """
        return []
