#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
"""

import sys
import logging
from datetime import date
from db.Class_DB_refactored import DB

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db/db_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def drop_and_recreate_schema(db):
    """Удаляет существующую схему и создает новую"""
    
    try:
        print("🗑️ Удаление существующей схемы...")
        
        # Удаляем все таблицы в правильном порядке (с учетом внешних ключей)
        tables_to_drop = ["Issued_Books", "Readers", "Books"]
        
        for table in tables_to_drop:
            try:
                from sqlalchemy import text
                with db.engine.begin() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE"))
                print(f"  ✅ Удалена таблица {table}")
            except Exception as e:
                print(f"  ⚠️ Предупреждение при удалении таблицы {table}: {e}")
        
        # Удаляем ENUM типы если они есть
        try:
            from sqlalchemy import text
            with db.engine.begin() as conn:
                conn.execute(text("DROP TYPE IF EXISTS book_genre CASCADE"))
                conn.execute(text("DROP TYPE IF EXISTS discount_category CASCADE"))
                conn.execute(text("DROP TYPE IF EXISTS damage_type CASCADE"))
            print("  ✅ Удалены ENUM типы")
        except Exception as e:
            print(f"  ⚠️ Предупреждение при удалении ENUM типов: {e}")
        
        print("✅ Схема удалена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при удалении схемы: {e}")
        return False

def create_test_data():
    """Создает тестовые данные для библиотеки"""
    
    # Подключение к базе данных
    db = DB(
        host="localhost",
        port=5432,
        dbname="library_db",
        user="postgres",
        password="DhhkKLNM"
    )
    
    try:
        # Подключаемся к базе данных
        if not db.connect():
            print("❌ Не удалось подключиться к базе данных")
            return False
        
        print("✅ Подключение к базе данных успешно")
        
        # Сначала удаляем старую схему
        print("🗑️ Удаление старой схемы...")
        if not drop_and_recreate_schema(db):
            print("❌ Не удалось удалить старую схему")
            return False
        
        # Создаем новую схему
        print("📚 Создание новой схемы базы данных...")
        if not db.create_schema():
            print("❌ Не удалось создать новую схему")
            return False
        
        # Заполняем таблицу Books
        print("📖 Заполнение таблицы Books...")
        books_data = [
            {
                "title": "Война и мир",
                "authors": ["Лев Толстой"],
                "genre": "Роман",
                "deposit_amount": 500.00,
                "daily_rental_rate": 50.00
            },
            {
                "title": "Преступление и наказание",
                "authors": ["Фёдор Достоевский"],
                "genre": "Роман",
                "deposit_amount": 450.00,
                "daily_rental_rate": 45.00
            },
            {
                "title": "Евгений Онегин",
                "authors": ["Александр Пушкин"],
                "genre": "Поэзия",
                "deposit_amount": 300.00,
                "daily_rental_rate": 30.00
            },
            {
                "title": "Мастер и Маргарита",
                "authors": ["Михаил Булгаков"],
                "genre": "Роман",
                "deposit_amount": 550.00,
                "daily_rental_rate": 55.00
            },
            {
                "title": "Анна Каренина",
                "authors": ["Лев Толстой"],
                "genre": "Роман",
                "deposit_amount": 480.00,
                "daily_rental_rate": 48.00
            },
            {
                "title": "Отцы и дети",
                "authors": ["Иван Тургенев"],
                "genre": "Роман",
                "deposit_amount": 400.00,
                "daily_rental_rate": 40.00
            },
            {
                "title": "Герой нашего времени",
                "authors": ["Михаил Лермонтов"],
                "genre": "Роман",
                "deposit_amount": 350.00,
                "daily_rental_rate": 35.00
            },
            {
                "title": "Мёртвые души",
                "authors": ["Николай Гоголь"],
                "genre": "Роман",
                "deposit_amount": 420.00,
                "daily_rental_rate": 42.00
            },
            {
                "title": "Капитанская дочка",
                "authors": ["Александр Пушкин"],
                "genre": "Повесть",
                "deposit_amount": 280.00,
                "daily_rental_rate": 28.00
            },
            {
                "title": "Обломов",
                "authors": ["Иван Гончаров"],
                "genre": "Роман",
                "deposit_amount": 380.00,
                "daily_rental_rate": 38.00
            }
        ]
        
        for book in books_data:
            result, error = db.insert_data("Books", book)
            if result:
                print(f"  ✅ Добавлена книга: {book['title']}")
            else:
                print(f"  ❌ Ошибка добавления: {book['title']} - {error}")
        
        # Заполняем таблицу Readers
        print("\n👥 Заполнение таблицы Readers...")
        readers_data = [
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "middle_name": "Иванович",
                "address": "ул. Ленина, д. 1, кв. 1",
                "phone": "+7-900-123-45-67",
                "discount_category": "Обычный",
                "discount_percent": 0
            },
            {
                "last_name": "Петров",
                "first_name": "Пётр",
                "middle_name": "Петрович",
                "address": "ул. Пушкина, д. 10, кв. 5",
                "phone": "+7-900-234-56-78",
                "discount_category": "Студент",
                "discount_percent": 10
            },
            {
                "last_name": "Сидоров",
                "first_name": "Сидор",
                "middle_name": "Сидорович",
                "address": "ул. Гагарина, д. 25, кв. 12",
                "phone": "+7-900-345-67-89",
                "discount_category": "Пенсионер",
                "discount_percent": 15
            },
            {
                "last_name": "Козлова",
                "first_name": "Анна",
                "middle_name": "Сергеевна",
                "address": "ул. Мира, д. 5, кв. 3",
                "phone": "+7-900-456-78-90",
                "discount_category": "Член_клуба",
                "discount_percent": 20
            },
            {
                "last_name": "Смирнов",
                "first_name": "Алексей",
                "middle_name": "Александрович",
                "address": "ул. Советская, д. 15, кв. 8",
                "phone": "+7-900-567-89-01",
                "discount_category": "Ветеран",
                "discount_percent": 25
            },
            {
                "last_name": "Новикова",
                "first_name": "Елена",
                "middle_name": "Владимировна",
                "address": "ул. Центральная, д. 30, кв. 15",
                "phone": "+7-900-678-90-12",
                "discount_category": "Студент",
                "discount_percent": 10
            },
            {
                "last_name": "Морозов",
                "first_name": "Дмитрий",
                "middle_name": "Игоревич",
                "address": "ул. Садовая, д. 8, кв. 4",
                "phone": "+7-900-789-01-23",
                "discount_category": "Обычный",
                "discount_percent": 0
            },
            {
                "last_name": "Волкова",
                "first_name": "Ольга",
                "middle_name": "Николаевна",
                "address": "ул. Парковая, д. 12, кв. 7",
                "phone": "+7-900-890-12-34",
                "discount_category": "Пенсионер",
                "discount_percent": 15
            }
        ]
        
        for reader in readers_data:
            result, error = db.insert_data("Readers", reader)
            if result:
                print(f"  ✅ Добавлен читатель: {reader['last_name']} {reader['first_name']}")
            else:
                print(f"  ❌ Ошибка добавления: {reader['last_name']} {reader['first_name']} - {error}")
        
        # Заполняем таблицу Issued_Books
        print("\n📚 Заполнение таблицы Issued_Books...")
        issued_books_data = [
            {
                "book_id": 1,
                "reader_id": 1,
                "issue_date": date(2024, 1, 15),
                "expected_return_date": date(2024, 2, 15),
                "actual_return_date": date(2024, 2, 10),
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": 50.00,
                "paid": True,
                "actual_rental_days": 26
            },
            {
                "book_id": 2,
                "reader_id": 2,
                "issue_date": date(2024, 1, 20),
                "expected_return_date": date(2024, 2, 20),
                "actual_return_date": None,
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": None,
                "paid": False,
                "actual_rental_days": None
            },
            {
                "book_id": 3,
                "reader_id": 3,
                "issue_date": date(2024, 1, 25),
                "expected_return_date": date(2024, 2, 25),
                "actual_return_date": date(2024, 2, 20),
                "damage_type": "Порвана_обложка",
                "damage_fine": 50.00,
                "final_rental_cost": 75.00,
                "paid": True,
                "actual_rental_days": 26
            },
            {
                "book_id": 4,
                "reader_id": 4,
                "issue_date": date(2024, 2, 1),
                "expected_return_date": date(2024, 3, 1),
                "actual_return_date": None,
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": None,
                "paid": False,
                "actual_rental_days": None
            },
            {
                "book_id": 5,
                "reader_id": 5,
                "issue_date": date(2024, 2, 5),
                "expected_return_date": date(2024, 3, 5),
                "actual_return_date": date(2024, 3, 1),
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": 40.00,
                "paid": True,
                "actual_rental_days": 25
            },
            {
                "book_id": 6,
                "reader_id": 6,
                "issue_date": date(2024, 2, 10),
                "expected_return_date": date(2024, 3, 10),
                "actual_return_date": date(2024, 3, 5),
                "damage_type": "Запачкана",
                "damage_fine": 30.00,
                "final_rental_cost": 55.00,
                "paid": True,
                "actual_rental_days": 24
            },
            {
                "book_id": 7,
                "reader_id": 7,
                "issue_date": date(2024, 2, 15),
                "expected_return_date": date(2024, 3, 15),
                "actual_return_date": None,
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": None,
                "paid": False,
                "actual_rental_days": None
            },
            {
                "book_id": 8,
                "reader_id": 8,
                "issue_date": date(2024, 2, 20),
                "expected_return_date": date(2024, 3, 20),
                "actual_return_date": date(2024, 3, 18),
                "damage_type": "Нет",
                "damage_fine": 0.00,
                "final_rental_cost": 35.00,
                "paid": True,
                "actual_rental_days": 27
            }
        ]
        
        for issued_book in issued_books_data:
            result, error = db.insert_data("Issued_Books", issued_book)
            if result:
                print(f"  ✅ Добавлена выдача: книга ID {issued_book['book_id']}, читатель ID {issued_book['reader_id']}")
            else:
                print(f"  ❌ Ошибка добавления выдачи: книга ID {issued_book['book_id']} - {error}")
        
        print("\n✅ Тестовые данные успешно добавлены!")
        print("\n📊 Статистика:")
        
        # Получаем статистику
        books_count = len(db.get_table_data("Books"))
        readers_count = len(db.get_table_data("Readers"))
        issued_count = len(db.get_table_data("Issued_Books"))
        
        print(f"  📚 Книг: {books_count}")
        print(f"  👥 Читателей: {readers_count}")
        print(f"  📖 Выдач: {issued_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении тестовыми данными: {e}")
        logging.error(f"Ошибка заполнения тестовыми данными: {e}")
        return False
    
    finally:
        # Отключаемся от базы данных
        db.disconnect()
        print("🔌 Соединение с базой данных закрыто")


def main():
    """Главная функция - удаляет схему, создает новую и заполняет данными"""
    print("🧪 Тестирование базы данных библиотеки")
    print("=" * 50)
    print("🔄 Полное пересоздание схемы и заполнение данными...")
    
    # Сразу выполняем полное пересоздание и заполнение
    create_test_data()
    
    print("\n✅ Готово! Схема пересоздана и заполнена тестовыми данными.")

if __name__ == "__main__":
    main()