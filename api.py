from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List as TList
from library import Library, Book


app = FastAPI(title="Library API", version="1.0.0")

def get_library() -> Library:
    return app.state.library

@app.on_event("startup")
def startup():
    app.state.library = Library(filename="library.json")


"""pydantic modelleri"""
class BookOut(BaseModel):
    title: str
    author: str
    isbn: str

class ISBNIn(BaseModel):
    isbn: str = Field(..., description="Kitabın ISBN'i")

@app.get("/books", response_model=TList[BookOut],summary ="Tüm Kitapları listele")
def list_books(lib: Library = Depends(get_library)):
    return [BookOut(title=b.title, author=b.author, isbn=b.isbn) for b in lib.list_books()]
    
@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED, summary="ISBN ile Kitap Ekle")

def create_book(payload: ISBNIn, lib: Library = Depends(get_library)):
    ok, msg = lib.add_book_by_isbn(payload.isbn)
    if not ok:

        detail = msg

        if "zaten" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        if "boş" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        if "bulunamadı" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    
    book = lib.find_book(payload.isbn)
    if not book:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Kitap eklendi ancak bulunamadı.")
    return BookOut(title=book.title, author=book.author, isbn=book.isbn)

@app.delete("/books/{isbn}", summary="ISBN ile Kitap Sil")
def delete_book(isbn: str, lib: Library = Depends(get_library)):
    removed = lib.remove_book(isbn)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitap bulunamadı.")
    return {"detail": "Silindi."}