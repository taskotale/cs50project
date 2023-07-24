# Bookshelf Web Application
#### Video Demo:  <https://youtu.be/F0oh_2ermYU>
#### Description: The Bookshelf web application is a simple and user-friendly platform that allows users to manage their book collection. 

Users can add books to their virtual bookshelves, browse through their collection, and search for new books using the Google Books API. The app will keep track where your books are, so you can easily find them as well as personal notes. The application also provides features like "Surprise Me!" to randomly pick an unread book and a section to keep track of borrowed books.

## Features

- User authentication: Users can register and log in to access their personalized bookshelf.
- Add books: Users can add books to their collection by providing the ISBN, manually entering book details, or scanning the book's barcode using an image.
- Browse and search: Users can browse through their book collection and search for books by title or author.
- Borrowed books: Users can keep track of books they borrowed to or from others.
- "Surprise Me!": Users can discover a random unread book from their collection.
- Bookshelf management: Users can add new bookshelves to organize their collection.

## Dependencies

The Bookshelf web application relies on the following external libraries and APIs:

- flask
- Bootstrap
- Google Books API: Used to fetch book details and cover images.
- PIL (Python Imaging Library): Used for image manipulation and compression.
- CS50: Library used for working with SQLite database with python.
- re: Used for password and username to match regular expressions against user input.
- os: Used to remove images from storage.
- base64 and IO: Used to encode images that will be shown on html without saving on server.
- pyzbar.pyzbar: Used for decoding the barcode on uploaded images
- werkzeug.security: Used to generate password hash

## Sections and components

##### app.py

In the file app.py is stored the main application logic and functions.

- There are few global items that are needed  in multiple routes:
    1. The db variable where we store the data from database 
    2. The get_books() function, which returns all the books for the current user
    3. The books_to_show list(array) which holds the books that will be shown on screen when a modal is on so we don't have to make multiple unnecessary calls to the database over and over.

- The / route - index. This is the main route to show books to the user. 
    -  Redirection:
        1. If redirected from 'Find': it will get the arguments from the url for the searched string. This section searches the database for similar input based on the 'title' OR 'author' and if the query does not produce a result it will request results from the Google Books API. (api_request.py)
        2. If redirected from 'Browse': it will query the database for all books with a specific bookshelf_id set in the books table.
        3. If redirected from the 'Surprise me' button: outputs a random single item from the queried list of unread books with the choice function from the random library.
        4. If looking from borrowed button: queries all books are marked as borrowed.
        5. If not redirected from anywhere uses the get_books() function to query all books.

    - All section will create a books dict/object which will then paginate the result with a simple function imported from the helpers.py file and stored in the book_to_show list for future use.

    - This route returns a render_template with necessary information to display the selected list of books.




