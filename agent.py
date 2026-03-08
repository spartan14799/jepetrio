import multiprocessing
from typing import Sequence, List
from dataclasses import dataclass, field
import pyautogui
import time
import numpy as np


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
    COORDINATES = np.array(
        [
            [
                (208, 1317),
                (208, 1318),
                (208, 1319),
                (208, 1320),
                (208, 1321),
                (208, 1322),
            ],
            [
                (335, 1317),
                (335, 1318),
                (335, 1319),
                (335, 1320),
                (335, 1321),
                (335, 1322),
            ],
            [
                (465, 1317),
                (465, 1318),
                (465, 1319),
                (465, 1320),
                (465, 1321),
                (465, 1322),
            ],
            [
                (609, 1317),
                (609, 1318),
                (609, 1319),
                (609, 1320),
                (609, 1321),
                (609, 1322),
            ],
            [
                (752, 1317),
                (752, 1318),
                (752, 1319),
                (752, 1320),
                (752, 1321),
                (752, 1322),
            ],
        ]
    )

    COLOR_RANGES = {
        "T": ((128, 218), (63, 106), (128, 215)),
        "Z": ((144, 240), (52, 97), (59, 111)),
        "S": ((110, 180), (130, 230), (52, 100)),
        "L": ((141, 245), (89, 150), (51, 104)),
        "J": ((77, 121), (63, 103), (136, 226)),
        "I": ((49, 98), (144, 229), (111, 178)),
        "O": ((160, 200), (140, 170), (51, 70)),
    }

    def __init__(self, weights=None):
        self.hold = None
        self.next_blocks_attr = [None, None, None, None, None]
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

        self.queue_perceptions = multiprocessing.Queue()
        self.queue_actions = multiprocessing.Queue()

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

    def next_blocks(self, screenshot: np.typing.NDArray[np.uint8]) -> list:
        return [
            self.most_frequent(self.possible_colors(screenshot, i)) for i in range(0, 5)
        ]

    def possible_colors(
        self, screenshot: np.typing.NDArray[np.uint8], index: int
    ) -> list:
        return [self.color(screenshot[r, c]) for r, c in self.COORDINATES[index]]

    def color(self, rgb: np.typing.NDArray[np.uint8] | Sequence[int]) -> str | None:
        r, g, b = rgb
        for name, (
            (r_min, r_max),
            (g_min, g_max),
            (b_min, b_max),
        ) in self.COLOR_RANGES.items():
            if r_min <= r <= r_max and g_min <= g <= g_max and b_min <= b <= b_max:
                return name
        return None

    def most_frequent(self, lista: list) -> str:
        return max(set(lista), key=lista.count)

    def start(self):
        p_processing = multiprocessing.Process(
            target=self.percept, args=(self.queue_perceptions,)
        )
        p_computing = multiprocessing.Process(
            target=self.compute, args=(self.queue_perceptions, self.queue_actions)
        )
        p_acting = multiprocessing.Process(
            target=self.action, args=(self.queue_actions,)
        )
        
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
