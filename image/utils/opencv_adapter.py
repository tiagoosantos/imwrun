import cv2
import numpy as np
from PIL import Image


def aplicar_opencv(img_pil, func):

    # garantir RGB
    img = img_pil.convert("RGB")

    # PIL → numpy
    img = np.array(img)

    # RGB → BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # aplicar processamento
    img = func(img)

    # BGR → RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # numpy → PIL
    return Image.fromarray(img)