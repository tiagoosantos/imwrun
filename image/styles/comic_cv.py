import cv2
from image.utils.opencv_adapter import aplicar_opencv


def _comic_cv(img):

    color = cv2.bilateralFilter(img, 9, 300, 300)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)

    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9,
        2
    )

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    cartoon = cv2.bitwise_and(color, edges)

    return cartoon


def aplicar(img):
    return aplicar_opencv(img, _comic_cv)