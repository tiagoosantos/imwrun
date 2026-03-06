import cv2

def aplicar(img_path):

    img = cv2.imread(img_path)

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

    color = cv2.bilateralFilter(img, 9, 300, 300)

    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon