import numpy as np
from pyautogui import screenshot


class Environment:
    def screenshot_arr(self) -> np.typing.NDArray:
        return np.array(screenshot())

    def response(self, action: str):
        if action == "*":
            return self.screenshot_arr()
        return False
