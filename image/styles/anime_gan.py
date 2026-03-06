import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "animeganv3.onnx"


# carregar modelo uma vez
session = ort.InferenceSession(str(MODEL_PATH))


def _preprocess(img):

    img = img.convert("RGB")
    img = np.array(img)

    h, w = img.shape[:2]

    # ajustar para múltiplos de 8
    h = h - h % 8
    w = w - w % 8

    img = cv2.resize(img, (w, h))

    img = img.astype(np.float32) / 127.5 - 1.0

    img = np.expand_dims(img, axis=0)

    return img, (h, w)


def _postprocess(fake_img, size):

    img = (np.squeeze(fake_img) + 1) / 2 * 255

    img = np.clip(img, 0, 255).astype(np.uint8)

    img = cv2.resize(img, (size[1], size[0]))

    return Image.fromarray(img)


def aplicar(img):

    original_size = img.size[::-1]

    mat, scale = _preprocess(img)

    input_name = session.get_inputs()[0].name

    fake_img = session.run(None, {input_name: mat})[0]

    return _postprocess(fake_img, original_size)