import requests

from flask import render_template
from io import BytesIO
from PIL import Image 



def get_book_data(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        api_response = response.json()
        print(api_response)
        if api_response['totalItems'] > 0:
            book_data = api_response['items'][0]['volumeInfo']
            title = book_data['title']
            authors = book_data['authors']
            language = book_data['language']
            cover = get_cover(book_data['imageLinks']['thumbnail'])
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

