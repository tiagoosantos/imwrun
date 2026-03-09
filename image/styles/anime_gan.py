import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path
from PIL import Image


# ==========================
# PATH DO MODELO
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "animeganv3.onnx"


# ==========================
# CONFIGURAÇÕES
# ==========================

MAX_DIMENSION = 1024


# ==========================
# CARREGAR MODELO UMA VEZ
# ==========================

session = ort.InferenceSession(str(MODEL_PATH))


# ==========================
# PREPROCESS
# ==========================

def _preprocess(img_pil):

    img = img_pil.convert("RGB")
    img = np.array(img)

    h, w = img.shape[:2]

    original_size = (h, w)

    # reduzir resolução se necessário
    if max(h, w) > MAX_DIMENSION:

        scale = MAX_DIMENSION / max(h, w)

        new_h = int(h * scale)
        new_w = int(w * scale)

        img = cv2.resize(img, (new_w, new_h))

        h, w = img.shape[:2]

    # melhorar contraste (bom para fotos de corrida)
    img = cv2.convertScaleAbs(img, alpha=1.15, beta=-5)

    # ajustar para múltiplos de 8
    h = h - h % 8
    w = w - w % 8

    img = cv2.resize(img, (w, h))

    # normalização [-1,1]
    img = img.astype(np.float32) / 127.5 - 1.0

    # batch dimension
    img = np.expand_dims(img, axis=0)

    return img, original_size


# ==========================
# INFERÊNCIA
# ==========================

def _inference(mat):

    input_name = session.get_inputs()[0].name

    fake_img = session.run(None, {input_name: mat})[0]

    return fake_img


# ==========================
# POSTPROCESS
# ==========================

def _postprocess(fake_img, original_size):

    img = (np.squeeze(fake_img) + 1) / 2 * 255

    img = np.clip(img, 0, 255).astype(np.uint8)

    img = cv2.resize(img, (original_size[1], original_size[0]))

    return Image.fromarray(img)


# ==========================
# FUNÇÃO PRINCIPAL
# ==========================

def aplicar(img):

    mat, original_size = _preprocess(img)

    fake_img = _inference(mat)

    return _postprocess(fake_img, original_size)