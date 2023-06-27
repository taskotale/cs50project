import re

from base64 import b64encode
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

db = SQL('sqlite:///bookshelf.db')

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/')
@login_required
def index():
    books = db.execute(
        "SELECT * FROM books JOIN users ON books.user_id = ?", session['user_id'])
    if books:
        return print(books)
    else:
        return render_template('index.html', message='You have no books')


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title').lower()
        author = request.form.get('author').lower()
        lang = request.form.get('language').lower()
        return render_template('add_book.html', message = 'Successfully added '+ title.title())
    else:
        return render_template('add_book.html')
    
@app.route('/add_bookshelf', methods=['GET', 'POST'])
@login_required
def add_bookshelf():
    if request.method == 'POST':
        bookshelf = request.form.get('bookshelf')
        uploaded_image = request.files['image']
        img = Image.open(uploaded_image)
        (width, height) = (int(img.width/4), int(img.height/4))
        img = img.resize((width, height))
        img_path = './static/img/' + '1' + '.jpg'
        img.save(img_path, quality = 70)
        if bookshelf.isnumeric():
            bookshelf = int(bookshelf)
            return render_template('add_bookshelf.html', path = img_path)
        else:
            return render_template('add_bookshelf.html', message = 'Please enter a number')
    else:
        return render_template('add_bookshelf.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # clear if any user already connected
    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return render_template('login.html', message='Please input name')
        elif not request.form.get('password'):
            return render_template('login.html', message='Please input password')

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get('username')
        )
        if len(rows) != 1 or not check_password_hash(
            rows[0]['hash'], request.form.get('password')
        ):
            return render_template('login.html', message='does not exist')

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # successful login
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''Register user'''
    if request.method == 'POST':
        #  first we get the posted info from the user
        username = request.form.get('username')
        password = request.form.get('password')
        repeatPass = request.form.get('confirmation')

        if not request.form.get('username'):
            return render_template('register.html', message='Please input name')
        elif not request.form.get('password'):
            return render_template('register.html', message='Please input password')
        elif not request.form.get('confirmation'):
            return render_template('register.html', message='Please confirm password')

        user_exist = db.execute(
            "SELECT username FROM users WHERE username = ?;", username
        )

        def validateUser(username, user_exist):
            if user_exist != []:
                return 'username already exists'
            else:
                return True

        def validatePass(password, repeatPass):
            if password != repeatPass:
                return 'password not matching'
            elif len(password) < 3:
                return 'password too short'
            # currently no need for additional security check
            # elif not re.search('[a-z]', password):
            #     return 'password must contain a lower case letter'
            # elif not re.search('[A-Z]', password):
            #     return 'password must contain a capital letter'
            # elif not re.search('[0-9]', password):
            #     return 'password must contain a number'
            # elif not re.search('[_@$]', password):
            #     return 'password must contain _ or @ or $'
            else:
                return True

        validName = validateUser(username, user_exist)
        validPass = validatePass(password, repeatPass)

        if validName == True:
            if validPass == True:
                hash_password = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?);",
                    username,
                    hash_password,
                )
                return redirect('/')
            else:
                # error not (validPass)
                return render_template('register.html', message='Invalid password')
        else:
            # error not valid (validName)
            return render_template('register.html', message='Invalid username')
    else:
        return render_template('register.html')
