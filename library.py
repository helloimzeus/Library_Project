import json
import os
from book import Book
class Library:
    def __init__(self, filename="library.json"):
        self.filename = filename
        self.books = []
        self.load_books()

    """library.json dosyasından kitapları yükler"""
    def load_books(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book(**book) for book in data]
        else:
            self.books = []

            
    """library.json dosyasına kitapları kaydeder"""
    def save_books(self):
        with open(self.filename, 'w', encoding="utf-8") as f:
            json.dump([book.__dict__ for book in self.books], f, ensure_ascii=False, indent=4)


    """Kitap ekler"""
    def add_book(self, book: Book):
        self.books.append(book)
        self.save_books()


    """Kitap ISBN'sine göre siler"""
    def remove_book(self, isbn: str):
        self.books = [book for book in self.books if book.isbn != isbn]
        self.save_books()


    """Kitapları listele"""
    def list_books(self):
        return self.books
    


    """Kitap ISBN'sine göre bulur"""
    def find_book(self, isbn: str):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None