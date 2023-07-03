import requests

from flask import redirect, session
from functools import wraps
from io import BytesIO
from PIL import Image



def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# def compress_img(uploaded_image):
#     img = Image.open(uploaded_image)
#     (width, height) = (int(img.width/4), int(img.height/4))
#     img = img.resize((width, height))
#     img_path = './static/img/' + '1' + '.jpg'
#     img.save(img_path, quality=70)
#     return 
