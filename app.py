import re
import json

from api_requests import get_book_data

from base64 import b64encode, b64decode
from io import BytesIO

from image import compress, check_file_type
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required
from io import BytesIO
from PIL import Image  # delete after transferring to separate file
from werkzeug.security import check_password_hash, generate_password_hash

from pyzbar.pyzbar import decode

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
        "SELECT title, author, image FROM books JOIN users ON books.user_id = ?", session['user_id'])
    if books:
        return render_template('index.html', books=books)
    else:
        return render_template('index.html', books='You have no books')


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        input_type = request.form.get('add')

        if input_type == 'isbn':
            isbn = request.form.get('isbn')
            if isbn == '':
                return render_template('add_book.html', message='Please input something'), 404
            book = get_book_data(isbn)
            if book == False:
                return render_template('add_book.html', message='Please Try Again Or input Manually'), 404

        elif input_type == 'manual':
            manual_image = request.files['manual_image']
            if manual_image:
                if check_file_type(manual_image):
                    cover = Image.open(manual_image)
                    cover.resize((128, 196))
                else:
                    return render_template('add_book.html', message='File not supported')
            else:
                cover = None
            book = {
                'title': request.form.get('title').title().strip(),
                'author': request.form.get('author').title().strip(),
                'language': request.form.get('language').lower(),
                'cover': cover
            }

        elif input_type == 'bc-img':
            uploaded_image = request.files['barcode_img']
            if check_file_type(uploaded_image):
                image = Image.open(uploaded_image)
            else:
                return render_template('add_book.html', message='File not supported')

            barcode = decode(image)
            barcode = str(barcode[0][0])
            barcode = re.findall('\d+', barcode)[0]
            book = book = get_book_data(barcode)

        check_duplicate = db.execute(
            "SELECT id FROM books WHERE title = ? AND author = ? AND language = ? AND user_id = ?", book['title'], book['author'], book['language'], session['user_id'])
        if check_duplicate != []:
            return render_template('add_book.html', message='You already have this book: ' + book['title'] + '\nAdd anyway?')

        session['book'] = book
        return redirect('/add_book_confirm')
        # return render_template('add_book.html', message='Successfully added: '+book['title'])
    else:
        return render_template('add_book.html')


@app.route('/add_book_confirm', methods=['GET','POST'])
@login_required
def confirm_book():
    book = session.get('book')
    if request.method == 'POST':
        # save book cover if not False
        path = ''
        if book['cover'] != None:
            authors = ''
            # since author is a list with multiple possible authors
            # making a string out of it so we can concat in a str
            for author in book['author']:
                authors += author
            path = 'static/book_img/'+book['title'] + authors+'.jpg'
            path = path.replace(' ', '')
            book['cover'].save(path, quality=100)
        db.execute("INSERT INTO books (title, author, language, image, user_id) VALUES (?,?,?,?,?);",
                   book['title'], book['author'], book['language'], path, session['user_id'])
        print('hello')
        return render_template('add_book.html')
    else:

        image = book['cover']
        print(image)
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()
        encoded_image = b64encode(image_bytes).decode('utf-8')
        bookshelves = db.execute("SELECT id, description FROM bookshelves WHERE user_id =?;", session['user_id'])
        return render_template('add_book_confirm.html', book=book, cover = encoded_image, bookshelves = bookshelves)


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

        if width.isnumeric() and height.isnumeric() and int(width) > 0 and int(height) > 0:
            width = int(width)
            height = int(height)
            db.execute("INSERT INTO bookshelves (width, height, description, user_id) VALUES (?,?,?,?);",
                       width, height, description, session['user_id'])
            if uploaded_image:
                if not check_file_type(uploaded_image):
                    return render_template('add_bookshelf.html', message='File not supported')
                bookshelf_id = db.execute(
                    "SELECT id FROM bookshelves WHERE user_id = ? ORDER BY id DESC LIMIT 1;", session['user_id'])
                path = './static/shelf_img/' + 'bsi' + \
                    str(bookshelf_id[0]['id']) + '.jpg'
                db.execute("UPDATE bookshelves SET image = ? WHERE id =?;",
                           path, bookshelf_id[0]['id'])
                compress(uploaded_image, path)
            return render_template('add_bookshelf.html', message='Successfully Added')
        else:
            return render_template('add_bookshelf.html', message='Please insert a valid bookshelf size')
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
