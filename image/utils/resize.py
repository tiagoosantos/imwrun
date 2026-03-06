from PIL import Image

def resize_cover(image, target_w, target_h):

    ratio = max(target_w / image.width, target_h / image.height)

    new_size = (
        int(image.width * ratio),
        int(image.height * ratio)
    )

    image = image.resize(new_size, Image.LANCZOS)

    left = (image.width - target_w) // 2
    top = (image.height - target_h) // 2

    right = left + target_w
    bottom = top + target_h

    return image.crop((left, top, right, bottom))