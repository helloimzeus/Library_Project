import pytest
from fastapi.testclient import TestClient
import api
from library import Library

class DummyResp:
    def __init__(self, status_code=200, json_data=None, headers=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.headers = headers or {"content-type": "application/json"}  # ← ÖNEMLİ
    def json(self): return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            req = httpx.Request("GET", "http://t")
            resp = httpx.Response(self.status_code, request=req)
            raise httpx.HTTPStatusError("err", request=req, response=resp)


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Her test izole kalsın diye geçici library dosyası
    lib = Library(filename=str(tmp_path / "lib.json"))
    # FastAPI dependency override
    api.app.dependency_overrides[api.get_library] = lambda: lib
    client = TestClient(api.app)
    yield client
    api.app.dependency_overrides.clear()

def test_create_and_list_book_success(client, monkeypatch):
    # Sadece library için çalışan sahte HTTP istemcisi
    def fake_http(self):
        class FakeClient:
            def __enter__(self): return self
            def __exit__(self, *exc): pass
            def get(self, url, **kwargs):
                if "/isbn/" in url:
                    return DummyResp(200, {"title": "Clean Code", "authors": [{"key": "/authors/OL1394243A"}]})
                if "/authors/" in url:
                    return DummyResp(200, {"name": "Robert C. Martin"})
                if "/search.json" in url:
                    return DummyResp(200, {"docs": [{"title": "Clean Code", "author_name": ["Robert C. Martin"]}]})
                return DummyResp(404, {})
        return FakeClient()

    # <<< ÖNEMLİ: Sadece bizim Library'nin HTTP katmanını patch’le >>>
    monkeypatch.setattr("library.Library._http", fake_http)

    # POST /books
    r = client.post("/books", json={"isbn": "978-0132350884"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Clean Code"
    assert "Robert" in data["author"]

    # GET /books
    r2 = client.get("/books")
    assert r2.status_code == 200
    items = r2.json()
    assert len(items) == 1
    assert items[0]["isbn"] == "9780132350884"  # normalize edilmiş


def test_create_book_not_found(client, monkeypatch):
    # Bu testte httpx.Client.get'i patch’lemek yeterli (JSON header DummyResp’te var)
    monkeypatch.setattr("library.httpx.Client.get", lambda *a, **k: DummyResp(404, {}))
    r = client.post("/books", json={"isbn": "000000"})
    assert r.status_code == 404
    assert "bulunamadı" in r.json()["detail"].lower()

def test_delete_book(client, monkeypatch):
    # önce ekle
    monkeypatch.setattr("library.httpx.Client.get",
        lambda *a, **k: DummyResp(200, {"title": "X", "authors": []}))
    r = client.post("/books", json={"isbn": "111"})
    assert r.status_code == 201

    # sonra sil
    r2 = client.delete("/books/111")
    assert r2.status_code == 200
    assert r2.json()["detail"] == "Silindi."

    # tekrar silmeye çalış → 404
    r3 = client.delete("/books/111")
    assert r3.status_code == 404
