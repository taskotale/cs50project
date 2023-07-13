import requests

from flask import redirect, session
from functools import wraps




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

# splits list into sublist 
def paginate (list, per_page):
    if not per_page:
        per_page = 10
    pages = [list[x:x+per_page] for x in range(0, len(list), per_page)]
    return pages

