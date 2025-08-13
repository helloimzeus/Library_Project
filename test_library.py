import os
import json
import pytest
from book import Book
from library import Library

TEST_FILE = 'test_library.json'

@pytest.fixture


def library():
    """temiz dosya oluşturma"""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    return Library(TEST_FILE)

def test_add_and_find_book(library):
    book = Book("Test Kitap", "Test Yazar", "1234567890")
    library.add_book(book)
    found_book = library.find_book("1234567890")
    assert found_book is not None
    assert found_book.title == "Test Kitap"

def test_remove_book(library):
    book = Book("Test Kitap", "Test Yazar", "1234567890")
    library.add_book(book)
    library.remove_book("1234567890")
    assert library.find_book("1234567890") is None
def test_list_books(library):
    book1 = Book("Kitap 1", "Yazar 1", "1111111111")
    book2 = Book("Kitap 2", "Yazar 2", "2222222222")
    library.add_book(book1)
    library.add_book(book2)
    books = library.list_books()
    assert len(books) == 2