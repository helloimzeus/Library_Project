# 📚 Library Project – Python 202 Bootcamp
**Aşama 1 → OOP (CLI) · Aşama 2 → Open Library API · Aşama 3 → FastAPI**

Bu proje; OOP ile terminal uygulaması geliştirmenizi, ISBN ile **Open Library** üzerinden kitap bilgisi çekerek uygulamayı zenginleştirmenizi ve son olarak **FastAPI** ile kendi web API’nizi yazmanızı amaçlar. Veriler `library.json` dosyasında kalıcı olarak tutulur.

## ✨ Özellikler
- **Aşama 1 (CLI)**  
  - `Book` ve `Library` sınıfları  
  - Kitap ekleme/silme/listeleme/arama  
  - JSON dosyasına kalıcı kayıt
- **Aşama 2 (API Entegrasyonu)**  
  - `httpx` ile **Open Library**’den ISBN’e göre kitap başlığı ve yazar(lar)ını çekme  
  - ISBN normalizasyonu (`-`/boşluk temizliği, `x→X`)  
  - 302 yönlendirmelerini izleyen **HTTP istemcisi**  
  - `/isbn/{isbn}.json` bulunamazsa `/search.json?isbn=...` **fallback**
- **Aşama 3 (FastAPI)**  
  - `GET /books` – tüm kitaplar  
  - `POST /books` – `{ "isbn": "..." }` gövdesiyle kitap ekler  
  - `DELETE /books/{isbn}` – kitabı siler  
  - Otomatik Swagger UI: `/docs`

---

## 🗂️ Proje Yapısı
```
Library_Project/
├── book.py
├── library.py
├── main.py
├── api.py
├── library.json
├── requirements.txt
├── test_library.py
├── test_api_integration.py
└── test_api_endpoints.py
```

---

## 🔧 Gereksinimler
- Python **3.10+** (Windows 10/11, macOS, Linux)
- İnternet bağlantısı (Aşama 2/3 canlı denemeler için)

---

## 🚀 Kurulum
```bash
# Proje klasörüne gir
cd Library_Project

# Sanal ortam (önerilir)
python -m venv venv

# Windows
.env\Scriptsctivate
# macOS / Linux
source venv/bin/activate

# Bağımlılıklar
python -m pip install -U pip
python -m pip install -r requirements.txt
```

`requirements.txt` içeriği (örnek):
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
httpx>=0.27.0
pytest>=8.3.0
```

---

## 🖥️ Aşama 1–2: Terminal Uygulaması (CLI)
Çalıştır:
```bash
python main.py
```

Menü:
```
1. Kitap Ekle (ISBN ile)
2. Kitap Sil
3. Kitapları Listele
4. Kitap Ara
5. Çıkış
```

- **Kitap Ekle**: Sadece ISBN girersiniz. Uygulama Open Library’den başlık ve yazar(lar)ını çeker.  
- **Kalıcı kayıt**: `library.json` dosyasında saklanır (uygulama kapansa da kaybolmaz).

> Notlar  
> • ISBN’ler normalize edilir (tire/boşluk silinir).  
> • `/isbn/{isbn}.json` 404 verirse `/search.json?isbn=...` ile yedek arama yapılır.  
> • HTTP istemcisi 302 yönlendirmeleri takip eder ve uygun `User-Agent` başlığı ile istek atar.

---

## 🌐 Aşama 3: FastAPI – Kendi API’n
Sunucuyu başlat:
```bash
python -m uvicorn api:app --reload
```

Tarayıcıdan:
- Swagger UI → http://127.0.0.1:8000/docs  
- Kitaplar → http://127.0.0.1:8000/books

### Endpoint’ler
| Yöntem | Yol              | Açıklama                                      | Gövde (JSON)             | Başarılı Yanıt |
|-------:|------------------|-----------------------------------------------|--------------------------|----------------|
| GET    | `/books`         | Kütüphanedeki tüm kitapları listeler          | —                        | 200, `[Book]`  |
| POST   | `/books`         | ISBN ile Open Library’den çekip ekler         | `{ "isbn": "..." }`      | 201, `Book`    |
| DELETE | `/books/{isbn}`  | Verilen ISBN’e sahip kitabı siler             | —                        | 200, `{detail}`|

**Book şeması**:
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884"
}
```

### cURL Örnekleri
```bash
# Ekle
curl -X POST http://127.0.0.1:8000/books   -H "Content-Type: application/json"   -d "{"isbn":"9780132350884"}"

# Listele
curl http://127.0.0.1:8000/books

# Sil
curl -X DELETE http://127.0.0.1:8000/books/9780132350884
```

---

## 🧪 Testler (pytest)
Tüm testleri çalıştır:
```bash
python -m pytest -q
```

Sık kullanılanlar:
```bash
python -m pytest -q test_library.py                 # sadece Aşama 1 temel testleri
python -m pytest -q -k add_book_by_isbn             # ada göre filtre
python -m pytest -q test_api_endpoints.py           # FastAPI endpoint testleri
```

> Testler, **ağa çıkmadan** `monkeypatch` ile HTTP çağrılarını sahteleyerek çalışır.  
> Endpoint testlerinde `Library._http` yardımcı metodu patch’lenir; böylece FastAPI’nin `TestClient`’ı etkilenmez.

---

## 🧱 Mimari & Kod Notları
- **`book.py`**: Basit veri sınıfı; `__str__`/`__repr__` ile okunaklı çıktı.  
- **`library.py`**:  
  - `add_book`, `remove_book`, `list_books`, `find_book`  
  - `_normalize_isbn` ile tutarlı ISBN kontrolü  
  - `_http()` → `httpx.Client(timeout, follow_redirects, User-Agent)`  
  - `_fetch_isbn_json` → `/isbn/{isbn}.json`  
  - `_fetch_author_name` → `/authors/{key}.json`  
  - `_fetch_from_search_api` → `/search.json?isbn=...` (fallback)  
  - `add_book_by_isbn` → tüm akışı yönetir, anlamlı hata mesajları döndürür.  
- **`api.py`**: FastAPI app + Pydantic modelleri (input/output), `GET/POST/DELETE` endpoint’leri, Swagger UI `/docs`

---

## 🧰 Sorun Giderme
- **`'venv' is not recognized`** → Sanal ortam aktif değil. Windows: `.env\Scriptsctivate`  
- **`ModuleNotFoundError: No module named 'httpx'/'fastapi'`** → `python -m pip install -r requirements.txt`  
- **`SyntaxError: '(' was never closed`** → `main.py` içindeki `print(...)` parantezlerini kontrol et.  
- **“Kitap bulunamadı”** → ISBN’i tire/boşluk olmadan gir; proje normalize ediyor. Kayıt `/isbn/...` dizininde yoksa `/search.json` fallback devreye girer.  
- **302/portal yönlendirmesi** → Kurumsal ağlarda görülebilir; proje `follow_redirects=True` ve içerik türü kontrolü yapar. Gerekirse farklı ağda deneyin (mobil hotspot vs).

---

## ✅ Teslim Notları
- Public GitHub repo (bonus: anlamlı commit mesajları)  
- `README.md` bu dosya  
- `requirements.txt` mevcut  
- Tüm Aşamalar için pytest testleri mevcut ve geçer durumda

