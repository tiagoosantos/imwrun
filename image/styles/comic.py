from PIL import ImageFilter, ImageEnhance


def aplicar(img):

    img = img.filter(ImageFilter.SMOOTH_MORE)

    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.8)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.4)

    edges = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    return edges