from PIL import ImageFilter, ImageEnhance

def aplicar(img):

    img = img.filter(ImageFilter.GaussianBlur(1.5))

    edges = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    enhancer = ImageEnhance.Color(edges)
    img = enhancer.enhance(1.35)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.25)

    return img