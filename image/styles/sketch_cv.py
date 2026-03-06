import cv2
from image.utils.opencv_adapter import aplicar_opencv


def _sketch_cv(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    inv = 255 - gray

    blur = cv2.GaussianBlur(inv, (21, 21), 0)

    sketch = cv2.divide(gray, 255 - blur, scale=256)

    sketch = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    return sketch


def aplicar(img):
    return aplicar_opencv(img, _sketch_cv)