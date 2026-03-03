import multiprocessing
import pyautogui
import time


class Agent:
    def __init__(self):
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
            p_acting.start()
            p_computing.start()
            p_acting.start()

        except KeyboardInterrupt:
            self.queue_actions.put("^")

            p_computing.terminate()
            p_computing.terminate()
