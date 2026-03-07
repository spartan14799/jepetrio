import agent
import numpy as np
import cv2 as cv

a = agent.Agent()

img_rgb = cv.imread("testing/2026-03-07-151156_hyprshot.png", cv.IMREAD_COLOR_BGR)
print(img_rgb)
