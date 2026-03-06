import cv2
import numpy as np
from image.utils.opencv_adapter import aplicar_opencv


def _manga(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 80, 200)

    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    edges = cv2.bitwise_not(edges)

    manga = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    return manga


def aplicar(img):
    return aplicar_opencv(img, _manga)