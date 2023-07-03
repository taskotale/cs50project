import re
import requests

from api_requests import get_book_data
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required
from PIL import Image  # delete after transferring to separate file
from werkzeug.security import check_password_hash, generate_password_hash

# using helper function for login required

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
        return render_template('index.html', message='you have something')
    else:
        return render_template('index.html', message='You have no books')


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        input_type = request.form.get('add')

        if input_type == 'isbn':
            isbn = request.form.get('isbn')
            book = get_book_data(isbn)
            if book == False:
                return render_template('add_book.html', message='Please Try Again Or input Manually'), 404
        elif input_type == 'manual':
            book = {
                'title': request.form.get('title').title().strip(),
                'author': request.form.get('author').title().strip(),
                'language': request.form.get('language').lower(),
                'cover': None
            }
    
        check_duplicate = db.execute(
            "SELECT id FROM books WHERE title = ? AND author = ? AND language = ? AND user_id = ?", book['title'], book['author'], book['language'], session['user_id'])
        if check_duplicate != []:
            return render_template('add_book.html', message='You already have this book: ' + book['title'] + '\nAdd anyway?')
        # FIND BOOK LOCATION ask where is this book
        # FIND BOOK LOCATION
        # FIND BOOK LOCATION
        # FIND BOOK LOCATION
        # FIND BOOK LOCATION
        
        # save book cover if not False
        path = ''
        if book['cover'] != None:
            authors = ''
            # since author is a list with multiple possible authors
            # making a string out of it so we can concat in a str
            for author in book['author']:
                authors += author
            path = 'static/book_img/'+book['title'] + authors+'.jpg'
            path = path.replace(' ','')
            book['cover'].save(path, quality=100)

        db.execute("INSERT INTO books (title, author, language, image, user_id) VALUES (?,?,?,?,?);", 
                   book['title'], book['author'], book['language'], path, session['user_id'])

        # isbn test numbers
        #  978-0-06-264154-0 - working
        #  978-86-6423-003-2 - not-working
        return render_template('add_book.html', message='Successfully added '+book['title'])
    else:
        return render_template('add_book.html')


@app.route('/add_bookshelf', methods=['GET', 'POST'])
@login_required
def add_bookshelf():
    if request.method == 'POST':
        width = request.form.get('width')
        height = request.form.get('height')
        description = request.form.get('description')

        # using the PIL module for image manipulation
        uploaded_image = request.files['image']
        # transfer image function to separate .py
        if uploaded_image:
            img = Image.open(uploaded_image)
            # (width, height) = (int(img.width/4), int(img.height/4))
            # img = img.resize((width, height))
            # img_path = './static/shelf_img/' + shelf_id + '.jpg'
            # img.save(img_path, quality=70)

        if width.isnumeric() and height.isnumeric() and int(width) > 0 and int(height) > 0:
            width = int(width)
            height = int(height)
            db.execute("INSERT INTO bookshelves (width, height, description, user_id) VALUES (?,?,?,?);",
                       width, height, description, session['user_id'])
            return render_template('add_bookshelf.html', message='Successfully Added')
        else:
            return render_template('add_bookshelf.html', message='not gooooood')
    else:
        return render_template('add_bookshelf.html')


# reused code from previous problem for login, logout and register
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

# @app.route('/book/<isbn>')
# def get_book(isbn):
#     url = f"https://api.openbd.jp/v1/get?isbn={isbn}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         book_data = response.json()
#         return jsonify(book_data)
#     else:
#         return jsonify(error='Book not found'), 404
