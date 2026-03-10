import numpy as np
import cv2 as cv
from pyautogui import screenshot


class Environment:
    START_COORDS = (520, 975)
    START_COLOR = np.array([255, 198, 0])
    def screenshot_arr(self) -> np.typing.NDArray:
        return np.array(screenshot())

    def response(self, action: str):
        if action == "*":
            return self.screenshot_arr()
        else:
            return None


    def game_countdown(self, sct: np.typing.NDArray)-> bool:
        if np.all(sct[self.START_COORDS] == self.START_COLOR):
            return True
        return False