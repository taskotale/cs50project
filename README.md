# Bookshelf Web Application

#### Video Demo: <https://youtu.be/F0oh_2ermYU>

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
        1. The db object to work with the data from database
        2. The get_books() function, which returns all the books for the current user
        3. The books_to_show list(array) which holds the books that will be shown on screen when a modal is on so we don't have to make multiple unnecessary calls to the database over and over.

    - The " route - index. This is the main route to show books to the user.
        -  Redirection:
            1. If redirected from Find: it will get the arguments from the url for the searched string. This section searches the database for similar input based on the 'title' OR 'author' and if the query does not produce a result it will request results from the Google Books API. (api_request.py)
            2. If redirected from Browse: it will query the database for all books with a specific bookshelf_id set in the books table.
            3. If redirected from the Surprise me! button: outputs a random single item from the queried list of unread books with the choice function from the random library.
            4. If looking from Borrowed books button: queries all books are marked as borrowed.
            5. If not redirected from anywhere uses the get_books() function to query all books.

        - All section will _ _create a books dict/object_ _ which will then paginate the result with a simple function imported from the helpers.py file and stored in the book_to_show list for future use.

        - This route returns a render_template with necessary information to display the selected list of books.

    - The add_book route.
        - This route if accessed by "GET" returns an html page that allows the user to select the way they want to add a book. If "POST", this route will gather details to make a book object that will be saved in the session and redirect to "/add_book_confirm" route.
        - There are 3 ways to input details and add a book:
            1. Search by The International Standard Book Number (ISBN). If user submits ISBN, the route will fetch a response from the Google API with the **get_book_data()** function from api_requests.py.
            2. Search by barcode image.  If the user submits an image with a barcode on it, the _ _decode_ _ function from pyzbar.pyzbar library will extract the ISBN and use the same path as the previous method.
            3.Manual input. If this option is selected and sent thru, the route will create the book object based on the manual user input form.

    - The add_book_from_find route.
        This route is used to make an object out of the details found online with the 'Find' option and redirect to the "/add_book_confirm" route.

    - The add_book_confirm route.
        - When approaching this route with "GET" method, it displays the details found in the object gathered by "/add_book". Checks for possible duplicates, shows the cover image of the book(or generic image if none) without saving and offers an option to set where the book will go.
        - The "POST" method of this route handles the selection of the location on the specific bookshelf if any is chosen. After completing the details redirects to the "added_book" route.

    - The added_book route handles the process of saving the details in the database and images in the system. The path for the image is set by title and author and not by user(owner) so a single img can be reused for multiple user and minimize storage space. (Possible future versions will save on the local user system the images, mostly user uploaded)

    - The add_bookshelf route. This route gathers input from the user about new bookshelves which will add on the bookshelf db table.

    - The book_details route creates a 'modal' over the index page that uses the books_to_show global list.
        - If the method is "GET", offers the user the overview of the details of the selected book found by book id gathered from the url. The jquery/js on the html will offer the possibility to click on a field and edit the inputs.
        - If method is "POST", and assuming that the user made a change, this function will request the data from the form and update the database.

    - The browse route allows users to get a view of the books per bookshelf and the option to delete an empty bookshelf. Mostly sql commands.

    - The login route checks for users by username and hashed password in the database and saves user in the session.
    - The logout route clears the session data.
    - The register route register a new user to the database. Checks for a valid more secure password and hashes the same  with the library werkzeug.security.

##### api_requests.py

    This support .py handles the logic of requests from the Google API and creates appropriate book objects.
    - get_book_data() function gets a api response when queried by ISBN and creates a json which will be used to gather book info
    - get_book() function returns a book object based on the json response received from the API.
    Gets 2 arguments, the json data and a boolean which will help determine how to create a cover img.
    - get_cover() function requests an img from the url provided in the API response.
    - search_for_books() function is used to search the google api by search terms with returns multiple books.

##### helpers.py

    Provides helper functions login_required and paginate.
    Requires wraps from functools library so we can wrap separate routes in  app.py.
    The paginate function takes an array of objects and splits them into pages/arrays of specific lengths.

##### script in index.html

    This code provides help with the pagination from different sources, like all books, search or bookshelf books. Makes it dynamic so there is no need to hardcode it for all options and injects the href in the html.

#### SQL database tables

    The database contains 3 tables.
    - Users - holds the id, name and hashed password
    - Bookshelves - contains details about the shelves as well as the user_id that owns the shelf (wanted to omit but impossible since there is an option for an empty bookshelf which will loose track if just JOINed with books.)
    - Books - All the necessary details about the books.
