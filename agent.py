import multiprocessing
import pyautogui
import time
import numpy as np


class Agent:
    def __init__(self):
        self.coordinates_to_check = [
            [
                (701, 1234),
                (701, 1235),
                (701, 1236),
                (701, 1237),
                (701, 1238),
                (701, 1239),
            ],
            [
                (598, 1234),
                (598, 1235),
                (598, 1236),
                (598, 1237),
                (598, 1238),
                (598, 1239),
            ],
            [
                (491, 1234),
                (491, 1235),
                (491, 1236),
                (491, 1237),
                (491, 1238),
                (491, 1239),
            ],
            [
                (389, 1234),
                (389, 1235),
                (389, 1236),
                (389, 1237),
                (389, 1238),
                (389, 1239),
            ],
            [
                (284, 1234),
                (284, 1235),
                (284, 1236),
                (284, 1237),
                (284, 1238),
                (284, 1239),
            ],
            [(678, 266), (678, 266), (678, 266), (678, 266), (678, 266), (678, 266)],
        ]

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

    def next_blocks(self, screenshot: np.ndarray) -> list:
        next_block1 = self.most_frequent(self.possible_colors(screenshot, 0))
        next_block2 = self.most_frequent(self.possible_colors(screenshot, 1))
        next_block3 = self.most_frequent(self.possible_colors(screenshot, 2))
        next_block4 = self.most_frequent(self.possible_colors(screenshot, 3))
        next_block5 = self.most_frequent(self.possible_colors(screenshot, 4))
        hold = self.most_frequent(self.possible_colors(screenshot, 5))
        return [next_block1, next_block2, next_block3, next_block4, next_block5, hold]

    def possible_colors(self, screenshot: np.ndarray, index: int) -> list:
        result = []
        for coordinate_tuple in self.coordinates_to_check[index]:
            result.append(
                self.color(screenshot[coordinate_tuple[0]][coordinate_tuple[1]])
            )
        return result

    def color(self, rgb: tuple) -> str | None:
        if 128 <= rgb[0] <= 218 and 63 <= rgb[1] <= 103 and 128 <= rgb[2] <= 215:
            return "T"
        elif 144 <= rgb[0] <= 240 and 52 <= rgb[1] <= 97 and 59 <= rgb[2] <= 111:
            return "Z"
        elif 100 <= rgb[0] <= 186 and 130 <= rgb[1] <= 237 and 59 <= rgb[2] <= 103:
            return "S"
        elif 141 <= rgb[0] <= 240 and 89 <= rgb[1] <= 150 and 51 <= rgb[2] <= 104:
            return "L"
        elif 77 <= rgb[0] <= 121 and 63 <= rgb[1] <= 103 and 136 <= rgb[2] <= 226:
            return "J"
        elif 51 <= rgb[0] <= 98 and 144 <= rgb[1] <= 229 and 111 <= rgb[2] <= 178:
            return "I"
        elif 142 <= rgb[0] <= 230 and 124 <= rgb[1] <= 202 and 51 <= rgb[2] <= 98:
            return "O"
        return "None"

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
