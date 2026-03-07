import multiprocessing
from typing import Sequence
import pyautogui
import time
import numpy as np


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
                (613, 1317),
                (613, 1318),
                (613, 1319),
                (613, 1320),
                (613, 1321),
                (613, 1322),
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
        "S": ((100, 186), (130, 237), (52, 103)),
        "L": ((141, 245), (89, 150), (51, 104)),
        "J": ((77, 121), (63, 103), (136, 226)),
        "I": ((49, 98), (144, 229), (111, 178)),
        "O": ((142, 230), (124, 202), (51, 98)),
    }

    def __init__(self):
        self.hold = None
        self.next_blocks_attr = [None, None, None, None, None]

        self.tablero = [[0 for _ in range(10)] for _ in range(20)]

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

        p_processing.start()
        p_computing.start()
        p_acting.start()

        try:
            p_acting.join()
            p_computing.join()
            p_acting.join()

        except KeyboardInterrupt:
            self.queue_actions.put("^")

            p_computing.terminate()
            p_processing.terminate()
            p_acting.join()
