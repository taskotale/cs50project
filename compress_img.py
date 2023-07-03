from PIL import Image


def compress(upload, path):
    img = Image.open(upload)
    (width, height) = (int(img.width/4), int(img.height/4))
    img = img.resize((width, height))
    img.save(path, quality=70)
    return
