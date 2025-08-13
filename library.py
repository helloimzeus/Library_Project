import json
import os
from typing import List, Optional
import httpx
from book import Book

OPENLIB_ISBN_URL = "https://openlibrary.org/isbn/{isbn}.json"
OPENLIB_AUTHOR_URL = "https://openlibrary.org{key}.json"
OPENLIB_SEARCH_URL = "https://openlibrary.org/search.json?isbn={isbn}"

class Library:
    def __init__(self, filename: str = "library.json"):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()

    # ---------- Yardımcılar ----------
    def _normalize_isbn(self, isbn: str) -> str:
        """Tire/boşlukları kaldırır, 'x'→'X' yapar."""
        return (isbn or "").replace("-", "").replace(" ", "").upper()

    def _http(self) -> httpx.Client:
        """302 yönlendirmelerini takip eden ortak HTTP istemcisi."""
        return httpx.Client(
            timeout=8.0,
            follow_redirects=True,
            headers={
                "User-Agent": "LibraryCLI/1.0 (educational; contact: example@example.com)"
            },
        )

    # jsondan kitapları yükler ve kaydeder
    def load_books(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book(**item) for item in data]
        else:
            self.books = []

    def save_books(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([b.__dict__ for b in self.books], f, ensure_ascii=False, indent=4)

    # kitap ekle, sil, listele, ara
    def add_book(self, book: Book) -> bool:
        norm = self._normalize_isbn(book.isbn)
        if any(self._normalize_isbn(b.isbn) == norm for b in self.books):
            return False
        # kayda normalize edilmiş ISBN yaz
        book.isbn = norm
        self.books.append(book)
        self.save_books()
        return True

    def remove_book(self, isbn: str) -> bool:
        norm = self._normalize_isbn(isbn)
        before = len(self.books)
        self.books = [b for b in self.books if self._normalize_isbn(b.isbn) != norm]
        removed = len(self.books) < before
        if removed:
            self.save_books()
        return removed

    def list_books(self) -> List[Book]:
        return self.books

    def find_book(self, isbn: str) -> Optional[Book]:
        norm = self._normalize_isbn(isbn)
        for b in self.books:
            if self._normalize_isbn(b.isbn) == norm:
                return b
        return None

    def _fetch_isbn_json(self, isbn: str) -> dict:
        """ISBN temel kitap verisini çeker."""
        url = OPENLIB_ISBN_URL.format(isbn=isbn)
        with self._http() as client:
            resp = client.get(url)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        if "application/json" not in (resp.headers.get("content-type", "")).lower():
            return {}
        return resp.json()

    def _fetch_author_name(self, author_key: str) -> Optional[str]:
        """Author yazar adını çeker"""
        url = OPENLIB_AUTHOR_URL.format(key=author_key)
        with self._http() as client:
            resp = client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        if "application/json" not in (resp.headers.get("content-type", "")).lower():
            return None
        data = resp.json()
        return data.get("name")

    def _extract_title_and_authors(self, data: dict) -> Optional[tuple[str, str]]:
        """ISBN JSON'undan başlık ve yazar üretir."""
        if not data:
            return None
        title = data.get("title")
        authors = data.get("authors", [])
        names: List[str] = []
        for a in authors:
            if isinstance(a, dict) and a.get("name"):
                names.append(a["name"])
                continue
            key = a.get("key") if isinstance(a, dict) else None
            if key:
                name = self._fetch_author_name(key)
                if name:
                    names.append(name)
        author_str = ", ".join(names) if names else "Bilinmiyor"
        if not title:
            return None
        return title, author_str

    def _fetch_from_search_api(self, isbn: str) -> Optional[tuple[str, str]]:
        """/search.json?isbn=... üzerinden başlık ve yazar(lar)ı dener (fallback)."""
        url = OPENLIB_SEARCH_URL.format(isbn=isbn)
        with self._http() as client:
            resp = client.get(url)
        resp.raise_for_status()
        if "application/json" not in (resp.headers.get("content-type", "")).lower():
            return None
        data = resp.json()
        docs = data.get("docs", [])
        if not docs:
            return None
        doc = docs[0]
        title = doc.get("title")
        authors = doc.get("author_name") or []
        if not title:
            return None
        author_str = ", ".join(authors) if authors else "Bilinmiyor"
        return title, author_str

    def add_book_by_isbn(self, isbn: str) -> tuple[bool, str]:
        """ISBN ile Open Library'den veriyi çekip kitabı ekler."""
        isbn = self._normalize_isbn(isbn)
        if not isbn:
            return False, "ISBN boş olamaz."
        if self.find_book(isbn):
            return False, "Bu ISBN zaten kayıtlı."

        try:
            # 1) ISBN endpoint'i
            raw = self._fetch_isbn_json(isbn)
            info = self._extract_title_and_authors(raw)
            # 2) Olmazsa search API fallback
            if not info:
                info = self._fetch_from_search_api(isbn)

            if not info:
                return False, "Kitap bulunamadı."
            title, author = info
            ok = self.add_book(Book(title=title, author=author, isbn=isbn))
            return (True, f"Eklendi: {title} – {author}") if ok else (False, "Eklerken bir sorun oluştu.")
        except httpx.RequestError:
            return False, "Ağ hatası: İnternet bağlantınızı kontrol edin."
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False, "Kitap bulunamadı."
            return False, f"API hatası: {e.response.status_code}"
        except Exception:
            return False, "Beklenmeyen bir hata oluştu."
