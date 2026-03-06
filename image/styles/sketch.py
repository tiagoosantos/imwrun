from PIL import ImageOps, ImageFilter, ImageEnhance

def aplicar(img):

    gray = ImageOps.grayscale(img)

    edges = gray.filter(ImageFilter.FIND_EDGES)

    enhancer = ImageEnhance.Contrast(edges)
    edges = enhancer.enhance(2)

    return ImageOps.invert(edges).convert("RGBA")