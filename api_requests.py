import requests

from io import BytesIO
from PIL import Image 



def get_book_data(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        api_response = response.json()
        if api_response['totalItems'] > 0:
            book_data = api_response['items'][0]['volumeInfo']
            title = book_data['title']
            authors = book_data['authors']
            language = book_data['language']
            print('BOOK DATA')
            print(book_data)
            print('BOOK DATA ENDDDD')
            if 'imageLinks' in book_data:
                cover = get_cover(book_data['imageLinks']['thumbnail'])
            else:
                cover = Image.open('static/book_img/generic_book.jpg')
            book = {
                'title': title,
                'author': authors,
                'language': language,
                'cover': cover
            }
            return book
        else:
            return False
    return False



def get_cover(url):
    response = requests.get(url)
    if response.status_code == 200:
        cover = response.content
        cover_img = Image.open(BytesIO(cover))
        return cover_img
    else:
        return False

