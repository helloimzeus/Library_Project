from library import Library

def main():
    library = Library()

    while True:
        print("\n--- Kütüphane Menüsü ---")
        print("1. Kitap Ekle (ISBN ile)")
        print("2. Kitap Sil")
        print("3. Kitapları Listele")
        print("4. Kitap Ara")
        print("5. Çıkış")

        choice = input("Seçiminiz: ").strip()

        if choice == "1":
            isbn = input("ISBN: ").strip()
            ok, msg = library.add_book_by_isbn(isbn)
            print(msg)

        elif choice == "2":
            isbn = input("Silinecek kitabın ISBN'i: ").strip()
            removed = library.remove_book(isbn)
            print("Silindi." if removed else "Bulunamadı.")

        elif choice == "3":
            books = library.list_books()
            if not books:
                print("Kütüphane boş.")
            else:
                for b in books:
                    print(b)

        elif choice == "4":
            isbn = input("Aranacak kitabın ISBN'i: ").strip()
            book = library.find_book(isbn)
            print(book if book else "Kitap bulunamadı.")

        elif choice == "5":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    main()
