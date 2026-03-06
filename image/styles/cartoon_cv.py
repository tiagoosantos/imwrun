import cv2
from image.utils.opencv_adapter import aplicar_opencv


def _cartoon(img):

    # melhorar contraste
    img = cv2.convertScaleAbs(img, alpha=1.2, beta=-10)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.medianBlur(gray, 5)

    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9,
        9
    )

    color = cv2.bilateralFilter(img, 9, 250, 250)

    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon


def aplicar(img):
    return aplicar_opencv(img, _cartoon)