from datetime import date
from Class_DB import DB

def fill_test_data(db):
    """
    Заполняет базу данных тестовыми данными
    """
    # Проверяем подключение к БД
    if not db.is_connected():
        print("Нет подключения к БД")
        return False

    # Создаем схему (таблицы) если они не существуют
    if not db.create_schema():
        print("Ошибка создания схемы БД")
        return False

    # Данные для таблицы Books
    books_data = [
        {
            "title": "Мастер и Маргарита",
            "authors": ["Михаил Булгаков"],
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
            "title": "1984",
            "authors": ["Джордж Оруэлл"],
            "genre": "Научная фантастика",
            "deposit_amount": 400.00,
            "daily_rental_rate": 40.00
        },
        {
            "title": "Гарри Поттер и философский камень",
            "authors": ["Джоан Роулинг"],
            "genre": "Фэнтези",
            "deposit_amount": 600.00,
            "daily_rental_rate": 60.00
        },
        {
            "title": "Краткая история времени",
            "authors": ["Стивен Хокинг"],
            "genre": "Научно-популярное",
            "deposit_amount": 350.00,
            "daily_rental_rate": 35.00
        },
        {
            "title": "Три товарища",
            "authors": ["Эрих Мария Ремарк"],
            "genre": "Роман",
            "deposit_amount": 480.00,
            "daily_rental_rate": 48.00
        },
        {
            "title": "Маленький принц",
            "authors": ["Антуан де Сент-Экзюпери"],
            "genre": "Повесть",
            "deposit_amount": 300.00,
            "daily_rental_rate": 30.00
        },
        {
            "title": "Убийство в Восточном экспрессе",
            "authors": ["Агата Кристи"],
            "genre": "Детектив",
            "deposit_amount": 420.00,
            "daily_rental_rate": 42.00
        },
        {
            "title": "Властелин колец",
            "authors": ["Джон Рональд Руэл Толкин"],
            "genre": "Фэнтези",
            "deposit_amount": 650.00,
            "daily_rental_rate": 65.00
        },
        {
            "title": "Психология влияния",
            "authors": ["Роберт Чалдини"],
            "genre": "Психология",
            "deposit_amount": 380.00,
            "daily_rental_rate": 38.00
        }
    ]

    # Данные для таблицы Readers
    readers_data = [
        {
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "Иванович",
            "address": "ул. Пушкина, д. 10, кв. 5",
            "phone": "+79161234567",
            "discount_category": "Обычный",
            "discount_percent": 0
        },
        {
            "last_name": "Петрова",
            "first_name": "Мария",
            "middle_name": "Сергеевна",
            "address": "пр. Ленина, д. 5, кв. 12",
            "phone": "+79167654321",
            "discount_category": "Студент",
            "discount_percent": 10
        },
        {
            "last_name": "Сидоров",
            "first_name": "Алексей",
            "middle_name": "Викторович",
            "address": "ул. Гагарина, д. 15, кв. 3",
            "phone": "+79165557733",
            "discount_category": "Пенсионер",
            "discount_percent": 15
        },
        {
            "last_name": "Кузнецова",
            "first_name": "Елена",
            "middle_name": "Александровна",
            "address": "пл. Свободы, д. 3, кв. 7",
            "phone": "+79169998822",
            "discount_category": "Член_клуба",
            "discount_percent": 20
        },
        {
            "last_name": "Николаев",
            "first_name": "Дмитрий",
            "middle_name": "Олегович",
            "address": "ул. Садовая, д. 20, кв. 9",
            "phone": "+79161112233",
            "discount_category": "Ветеран",
            "discount_percent": 25
        },
        {
            "last_name": "Фёдорова",
            "first_name": "Анна",
            "middle_name": None,
            "address": "пр. Мира, д. 8, кв. 15",
            "phone": "+79164445566",
            "discount_category": "Обычный",
            "discount_percent": 0
        }
    ]

    # Вставляем данные в таблицу Books
    print("Добавление книг...")
    for book in books_data:
        if not db.insert_data("Books", book):
            print(f"Ошибка при добавлении книги: {book['title']}")

    # Вставляем данные в таблицу Readers
    print("Добавление читателей...")
    for reader in readers_data:
        if not db.insert_data("Readers", reader):
            print(f"Ошибка при добавлении читателя: {reader['last_name']} {reader['first_name']}")

    # Данные для таблицы Issued_Books
    issued_books_data = [
        {
            "book_id": 1,
            "reader_id": 1,
            "issue_date": date(2024, 1, 15),
            "expected_return_date": date(2024, 2, 15),
            "actual_return_date": date(2024, 2, 10),
            "damage_type": "Нет",
            "damage_fine": 0.00,
            "final_rental_cost": 1300.00,
            "paid": True,
            "actual_rental_days": 26
        },
        {
            "book_id": 2,
            "reader_id": 2,
            "issue_date": date(2024, 3, 1),
            "expected_return_date": date(2024, 3, 15),
            "actual_return_date": date(2024, 3, 20),
            "damage_type": "Царапина",
            "damage_fine": 100.00,
            "final_rental_cost": 855.00,
            "paid": True,
            "actual_rental_days": 19
        },
        {
            "book_id": 3,
            "reader_id": 3,
            "issue_date": date(2024, 4, 10),
            "expected_return_date": date(2024, 4, 24),
            "actual_return_date": None,
            "damage_type": None,
            "damage_fine": None,
            "final_rental_cost": None,
            "paid": False,
            "actual_rental_days": None
        },
        {
            "book_id": 4,
            "reader_id": 4,
            "issue_date": date(2024, 5, 12),
            "expected_return_date": date(2024, 5, 26),
            "actual_return_date": date(2024, 5, 25),
            "damage_type": "Нет",
            "damage_fine": 0.00,
            "final_rental_cost": 780.00,
            "paid": True,
            "actual_rental_days": 13
        },
        {
            "book_id": 5,
            "reader_id": 5,
            "issue_date": date(2024, 6, 1),
            "expected_return_date": date(2024, 6, 15),
            "actual_return_date": date(2024, 6, 14),
            "damage_type": "Порвана_обложка",
            "damage_fine": 200.00,
            "final_rental_cost": 712.50,
            "paid": True,
            "actual_rental_days": 13
        },
        {
            "book_id": 6,
            "reader_id": 6,
            "issue_date": date(2024, 7, 3),
            "expected_return_date": date(2024, 7, 17),
            "actual_return_date": date(2024, 7, 20),
            "damage_type": "Запачкана",
            "damage_fine": 150.00,
            "final_rental_cost": 1296.00,
            "paid": True,
            "actual_rental_days": 17
        },
        {
            "book_id": 7,
            "reader_id": 1,
            "issue_date": date(2024, 8, 10),
            "expected_return_date": date(2024, 8, 24),
            "actual_return_date": date(2024, 8, 22),
            "damage_type": "Нет",
            "damage_fine": 0.00,
            "final_rental_cost": 360.00,
            "paid": True,
            "actual_rental_days": 12
        },
        {
            "book_id": 8,
            "reader_id": 2,
            "issue_date": date(2024, 9, 5),
            "expected_return_date": date(2024, 9, 19),
            "actual_return_date": None,
            "damage_type": None,
            "damage_fine": None,
            "final_rental_cost": None,
            "paid": False,
            "actual_rental_days": None
        },
        {
            "book_id": 1,
            "reader_id": 3,
            "issue_date": date(2024, 10, 1),
            "expected_return_date": date(2024, 10, 15),
            "actual_return_date": date(2024, 10, 10),
            "damage_type": "Нет",
            "damage_fine": 0.00,
            "final_rental_cost": 675.00,
            "paid": True,
            "actual_rental_days": 9
        }
    ]

    # Вставляем данные в таблицу Issued_Books
    print("Добавление записей о выдаче книг...")
    for issued_book in issued_books_data:
        if not db.insert_data("Issued_Books", issued_book):
            print(
                f"Ошибка при добавлении записи о выдаче книги ID {issued_book['book_id']} читателю ID {issued_book['reader_id']}")

    print("Заполнение тестовыми данными завершено!")
    return True


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр класса DB
    db = DB(host="localhost", port=5432, dbname="library_db",
            user="postgres", password="root")

    # Подключаемся к базе данных
    if db.connect():
        # Заполняем базу тестовыми данными
        db.drop_schema()
        db.create_schema()
        fill_test_data(db)
        # Закрываем соединение
        db.disconnect()
    else:
        print("Не удалось подключиться к базе данных")