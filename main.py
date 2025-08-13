from book import Book
from library import Library
def main():
    library = Library()

    while True:
        print("\nKütüphane Yönetim Sistemi")
        print("1. Kitap Ekle")
        print("2. Kitap Sil")
        print("3. Kitapları Listele")
        print("4. Kitap Bul")
        print("5. Çıkış")

        choice = input("Seçiminizi yapın: ")

        if choice == '1':
            title = input("Kitap Başlığı: ")
            author = input("Yazar: ")
            isbn = input("ISBN: ")
            book = Book(title, author, isbn)
            library.add_book(book)
            print(f"{title} kitabı eklendi.")
        
        elif choice == '2':
            isbn = input("Silinecek kitabın ISBN'si: ")
            library.remove_book(isbn)
            print(f"{isbn} ISBN'li kitap silindi.")
        
        elif choice == '3':
            books = library.list_books()
            if books:
                for book in books:
                    print(f"{book.title} - {book.author} (ISBN: {book.isbn})")
            else:
                print("Kütüphanede kitap bulunmamaktadır.")
        
        elif choice == '4':
            isbn = input("Aranacak kitabın ISBN'si: ")
            book = library.find_book(isbn)
            if book:
                print(f"{book.title} - {book.author} (ISBN: {book.isbn}) bulundu.")
            else:
                print(f"{isbn} ISBN'li kitap bulunamadı.")
        
        elif choice == '5':
            print("Çıkılıyor...")
            break
        
        else:
            print("Geçersiz seçim, lütfen tekrar deneyin.")
if __name__ == "__main__":
    main()