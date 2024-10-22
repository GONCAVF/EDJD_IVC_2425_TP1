import pygame
from pygame.locals import *
import cv2
import numpy as np


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
