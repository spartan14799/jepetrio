import multiprocessing
import pyautogui
import time


class Agent:
    def __init__(self):

        self.tablero = [[0 for _ in range(10)] for _ in range(20)]

        self.piezas_mapeo = {
            'I': [
                [(0,0), (0,1), (0,2), (0,3)], [(0,2), (1,2), (2,2), (3,2)],
                [(0,0), (0,1), (0,2), (0,3)], [(0,2), (1,2), (2,2), (3,2)]
            ],
            'J': [
                [(0,0), (1,0), (1,1), (1,2)], [(0,1), (0,2), (1,1), (2,1)],
                [(1,0), (1,1), (1,2), (2,2)], [(0,1), (1,1), (2,0), (2,1)]
            ],
            'L': [
                [(0,2), (1,0), (1,1), (1,2)], [(0,1), (1,1), (2,1), (2,2)],
                [(1,0), (1,1), (1,2), (2,0)], [(0,0), (0,1), (1,1), (2,1)]
            ],
            'O': [
                [(0,0), (0,1), (1,0), (1,1)] # El cubo no cambia al rotar
            ],
            'S': [
                [(0,1), (0,2), (1,0), (1,1)], [(0,1), (1,1), (1,2), (2,2)]
            ],
            'T': [
                [(0,1), (1,0), (1,1), (1,2)], [(0,1), (1,1), (2,1), (1,2)],
                [(1,0), (1,1), (1,2), (2,1)], [(0,1), (1,1), (2,1), (1,0)]
            ],
            'Z': [
                [(0,0), (0,1), (1,1), (1,2)], [(0,2), (1,1), (1,2), (2,1)]
            ]
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
