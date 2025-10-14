# test.py

from datetime import date
from Class_DB import DB

# --- Конфигурация скрипта ---
# Установите в True, если хотите полностью очистить базу данных перед заполнением.
# ВНИМАНИЕ: Это удалит все существующие данные в таблицах!
RESET_DATABASE_BEFORE_FILL = True

def fill_test_data(db):
    """
    Заполняет базу данных тестовыми данными, если они еще не были добавлены.
    """
    # Проверяем подключение к БД
    if not db.is_connected():
        print("Ошибка: нет подключения к БД.")
        return False

    # Проверяем, есть ли уже данные в таблице Books, чтобы избежать дублирования
    if db.count_records_filtered("Books") > 0:
        print("База данных уже содержит данные. Заполнение пропущено.")
        print("Чтобы принудительно очистить и заполнить БД, установите RESET_DATABASE_BEFORE_FILL = True в test.py")
        return True

    # Данные для таблицы Books
    books_data = [
        {"title": "Мастер и Маргарита", "authors": ["Михаил Булгаков"], "genre": "Роман", "deposit_amount": 500.00, "daily_rental_rate": 50.00},
        {"title": "Преступление и наказание", "authors": ["Фёдор Достоевский"], "genre": "Роман", "deposit_amount": 450.00, "daily_rental_rate": 45.00},
        {"title": "1984", "authors": ["Джордж Оруэлл"], "genre": "Научная фантастика", "deposit_amount": 400.00, "daily_rental_rate": 40.00},
        {"title": "Гарри Поттер и философский камень", "authors": ["Джоан Роулинг"], "genre": "Фэнтези", "deposit_amount": 600.00, "daily_rental_rate": 60.00},
        {"title": "Краткая история времени", "authors": ["Стивен Хокинг", "Стивен Хокинг"], "genre": "Научно-популярное", "deposit_amount": 350.00, "daily_rental_rate": 35.00},
        {"title": "Три товарища", "authors": ["Эрих Мария Ремарк"], "genre": "Роман", "deposit_amount": 480.00, "daily_rental_rate": 48.00},
        {"title": "Маленький принц", "authors": ["Антуан де Сент-Экзюпери"], "genre": "Повесть", "deposit_amount": 300.00, "daily_rental_rate": 30.00},
        {"title": "Убийство в Восточном экспрессе", "authors": ["Агата Кристи"], "genre": "Детектив", "deposit_amount": 420.00, "daily_rental_rate": 42.00},
        {"title": "Властелин колец", "authors": ["Джон Рональд Руэл Толкин"], "genre": "Фэнтези", "deposit_amount": 650.00, "daily_rental_rate": 65.00},
        {"title": "Психология влияния", "authors": ["Роберт Чалдини"], "genre": "Психология", "deposit_amount": 380.00, "daily_rental_rate": 38.00}
    ]

    # Данные для таблицы Readers
    readers_data = [
        {"last_name": "Иванов", "first_name": "Иван", "middle_name": "Иванович", "address": "ул. Пушкина, д. 10, кв. 5", "phone": "+79161234567", "discount_category": "Обычный", "discount_percent": 0},
        {"last_name": "Петрова", "first_name": "Мария", "middle_name": "Сергеевна", "address": "пр. Ленина, д. 5, кв. 12", "phone": "+79167654321", "discount_category": "Студент", "discount_percent": 10},
        {"last_name": "Сидоров", "first_name": "Алексей", "middle_name": "Викторович", "address": "ул. Гагарина, д. 15, кв. 3", "phone": "+79165557733", "discount_category": "Пенсионер", "discount_percent": 15},
        {"last_name": "Кузнецова", "first_name": "Елена", "middle_name": "Александровна", "address": "пл. Свободы, д. 3, кв. 7", "phone": "+79169998822", "discount_category": "Член_клуба", "discount_percent": 20},
        {"last_name": "Николаев", "first_name": "Дмитрий", "middle_name": "Олегович", "address": "ул. Садовая, д. 20, кв. 9", "phone": "+79161112233", "discount_category": "Ветеран", "discount_percent": 25},
        {"last_name": "Фёдорова", "first_name": "Анна", "middle_name": None, "address": "пр. Мира, д. 8, кв. 15", "phone": "+79164445566", "discount_category": "Обычный", "discount_percent": 0}
    ]

    # Данные для таблицы Issued_Books
    # ИСПРАВЛЕНО: для записей, где книга еще не возвращена, теперь ЯВНО указаны
    # значения по умолчанию для 'damage_type' и 'damage_fine', чтобы избежать ошибок NOT NULL.
    issued_books_data = [
        {"book_id": 1, "reader_id": 1, "issue_date": date(2024, 1, 15), "expected_return_date": date(2024, 2, 15), "actual_return_date": date(2024, 2, 10), "damage_type": "Нет", "damage_fine": 0.00, "final_rental_cost": 1300.00, "paid": True, "actual_rental_days": 26},
        {"book_id": 2, "reader_id": 2, "issue_date": date(2024, 3, 1), "expected_return_date": date(2024, 3, 15), "actual_return_date": date(2024, 3, 20), "damage_type": "Царапина", "damage_fine": 100.00, "final_rental_cost": 855.00, "paid": True, "actual_rental_days": 19},
        {"book_id": 3, "reader_id": 3, "issue_date": date(2024, 4, 10), "expected_return_date": date(2024, 4, 24), "actual_return_date": None, "damage_type": "Нет", "damage_fine": 0.00, "paid": False},
        {"book_id": 4, "reader_id": 4, "issue_date": date(2024, 5, 12), "expected_return_date": date(2024, 5, 26), "actual_return_date": date(2024, 5, 25), "damage_type": "Нет", "damage_fine": 0.00, "final_rental_cost": 780.00, "paid": True, "actual_rental_days": 13},
        {"book_id": 5, "reader_id": 5, "issue_date": date(2024, 6, 1), "expected_return_date": date(2024, 6, 15), "actual_return_date": date(2024, 6, 14), "damage_type": "Порвана_обложка", "damage_fine": 200.00, "final_rental_cost": 712.50, "paid": True, "actual_rental_days": 13},
        {"book_id": 6, "reader_id": 6, "issue_date": date(2024, 7, 3), "expected_return_date": date(2024, 7, 17), "actual_return_date": date(2024, 7, 20), "damage_type": "Запачкана", "damage_fine": 150.00, "final_rental_cost": 1296.00, "paid": True, "actual_rental_days": 17},
        {"book_id": 7, "reader_id": 1, "issue_date": date(2024, 8, 10), "expected_return_date": date(2024, 8, 24), "actual_return_date": date(2024, 8, 22), "damage_type": "Нет", "damage_fine": 0.00, "final_rental_cost": 360.00, "paid": True, "actual_rental_days": 12},
        {"book_id": 8, "reader_id": 2, "issue_date": date(2024, 9, 5), "expected_return_date": date(2024, 9, 19), "actual_return_date": None, "damage_type": "Нет", "damage_fine": 0.00, "paid": False},
        {"book_id": 1, "reader_id": 3, "issue_date": date(2024, 10, 1), "expected_return_date": date(2024, 10, 15), "actual_return_date": date(2024, 10, 10), "damage_type": "Нет", "damage_fine": 0.00, "final_rental_cost": 675.00, "paid": True, "actual_rental_days": 9}
    ]

    # --- Вставка данных с обработкой ошибок ---
    print("\n--- Начало добавления тестовых данных ---")

    # Вставляем книги
    print("Добавление книг...")
    success_count = 0
    for book in books_data:
        if db.insert_data("Books", book):
            success_count += 1
        else:
            print(f"  [ОШИБКА] Не удалось добавить книгу: {book['title']}")
    print(f"Добавлено {success_count} из {len(books_data)} книг.")

    # Вставляем читателей
    print("\nДобавление читателей...")
    success_count = 0
    for reader in readers_data:
        if db.insert_data("Readers", reader):
            success_count += 1
        else:
            print(f"  [ОШИБКА] Не удалось добавить читателя: {reader['last_name']} {reader['first_name']}")
    print(f"Добавлено {success_count} из {len(readers_data)} читателей.")

    # Вставляем записи о выдаче
    print("\nДобавление записей о выдаче книг...")
    success_count = 0
    for issued_book in issued_books_data:
        if db.insert_data("Issued_Books", issued_book):
            success_count += 1
        else:
            print(f"  [ОШИБКА] Не удалось добавить запись о выдаче (книга ID: {issued_book.get('book_id')}, читатель ID: {issued_book.get('reader_id')})")
    print(f"Добавлено {success_count} из {len(issued_books_data)} записей о выдаче.")

    print("\n--- Заполнение тестовыми данными завершено! ---")
    return True

def main():
    """
    Основная функция для подключения к БД и заполнения данными.
    """
    # Создаем экземпляр класса DB.
    # Учетные данные можно изменить здесь, если они отличаются от defaults в Class_DB.py
    db = DB(
        host="localhost",
        port=5432,
        dbname="library_db",
        user="postgres",
        password="root" # <-- ИЗМЕНИТЕ ПАРОЛЬ, ЕСЛИ НЕОБХОДИМО
    )

    try:
        # Подключаемся к базе данных
        if not db.connect():
            print("Критическая ошибка: не удалось подключиться к базе данных.")
            print("Проверьте параметры подключения (хост, порт, имя пользователя, пароль, имя БД).")
            return

        # Сбрасываем схему, если это указано в конфигурации
        if RESET_DATABASE_BEFORE_FILL:
            print("Сброс базы данных (удаление всех таблиц)...")
            if not db.drop_schema():
                print("Ошибка при сбросе схемы. Дальнейшие действия отменены.")
                return
            print("Схема успешно удалена.")

        # Создаем схему (таблицы), если они не существуют
        print("Создание схемы базы данных (если отсутствует)...")
        if not db.create_schema():
            print("Ошибка при создании схемы БД. Дальнейшие действия отменены.")
            return
        print("Схема готова.")

        # Заполняем базу тестовыми данными
        fill_test_data(db)
        print(db.get_table_constraints('Issued_Books'))

    finally:
        # В любом случае, закрываем соединение с БД
        print("\nЗакрытие соединения с базой данных...")
        db.disconnect()

if __name__ == "__main__":
    main()