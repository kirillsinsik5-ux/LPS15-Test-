"""
Мини-проект «Библиотека»
Контрольная работа по ООП, работе с файлами и обработке ошибок
"""

import json
import os
import csv
from datetime import datetime, date
from typing import List, Dict, Optional, Any


# ==================== ЧАСТЬ 1: КЛАССЫ ====================

class Book:
    """Класс, представляющий книгу."""
    
    def __init__(self, book_id: int, title: str, author: str, year: int, 
                 copies: int = 1, genre: str = ""):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre  # ЗАДАНИЕ 1: Добавлен жанр
        self.copies = copies
        self.available = copies
    
    def is_available(self) -> bool:
        """Проверяет, есть ли хотя бы один экземпляр."""
        return self.available > 0
    
    def borrow(self) -> bool:
        """Выдает один экземпляр книги."""
        if self.is_available():
            self.available -= 1
            return True
        return False
    
    def return_book(self) -> bool:
        """Возвращает один экземпляр книги."""
        if self.available < self.copies:
            self.available += 1
            return True
        return False
    
    def to_dict(self) -> dict:
        """Преобразует книгу в словарь для JSON."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "copies": self.copies,
            "available": self.available
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Создает книгу из словаря."""
        book = cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["year"],
            data.get("copies", 1),
            data.get("genre", "")
        )
        book.available = data.get("available", book.copies)
        return book
    
    def __str__(self) -> str:
        status = "✓" if self.is_available() else "✗"
        genre_info = f" [{self.genre}]" if self.genre else ""
        return f"[{status}] {self.book_id}: {self.title} — {self.author} ({self.year}){genre_info} | {self.available}/{self.copies}"


class Person:
    """Базовый класс для человека."""
    
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone
    
    def get_contact_info(self) -> str:
        return f"{self.name} | email: {self.email} | тел: {self.phone}"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }


class Reader(Person):
    """Класс читателя (наследник Person)."""
    
    def __init__(self, reader_id: int, name: str, email: str, phone: str):
        super().__init__(name, email, phone)
        self.reader_id = reader_id
        self.borrowed_books = []  # Список ID книг на руках
        self.history = []  # История операций
        self.borrow_dates = {}  # ЗАДАНИЕ 2: {book_id: дата_выдачи}
    
    def borrow_book(self, book_id: int) -> None:
        """Добавляет книгу в список взятых."""
        self.borrowed_books.append(book_id)
        self.borrow_dates[book_id] = date.today()  # ЗАДАНИЕ 2
        self.history.append(f"Взял книгу {book_id} ({date.today()})")
    
    def return_book(self, book_id: int) -> bool:
        """Удаляет книгу из списка взятых."""
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
            # ЗАДАНИЕ 2: Подсчет дней
            if book_id in self.borrow_dates:
                borrow_date = self.borrow_dates[book_id]
                days_borrowed = (date.today() - borrow_date).days
                self.history.append(f"Вернул книгу {book_id} (было на руках: {days_borrowed} дней)")
                del self.borrow_dates[book_id]
            else:
                self.history.append(f"Вернул книгу {book_id}")
            return True
        return False
    
    def has_book(self, book_id: int) -> bool:
        """Проверяет, есть ли книга у читателя."""
        return book_id in self.borrowed_books
    
    def get_borrowed_count(self) -> int:
        return len(self.borrowed_books)
    
    def get_borrow_days(self, book_id: int) -> Optional[int]:
        """ЗАДАНИЕ 2: Возвращает количество дней, сколько книга у читателя."""
        if book_id in self.borrow_dates:
            return (date.today() - self.borrow_dates[book_id]).days
        return None
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["reader_id"] = self.reader_id
        data["borrowed_books"] = self.borrowed_books
        data["history"] = self.history
        # ЗАДАНИЕ 2: Сохраняем даты выдачи
        data["borrow_dates"] = {str(k): v.isoformat() for k, v in self.borrow_dates.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reader':
        reader = cls(
            data["reader_id"],
            data["name"],
            data["email"],
            data["phone"]
        )
        reader.borrowed_books = data.get("borrowed_books", [])
        reader.history = data.get("history", [])
        # ЗАДАНИЕ 2: Восстанавливаем даты выдачи
        borrow_dates = data.get("borrow_dates", {})
        reader.borrow_dates = {int(k): datetime.fromisoformat(v).date() 
                                for k, v in borrow_dates.items()}
        return reader
    
    def __str__(self) -> str:
        return f"[{self.reader_id}] {self.name} — на руках: {len(self.borrowed_books)} книг"


class Logger:
    """ЗАДАНИЕ 4: Класс для логирования действий."""
    
    def __init__(self, log_file: str = "library.log"):
        self.log_file = log_file
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Создает папку для логов если её нет."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log(self, action: str, details: str = "", level: str = "INFO"):
        """Записывает действие в лог-файл."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {action}"
        if details:
            log_entry += f": {details}"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Ошибка записи лога: {e}")
    
    def info(self, action: str, details: str = ""):
        self.log(action, details, "INFO")
    
    def error(self, action: str, details: str = ""):
        self.log(action, details, "ERROR")
    
    def warning(self, action: str, details: str = ""):
        self.log(action, details, "WARNING")


class Library:
    """Класс, управляющий библиотекой."""
    
    def __init__(self, name: str, books_file: str = "data/books.json",
                 readers_file: str = "data/readers.json"):
        self.name = name
        self.books_file = books_file
        self.readers_file = readers_file
        self.books: Dict[int, Book] = {}
        self.readers: Dict[int, Reader] = {}
        self._next_book_id = 1
        self._next_reader_id = 1
        
        # ЗАДАНИЕ 4: Инициализация логгера
        self.logger = Logger("logs/library.log")
        
        # Создание папок
        self._ensure_directories()
        self.load_data()
    
    def _ensure_directories(self):
        """Создает необходимые папки."""
        for path in ["data", "reports", "logs"]:
            if not os.path.exists(path):
                os.makedirs(path)
    
    # ========== ПОИСК ==========
    
    def find_book_by_id(self, book_id: int) -> Optional[Book]:
        return self.books.get(book_id)
    
    def find_reader_by_id(self, reader_id: int) -> Optional[Reader]:
        return self.readers.get(reader_id)
    
    def search_books(self, query: str) -> List[Book]:
        """Ищет книги по названию, автору или жанру (частичное совпадение)."""
        query = query.lower()
        results = []
        for book in self.books.values():
            if (query in book.title.lower() or 
                query in book.author.lower() or
                query in book.genre.lower()):  # ЗАДАНИЕ 1: поиск по жанру
                results.append(book)
        return results
    
    def search_by_genre(self, genre: str) -> List[Book]:
        """ЗАДАНИЕ 1: Поиск книг по жанру."""
        genre = genre.lower()
        return [book for book in self.books.values() 
                if genre in book.genre.lower()]
    
    def search_readers(self, query: str) -> List[Reader]:
        """Ищет читателей по имени."""
        query = query.lower()
        return [r for r in self.readers.values() if query in r.name.lower()]
    
    # ========== ДОБАВЛЕНИЕ ==========
    
    def add_book(self, title: str, author: str, year: int, 
                 copies: int = 1, genre: str = "") -> Book:
        """Добавляет новую книгу."""
        book = Book(self._next_book_id, title, author, year, copies, genre)
        self.books[self._next_book_id] = book
        self._next_book_id += 1
        self.save_data()
        self.logger.info("Добавлена книга", f"'{title}' (ID: {book.book_id})")
        return book
    
    def add_reader(self, name: str, email: str, phone: str) -> Reader:
        """Добавляет нового читателя."""
        reader = Reader(self._next_reader_id, name, email, phone)
        self.readers[self._next_reader_id] = reader
        self._next_reader_id += 1
        self.save_data()
        self.logger.info("Добавлен читатель", f"{name} (ID: {reader.reader_id})")
        return reader
    
    # ========== ВЫДАЧА И ВОЗВРАТ ==========
    
    def borrow_book(self, reader_id: int, book_id: int) -> str:
        """Выдает книгу читателю."""
        reader = self.find_reader_by_id(reader_id)
        if not reader:
            self.logger.error("Выдача книги", f"Читатель {reader_id} не найден")
            return "Читатель не найден"
        
        book = self.find_book_by_id(book_id)
        if not book:
            self.logger.error("Выдача книги", f"Книга {book_id} не найдена")
            return "Книга не найдена"
        
        if not book.is_available():
            self.logger.warning("Выдача книги", f"Нет экземпляров '{book.title}'")
            return "Нет доступных экземпляров"
        
        reader.borrow_book(book_id)
        book.borrow()
        self.save_data()
        
        msg = f"Книга '{book.title}' выдана {reader.name}"
        self.logger.info("Выдача книги", msg)
        return msg
    
    def return_book(self, reader_id: int, book_id: int) -> str:
        """Возвращает книгу от читателя."""
        reader = self.find_reader_by_id(reader_id)
        if not reader:
            self.logger.error("Возврат книги", f"Читатель {reader_id} не найден")
            return "Читатель не найден"
        
        book = self.find_book_by_id(book_id)
        if not book:
            self.logger.error("Возврат книги", f"Книга {book_id} не найдена")
            return "Книга не найдена"
        
        if not reader.has_book(book_id):
            self.logger.warning("Возврат книги", f"У читателя {reader.name} нет книги {book_id}")
            return "У читателя нет этой книги"
        
        days_borrowed = reader.get_borrow_days(book_id)  # ЗАДАНИЕ 2
        reader.return_book(book_id)
        book.return_book()
        self.save_data()
        
        msg = f"Книга '{book.title}' возвращена"
        if days_borrowed:
            msg += f" (была на руках {days_borrowed} дней)"
        self.logger.info("Возврат книги", msg)
        return msg
    
    # ========== ОТЧЕТЫ ==========
    
    def get_all_books(self) -> List[Book]:
        return list(self.books.values())
    
    def get_all_readers(self) -> List[Reader]:
        return list(self.readers.values())
    
    def get_available_books(self) -> List[Book]:
        return [b for b in self.books.values() if b.is_available()]
    
    def get_borrowed_books(self) -> List[dict]:
        borrowed = []
        for reader in self.readers.values():
            for book_id in reader.borrowed_books:
                book = self.find_book_by_id(book_id)
                if book:
                    days = reader.get_borrow_days(book_id)  # ЗАДАНИЕ 2
                    borrowed.append({
                        "reader": reader.name,
                        "reader_id": reader.reader_id,
                        "book": book.title,
                        "book_id": book_id,
                        "borrow_date": reader.borrow_dates.get(book_id),
                        "days_borrowed": days
                    })
        return borrowed
    
    def get_reader_debtors(self) -> List[Reader]:
        """Читатели, у которых больше 3 книг на руках."""
        return [r for r in self.readers.values() if r.get_borrowed_count() > 3]
    
    def get_statistics(self) -> dict:
        return {
            "total_books": len(self.books),
            "total_readers": len(self.readers),
            "available_books": len(self.get_available_books()),
            "borrowed_books": len(self.get_borrowed_books()),
            "debtors": len(self.get_reader_debtors())
        }
    
    # ЗАДАНИЕ 3: Экспорт в CSV
    
    def export_books_to_csv(self, filename: str = "reports/books_report.csv") -> str:
        """Экспортирует список книг в CSV."""
        self._ensure_directories()
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Название", "Автор", "Год", "Жанр", "Всего", "Доступно", "Статус"])
            
            for book in self.books.values():
                writer.writerow([
                    book.book_id,
                    book.title,
                    book.author,
                    book.year,
                    book.genre,
                    book.copies,
                    book.available,
                    "Доступна" if book.is_available() else "Все на руках"
                ])
        
        self.logger.info("Экспорт CSV", f"Книги экспортированы в {filename}")
        return filename
    
    def export_readers_to_csv(self, filename: str = "reports/readers_report.csv") -> str:
        """Экспортирует список читателей в CSV."""
        self._ensure_directories()
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "ФИО", "Email", "Телефон", "Книг на руках", "История операций"])
            
            for reader in self.readers.values():
                writer.writerow([
                    reader.reader_id,
                    reader.name,
                    reader.email,
                    reader.phone,
                    reader.get_borrowed_count(),
                    "; ".join(reader.history[-5:]) if reader.history else "Нет операций"
                ])
        
        self.logger.info("Экспорт CSV", f"Читатели экспортированы в {filename}")
        return filename
    
    def export_borrowed_to_csv(self, filename: str = "reports/borrowed_report.csv") -> str:
        """ЗАДАНИЕ 3: Экспорт книг на руках в CSV."""
        self._ensure_directories()
        borrowed = self.get_borrowed_books()
        
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID читателя", "Читатель", "ID книги", "Книга", "Дата выдачи", "Дней на руках"])
            
            for item in borrowed:
                writer.writerow([
                    item["reader_id"],
                    item["reader"],
                    item["book_id"],
                    item["book"],
                    item["borrow_date"].isoformat() if item["borrow_date"] else "Неизвестно",
                    item["days_borrowed"] if item["days_borrowed"] else 0
                ])
        
        self.logger.info("Экспорт CSV", f"Книги на руках экспортированы в {filename}")
        return filename
    
    # ========== РАБОТА С ФАЙЛАМИ ==========
    
    def save_data(self):
        """Сохраняет данные в JSON файлы."""
        # Сохраняем книги
        books_data = [book.to_dict() for book in self.books.values()]
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, ensure_ascii=False, indent=4)
        
        # Сохраняем читателей
        readers_data = [reader.to_dict() for reader in self.readers.values()]
        with open(self.readers_file, 'w', encoding='utf-8') as f:
            json.dump(readers_data, f, ensure_ascii=False, indent=4)
        
        self.logger.info("Сохранение данных", "Данные сохранены в JSON")
    
    def load_data(self):
        """Загружает данные из JSON файлов."""
        # Загружаем книги
        if os.path.exists(self.books_file):
            try:
                with open(self.books_file, 'r', encoding='utf-8') as f:
                    books_data = json.load(f)
                max_id = 0
                for data in books_data:
                    book = Book.from_dict(data)
                    self.books[book.book_id] = book
                    max_id = max(max_id, book.book_id)
                self._next_book_id = max_id + 1
                self.logger.info("Загрузка данных", f"Загружено {len(books_data)} книг")
            except Exception as e:
                self.logger.error("Загрузка книг", str(e))
        
        # Загружаем читателей
        if os.path.exists(self.readers_file):
            try:
                with open(self.readers_file, 'r', encoding='utf-8') as f:
                    readers_data = json.load(f)
                max_id = 0
                for data in readers_data:
                    reader = Reader.from_dict(data)
                    self.readers[reader.reader_id] = reader
                    max_id = max(max_id, reader.reader_id)
                self._next_reader_id = max_id + 1
                self.logger.info("Загрузка данных", f"Загружено {len(readers_data)} читателей")
            except Exception as e:
                self.logger.error("Загрузка читателей", str(e))


# ==================== ЧАСТЬ 2: КОНСОЛЬНЫЙ ИНТЕРФЕЙС ====================

class LibraryApp:
    """Консольное приложение для управления библиотекой."""
    
    def __init__(self):
        self.lib = Library("Городская библиотека")
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        print("\n" + "=" * 60)
        print(f"📚 {title}")
        print("=" * 60)
    
    def print_menu(self):
        print("\n" + "-" * 40)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 40)
        print("📖 УПРАВЛЕНИЕ КНИГАМИ:")
        print(" 1. Добавить книгу")
        print(" 2. Показать все книги")
        print(" 3. Поиск книг")
        print(" 4. Поиск по жанру")  # ЗАДАНИЕ 1
        print(" 5. Показать доступные книги")
        print("\n👥 УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ:")
        print(" 6. Добавить читателя")
        print(" 7. Показать всех читателей")
        print(" 8. Поиск читателей")
        print("\n🔄 ОПЕРАЦИИ:")
        print(" 9. Выдать книгу")
        print(" 10. Вернуть книгу")
        print(" 11. Книги на руках (с датами)")  # ЗАДАНИЕ 2
        print("\n📊 ОТЧЕТЫ:")
        print(" 12. Статистика")
        print(" 13. Должники (>3 книг)")
        print(" 14. Экспорт в CSV")  # ЗАДАНИЕ 3
        print("\n💾 ДРУГОЕ:")
        print(" 0. Выход")
        print("-" * 40)
    
    # ========== КНИГИ ==========
    
    def add_book_menu(self):
        self.print_header("ДОБАВЛЕНИЕ КНИГИ")
        title = input("Название: ").strip()
        if not title:
            print("❌ Название не может быть пустым")
            return
        
        author = input("Автор: ").strip()
        if not author:
            print("❌ Автор не может быть пустым")
            return
        
        try:
            year = int(input("Год издания: "))
        except ValueError:
            print("❌ Год должен быть числом")
            return
        
        genre = input("Жанр (опционально): ").strip()  # ЗАДАНИЕ 1
        
        try:
            copies = int(input("Количество экземпляров (по умолчанию 1): ") or "1")
        except ValueError:
            copies = 1
        
        book = self.lib.add_book(title, author, year, copies, genre)
        print(f"\n✅ Книга добавлена: {book}")
    
    def show_books_menu(self):
        self.print_header("ВСЕ КНИГИ")
        books = self.lib.get_all_books()
        if not books:
            print("📭 В библиотеке нет книг")
            return
        for book in books:
            print(book)
    
    def search_books_menu(self):
        self.print_header("ПОИСК КНИГ")
        query = input("Введите название, автора или жанр: ").strip()
        if not query:
            print("❌ Введите поисковый запрос")
            return
        results = self.lib.search_books(query)
        print(f"\n📖 Найдено книг: {len(results)}")
        for book in results:
            print(book)
    
    def search_by_genre_menu(self):  # ЗАДАНИЕ 1
        self.print_header("ПОИСК ПО ЖАНРУ")
        genre = input("Введите жанр: ").strip()
        if not genre:
            print("❌ Введите жанр")
            return
        results = self.lib.search_by_genre(genre)
        print(f"\n📖 Найдено книг в жанре '{genre}': {len(results)}")
        for book in results:
            print(book)
    
    def show_available_books_menu(self):
        self.print_header("ДОСТУПНЫЕ КНИГИ")
        books = self.lib.get_available_books()
        if not books:
            print("📭 Нет доступных книг")
            return
        for book in books:
            print(book)
    
    # ========== ЧИТАТЕЛИ ==========
    
    def add_reader_menu(self):
        self.print_header("ДОБАВЛЕНИЕ ЧИТАТЕЛЯ")
        name = input("ФИО: ").strip()
        if not name:
            print("❌ ФИО не может быть пустым")
            return
        email = input("Email: ").strip()
        phone = input("Телефон: ").strip()
        reader = self.lib.add_reader(name, email, phone)
        print(f"\n✅ Читатель добавлен: {reader}")
    
    def show_readers_menu(self):
        self.print_header("ВСЕ ЧИТАТЕЛИ")
        readers = self.lib.get_all_readers()
        if not readers:
            print("👥 Нет читателей")
            return
        for reader in readers:
            print(reader)
    
    def search_readers_menu(self):
        self.print_header("ПОИСК ЧИТАТЕЛЕЙ")
        query = input("Введите имя читателя: ").strip()
        if not query:
            print("❌ Введите поисковый запрос")
            return
        results = self.lib.search_readers(query)
        print(f"\n👥 Найдено читателей: {len(results)}")
        for reader in results:
            print(reader)
    
    # ========== ОПЕРАЦИИ ==========
    
    def borrow_book_menu(self):
        self.print_header("ВЫДАЧА КНИГИ")
        try:
            reader_id = int(input("ID читателя: "))
            book_id = int(input("ID книги: "))
        except ValueError:
            print("❌ ID должны быть числами")
            return
        result = self.lib.borrow_book(reader_id, book_id)
        print(f"\n{result}")
    
    def return_book_menu(self):
        self.print_header("ВОЗВРАТ КНИГИ")
        try:
            reader_id = int(input("ID читателя: "))
            book_id = int(input("ID книги: "))
        except ValueError:
            print("❌ ID должны быть числами")
            return
        result = self.lib.return_book(reader_id, book_id)
        print(f"\n{result}")
    
    def show_borrowed_books_menu(self):
        """ЗАДАНИЕ 2: Показывает книги на руках с датами выдачи."""
        self.print_header("КНИГИ НА РУКАХ")
        borrowed = self.lib.get_borrowed_books()
        if not borrowed:
            print("📭 Нет книг на руках")
            return
        
        print("\n📖 КНИГИ В ПРОКАТЕ:")
        print("-" * 60)
        for item in borrowed:
            borrow_date_str = item["borrow_date"].strftime("%d.%m.%Y") if item["borrow_date"] else "Неизвестно"
            days = item["days_borrowed"] if item["days_borrowed"] else 0
            print(f"📖 '{item['book']}' — {item['reader']}")
            print(f"   📅 Выдана: {borrow_date_str} | На руках: {days} дней")
        print("-" * 60)
    
    # ========== ОТЧЕТЫ ==========
    
    def show_statistics_menu(self):
        self.print_header("СТАТИСТИКА БИБЛИОТЕКИ")
        stats = self.lib.get_statistics()
        print(f"📚 Всего книг: {stats['total_books']}")
        print(f"📖 Доступно: {stats['available_books']}")
        print(f"📕 На руках: {stats['borrowed_books']}")
        print(f"👥 Читателей: {stats['total_readers']}")
        print(f"⚠️ Должников (>3 книг): {stats['debtors']}")
        if stats['total_books'] > 0:
            percent = (stats['available_books'] / stats['total_books']) * 100
            print(f"📊 Доступность книг: {percent:.1f}%")
    
    def show_debtors_menu(self):
        self.print_header("ДОЛЖНИКИ (>3 КНИГ НА РУКАХ)")
        debtors = self.lib.get_reader_debtors()
        if not debtors:
            print("✅ Нет должников")
            return
        for reader in debtors:
            print(f"⚠️ {reader} — книг на руках: {reader.get_borrowed_count()}")
    
    def export_reports_menu(self):  # ЗАДАНИЕ 3
        self.print_header("ЭКСПОРТ ОТЧЕТОВ В CSV")
        print("1. Экспортировать все книги")
        print("2. Экспортировать всех читателей")
        print("3. Экспортировать книги на руках")
        print("0. Назад")
        
        choice = input("\nВыберите тип отчета: ").strip()
        
        try:
            if choice == "1":
                filename = self.lib.export_books_to_csv()
                print(f"\n✅ Отчет по книгам сохранен в: {filename}")
            elif choice == "2":
                filename = self.lib.export_readers_to_csv()
                print(f"\n✅ Отчет по читателям сохранен в: {filename}")
            elif choice == "3":
                filename = self.lib.export_borrowed_to_csv()
                print(f"\n✅ Отчет по выданным книгам сохранен в: {filename}")
            elif choice == "0":
                return
            else:
                print("❌ Неверный выбор!")
        except Exception as e:
            print(f"❌ Ошибка при экспорте: {e}")
    
    # ========== ГЛАВНЫЙ ЦИКЛ ==========
    
    def run(self):
        self.clear_screen()
        print("=" * 60)
        print("🏫 ДОБРО ПОЖАЛОВАТЬ В БИБЛИОТЕКУ!")
        print(f"   {self.lib.name}")
        print("=" * 60)
        print("\n📝 Все действия логируются в папке logs/")
        print("📊 Отчеты сохраняются в папке reports/")
        
        while True:
            self.print_menu()
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "0":
                print("\n💾 Сохранение данных...")
                self.lib.save_data()
                print("👋 До свидания!")
                break
            
            # Книги
            elif choice == "1":
                self.add_book_menu()
            elif choice == "2":
                self.show_books_menu()
            elif choice == "3":
                self.search_books_menu()
            elif choice == "4":  # ЗАДАНИЕ 1
                self.search_by_genre_menu()
            elif choice == "5":
                self.show_available_books_menu()
            
            # Читатели
            elif choice == "6":
                self.add_reader_menu()
            elif choice == "7":
                self.show_readers_menu()
            elif choice == "8":
                self.search_readers_menu()
            
            # Операции
            elif choice == "9":
                self.borrow_book_menu()
            elif choice == "10":
                self.return_book_menu()
            elif choice == "11":  # ЗАДАНИЕ 2
                self.show_borrowed_books_menu()
            
            # Отчеты
            elif choice == "12":
                self.show_statistics_menu()
            elif choice == "13":
                self.show_debtors_menu()
            elif choice == "14":  # ЗАДАНИЕ 3
                self.export_reports_menu()
            
            else:
                print("❌ Неверный выбор!")
            
            input("\n📌 Нажмите Enter для продолжения...")


# Запуск приложения
if __name__ == "__main__":
    app = LibraryApp()
    app.run()