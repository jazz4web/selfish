import io
import os

from PIL import Image


def resize(size, image=None):
    b = None
    if image is None:
        f = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'images', 'empty.png')
        try:
            image = Image.open(f)
        except OSError:
            return None
    else:
        b = io.BytesIO(image)
        try:
            image = Image.open(b)
        except:
            b.close()
            return None
    v = io.BytesIO()
    out = image.resize((size, size))
    out.save(v, format='PNG')
    v.seek(0)
    res = v.read()
    out.close()
    v.close()
    image.close()
    if b:
        b.close()
    return res
