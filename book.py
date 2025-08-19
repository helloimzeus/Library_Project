class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

    # çıktıların düzgün görünmesi için
    def __repr__(self):
        return f"Book(title={self.title!r}, author={self.author!r}, isbn={self.isbn!r})"
