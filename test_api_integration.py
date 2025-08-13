import pytest
from library import Library
from book import Book

class DummyResp:
    def __init__(self, status_code = 200, json_data = None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json
    def raise_for_status(self):
        if 400 <= self.status_code:
            import httpx
            request = httpx.Request("GET", "http://test")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("Error", request=request, response=response)
    def test_add_book_by_isbn_success(monkeypatch, tmp_path):
        libfile = tmp_path / "library.json"
        library = Library(filename=str(libfile))


        isbn_json = {
            "title": "clean code",
            "authors": [{"key": "/authors/OL1394243A"}]
        }
        author_json = {"name": "Robert C. Martin"}

    # httpx.Client.get fonksiyonunu sahteleyelim
        def fake_get(self, url):
            if url.endswith(".json") and "/isbn/" in url:
                return DummyResp(200, isbn_json)
            if url.endswith(".json") and "/authors/" in url:
                return DummyResp(200, author_json)
            return DummyResp(404, {})

        monkeypatch.setattr("httpx.Client.get", fake_get)

        ok, msg = library.add_book_by_isbn("9780132350884")
        assert ok is True
        assert "Clean Code" in msg
        assert any(b.title == "Clean Code" and b.author == "Robert C. Martin" for b in library.list_books())

def test_add_book_by_isbn_not_found(monkeypatch, tmp_path):
    libfile = tmp_path / "lib.json"
    library = Library(filename=str(libfile))

    def fake_get(self, url):
        return DummyResp(404, {})

    monkeypatch.setattr("httpx.Client.get", fake_get)

    ok, msg = library.add_book_by_isbn("0000000000")
    assert ok is False
    assert "bulunamadı" in msg.lower()

def test_add_book_by_isbn_duplicate(monkeypatch, tmp_path):
    libfile = tmp_path / "lib.json"
    library = Library(filename=str(libfile))

    # aynı başarılı cevap
    isbn_json = {"title": "Test", "authors": []}
    def fake_get(self, url):
        return DummyResp(200, isbn_json)
    monkeypatch.setattr("httpx.Client.get", fake_get)

    ok1, _ = library.add_book_by_isbn("111")
    ok2, msg2 = library.add_book_by_isbn("111")
    assert ok1 is True
    assert ok2 is False
    assert "zaten" in msg2.lower()