from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData, inspect, UniqueConstraint, CheckConstraint, Boolean, Enum, ARRAY
from sqlalchemy import Table, Column, Integer, String, Numeric, Date, ForeignKey, text
import logging
from datetime import date
from typing import Optional, Dict, Any, List


class DB:
    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 dbname: str = "library_db",
                 user: str = "postgres",
                 password: str = "root",
                 sslmode: str = "prefer",
                 connect_timeout: int = 5,
                 log_file: str = "db_app.log"):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.sslmode = sslmode
        self.connect_timeout = connect_timeout
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None
        self.tables: Dict[str, Table] = {}
        self.logger = logging.getLogger(f"DB_{dbname}")
        self.logger.setLevel(logging.INFO)
        # Создаём обработчик для записи в файл
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        # Формат сообщений: временная метка, уровень, сообщение
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        # Очищаем предыдущие обработчики (если объект пересоздаётся)
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        # Также логгируем в консоль (опционально)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.info(f"Инициализация DB для {dbname} на {host}:{port}")

    def format_db_error(self, error: Exception) -> str:
        """Преобразует ошибки БД в человеко-понятные сообщения."""
        error_msg = str(error)
        if "could not connect to server" in error_msg:
            return "Не удалось подключиться к серверу БД. Проверьте хост, порт и доступность сервера."
        if "password authentication failed" in error_msg:
            return "Неверное имя пользователя или пароль. Проверьте учётные данные."
        if "database" in error_msg and "does not exist" in error_msg:
            return "Указанная база данных не существует. Проверьте имя БД."
        if "timeout" in error_msg.lower():
            return "Превышено время ожидания подключения. Проверьте настройки сети или сервера."
        if "Connection refused" in error_msg:
            return "Соединение отклонено. Проверьте, запущен ли PostgreSQL."
        # Общее сообщение, если не распознали конкретную ошибку
        return f"Ошибка подключения: {error_msg[:200]}..."

    def connect(self) -> bool:
        """
        Подключается к базе данных.
        Логирует попытку и результат с человеко-понятными сообщениями.
        """
        self.logger.info("Попытка подключения к БД...")
        try:
            database_url = (
                f"postgresql+psycopg2://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.dbname}"
                f"?sslmode={self.sslmode}"
                f"&connect_timeout={self.connect_timeout}"
            )
            self.engine = create_engine(
                database_url,
                future=True,
                pool_pre_ping=True
            )
            # Проверка подключения
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            success_msg = f"Подключено к {self.dbname} на {self.host}:{self.port}"
            self.logger.info(success_msg)
            # Инициализируем метаданные
            self._build_metadata()
            return True
        except Exception as e:
            # Получаем человеко-понятное сообщение
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка подключения: {user_friendly_msg}")
            self.engine = None
            return False

    def _build_metadata(self):
        BookGenre = Enum('Роман', 'Повесть', 'Рассказ', 'Поэзия', 'Детектив',
                         'Триллер', 'Научная фантастика', 'Фэнтези', 'Научная литература', 'Биография', 'Мемуары',
                         'История', 'Философия', 'Психология', 'Саморазвитие', 'Детская литература', 'Приключения',
                         'Ужасы', 'Классика', 'Эссе', 'Пьеса', 'Научно-популярное', 'Путешествия',
                         name='book_genre'
                         )
        DiscountCategory = Enum('Студент', 'Пенсионер', 'Ветеран', 'Член_клуба', 'Обычный',
                                name='discount_category'
                                )
        DamageType = Enum('Нет', 'Царапина', 'Порвана_обложка', 'Потеряна_страница', 'Запачкана', 'Утеряна',
                          name='damage_type'
                          )
        self.metadata = MetaData()
        self.tables["Books"] = Table(
            "Books", self.metadata,
            Column("id_book", Integer, primary_key=True, autoincrement=True),
            Column("title", String(255), nullable=False),
            Column("authors", ARRAY(String(255)), nullable=False),
            Column("genre", BookGenre, nullable=False),
            Column("deposit_amount", Numeric(10, 2), nullable=False),
            Column("daily_rental_rate", Numeric(10, 2), nullable=False, comment="Base rental cost per day"),
            UniqueConstraint("title", "authors", name="uq_books_title_authors"),
            CheckConstraint("deposit_amount >= 0", name="chk_books_deposit_non_negative"),
            CheckConstraint("daily_rental_rate > 0", name="chk_books_daily_rate_positive"),
            CheckConstraint("array_length(authors, 1) > 0", name="chk_books_authors_not_empty"),
        )
        self.tables["Readers"] = Table(
            "Readers", self.metadata,
            Column("reader_id", Integer, primary_key=True, autoincrement=True),
            Column("last_name", String(100), nullable=False),
            Column("first_name", String(100), nullable=False),
            Column("middle_name", String(100)),
            Column("address", String),
            Column("phone", String(20)),
            Column("discount_category", DiscountCategory, default='Regular'),
            Column("discount_percent", Integer, default=0),
            UniqueConstraint("last_name", "first_name", "middle_name", "phone", name="uq_readers_full_info"),
            CheckConstraint("discount_percent BETWEEN 0 AND 100", name="chk_readers_discount_valid"),
        )
        self.tables["Issued_Books"] = Table(
            "Issued_Books", self.metadata,
            Column("issue_id", Integer, primary_key=True, autoincrement=True),
            Column("book_id", Integer, ForeignKey("Books.id_book", ondelete="CASCADE"), nullable=False),
            Column("reader_id", Integer, ForeignKey("Readers.reader_id", ondelete="CASCADE"), nullable=False),
            Column("issue_date", Date, nullable=False),
            Column("expected_return_date", Date, nullable=False),
            Column("actual_return_date", Date),
            Column("damage_type", DamageType, default='None'),
            Column("damage_fine", Numeric(10, 2), default=0),
            Column("final_rental_cost", Numeric(10, 2)),
            Column("paid", Boolean, default=False),
            Column("actual_rental_days", Integer),
            CheckConstraint("damage_fine >= 0", name="chk_issued_damage_fine_non_negative"),
            CheckConstraint("actual_rental_days >= 0", name="chk_issued_duration_non_negative"),
            CheckConstraint(
                "(actual_return_date IS NULL) OR (actual_return_date >= issue_date)",
                name="chk_issued_return_date_valid"
            ),
            CheckConstraint("expected_return_date >= issue_date", name="chk_issued_expected_date_valid"),
            CheckConstraint(
                "(actual_return_date IS NULL AND final_rental_cost IS NULL AND actual_rental_days IS NULL) "
                "OR (actual_return_date IS NOT NULL AND final_rental_cost IS NOT NULL AND actual_rental_days IS NOT NULL)",
                name="chk_issued_consistency_on_return"
            ),
            UniqueConstraint("book_id", "reader_id", "actual_return_date", name="uq_issued_book_reader_active"),
        )
        if self.engine:
            self.metadata.bind = self.engine

    def disconnect(self):
        """Закрывает соединение с БД и освобождает ресурсы."""
        if self.engine:
            try:
                self.engine.dispose()
                self.engine = None
                self.metadata = None
                self.tables = {}
                msg = "Соединение с БД закрыто"
                self.logger.info(msg)
            except Exception as e:
                error_msg = f"Ошибка при закрытии соединения: {str(e)}"
                self.logger.error(error_msg)
        else:
            msg = "Соединение уже закрыто или не было установлено"
            self.logger.info(msg)

    def is_connected(self) -> bool:
        """Проверяет, активно ли соединение с БД."""
        connected = self.engine is not None
        self.logger.info(f"Проверка подключения: {'активно' if connected else 'не активно'}")
        return connected

    def create_schema(self) -> bool:
        """
        Создаёт схему БД, если таблицы ещё не существуют.
        Логирует DDL-операции и ошибки.
        """
        if not self.is_connected():
            return False
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            expected_tables = set(self.tables.keys())
            if expected_tables.issubset(existing_tables):
                msg = "Схема уже существует — все таблицы созданы ранее"
                self.logger.info(msg)
                return True
            # Логируем начало DDL-операции
            self.logger.info("Выполнение DDL: CREATE TABLES...")
            # Выполняем создание
            self.metadata.create_all(self.engine)
            # Проверяем результат
            inspector = inspect(self.engine)
            existing_tables_after = set(inspector.get_table_names())
            if expected_tables.issubset(existing_tables_after):
                msg = "Схема успешно создана"
                self.logger.info(msg)
                return True
            else:
                missing = expected_tables - existing_tables_after
                msg = f"Не удалось создать таблицы: {missing}"
                self.logger.error(msg)
                return False

        except Exception as e:
            # Получаем человеко-понятное сообщение
            user_friendly_msg = self.format_db_error(e)
            print(user_friendly_msg)
            self.logger.error(f"Ошибка создания схемы: {user_friendly_msg}")
            return False

    def drop_schema(self) -> bool:
        """
        Удаляет все таблицы схемы.
        Логирует DDL-операции и ошибки.
        """
        if not self.is_connected():
            return False
        try:
            self.logger.info("Выполнение DDL: DROP TABLES...")
            self.metadata.drop_all(self.engine)
            msg = "Схема успешно удалена"
            self.logger.info(msg)
            return True
        except Exception as e:
            # Получаем человеко-понятное сообщение
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка удаления схемы: {user_friendly_msg}")
            return False

    def get_table_names(self) -> List[str]:
        """
        Возвращает список названий всех таблиц в текущей БД.
        Логирует попытку получения и ошибки.
        """
        if not self.is_connected():
            return []
        try:
            self.logger.info("Получение списка таблиц из БД...")
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            self.logger.info(f"Получено {len(table_names)} таблиц: {table_names}")
            return table_names
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка получения списка таблиц: {user_friendly_msg}")
            return []

    def get_column_names(self, table_name: str) -> List[str]:
        """
        Возвращает список названий колонок для указанной таблицы.
        Логирует операцию и ошибки.
        """
        if not self.is_connected():
            return []
        try:
            self.logger.info(f"Получение списка колонок для таблицы '{table_name}'...")
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            if table_name not in existing_tables:
                msg = f"Таблица '{table_name}' не существует в БД"
                self.logger.error(msg)
                return []
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            self.logger.info(f"Получено {len(column_names)} колонок для таблицы '{table_name}': {column_names}")
            return column_names

        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            print(user_friendly_msg)
            self.logger.error(f"Ошибка получения колонок таблицы '{table_name}': {user_friendly_msg}")
            return []

    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Возвращает все данные из указанной таблицы в виде списка словарей.
        Логирует DML-операцию (SELECT) и ошибки.
        """
        if not self.is_connected():
            msg = "Нет подключения к БД"
            self.logger.error(msg)
            return []
        try:
            if table_name not in self.tables:
                msg = f"Таблица '{table_name}' не определена в метаданных приложения"
                self.logger.error(msg)
                return []
            self.logger.info(f"Выполнение DML: SELECT * FROM \"{table_name}\"")
            table = self.tables[table_name]
            with self.engine.connect() as conn:
                result = conn.execute(table.select())
                rows = [dict(row._mapping) for row in result]
            msg = f"Получено {len(rows)} строк из таблицы '{table_name}'"
            self.logger.info(msg)
            return rows
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка получения данных из таблицы '{table_name}': {user_friendly_msg}")
            return []

    def _validate_data(self, table_name: str, data: Dict[str, Any]) -> List[str]:
        """
        Валидирует данные перед вставкой.
        Игнорирует NOT NULL для автоинкрементных первичных ключей, если они не переданы.
        Возвращает список ошибок (пустой = всё ок).
        """
        if table_name not in self.tables:
            return [f"Таблица '{table_name}' не существует в метаданных"]
        table = self.tables[table_name]
        errors = []
        for column in table.columns:
            col_name = column.name
            is_nullable = column.nullable
            value = data.get(col_name)
            # ПРОПУСКАЕМ автоинкрементные PK, если значение не передано
            if column.primary_key and column.autoincrement and value is None:
                continue  # БД сама сгенерирует значение — это нормально
            # Проверка NOT NULL (если поле не PK autoincrement)
            if not is_nullable and value is None:
                errors.append(f"Поле '{col_name}' обязательно (NOT NULL), но получено NULL")
                continue  # Дальше не проверяем, если уже ошибка
            # Определяем ожидаемый тип Python для базовой проверки
            py_type = None
            if isinstance(column.type, (String, Enum)):
                py_type = str
            elif isinstance(column.type, Integer):
                py_type = int
            elif isinstance(column.type, Numeric):
                py_type = (int, float)
            elif isinstance(column.type, Date):
                py_type = (str, date)  # разрешаем строку в формате 'YYYY-MM-DD'
            elif isinstance(column.type, Boolean):
                py_type = bool
            elif isinstance(column.type, ARRAY):
                py_type = list
            # Проверка типа (если значение не None)
            if value is not None and py_type:
                if not isinstance(value, py_type):
                    errors.append(f"Поле '{col_name}' имеет неверный тип. Ожидался {py_type}, получен {type(value)}")
            # Дополнительные проверки для специфичных типов
            if isinstance(column.type, Date) and isinstance(value, str):
                try:
                    from datetime import datetime
                    datetime.strptime(value, '%Y-%m-%d')  # Проверка формата
                except ValueError:
                    errors.append(f"Поле '{col_name}' должно быть в формате 'YYYY-MM-DD', получено: {value}")
            if isinstance(column.type, Numeric) and isinstance(value, (int, float)):
                # Пример: поля, где значение не должно быть отрицательным
                if column.name in ["deposit_amount", "daily_rental_rate", "damage_fine"] and value < 0:
                    errors.append(f"Поле '{col_name}' не может быть отрицательным")
            # Проверка ENUM (если есть)
            if isinstance(column.type, Enum) and value is not None:
                if value not in column.type.enums:
                    errors.append(
                        f"Поле '{col_name}' имеет недопустимое значение '{value}'. Допустимые: {list(column.type.enums)}")
        return errors

    def _check_foreign_key_exists(self, table_name: str, column_name: str, value: Any) -> bool:
        """
        Проверяет, существует ли запись с указанным значением в указанной таблице и колонке.
        Используется для проверки внешних ключей.
        """
        if value is None:
            return False
        if table_name not in self.tables:
            return False
        table = self.tables[table_name]
        column = getattr(table.c, column_name, None)
        if column is None:
            return False
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    table.select().where(column == value).limit(1)
                )
                return result.fetchone() is not None
        except Exception:
            return False

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        Вставляет одну запись в указанную таблицу.
        Логирует DML-операции и ошибки, выводит человеко-понятные сообщения.
        """
        if not self.is_connected():
            return False
        # Валидация данных
        validation_errors = self._validate_data(table_name, data)
        if validation_errors:
            self.logger.warning(f"Ошибки валидации данных для таблицы '{table_name}':")
            for err in validation_errors:
                full_msg = f"  - {err}"
                self.logger.warning(full_msg)
            return False
        try:
            table = self.tables[table_name]
            # Проверка внешних ключей (для Issued_Books)
            if table_name == "Issued_Books":
                book_id = data.get("book_id")
                if not self._check_foreign_key_exists("Books", "id_book", book_id):
                    msg = f"Книга с id_book = {book_id} не существует. Сначала добавьте книгу."
                    self.logger.error(msg)
                    return False
                reader_id = data.get("reader_id")
                if not self._check_foreign_key_exists("Readers", "reader_id", reader_id):
                    msg = f"Читатель с reader_id = {reader_id} не существует. Сначала добавьте читателя."
                    print(msg)
                    self.logger.error(msg)
                    return False
            # Логируем DML-операцию
            self.logger.info(f"Выполнение DML: INSERT INTO \"{table_name}\" ({list(data.keys())})")
            # Вставка с транзакцией
            with self.engine.begin() as conn:
                result = conn.execute(table.insert().values(**data))
                inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else 'неизвестен'
                msg = f"Успешно вставлена 1 запись в таблицу '{table_name}' (ID: {inserted_id})"
                self.logger.info(msg)
                return True
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка при вставке в '{table_name}': {user_friendly_msg}")
            return False

    def record_exists(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """
        Проверяет, существует ли запись в таблице, удовлетворяющая условию.
        Логирует операцию и ошибки, выводит человеко-понятные сообщения.
        """
        if not self.is_connected():
            return False
        if table_name not in self.tables:
            msg = f"Таблица '{table_name}' не определена в метаданных приложения"
            self.logger.error(msg)
            return False
        try:
            table = self.tables[table_name]
            # Строим WHERE условие
            where_clauses = []
            params = {}
            invalid_columns = []
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    invalid_columns.append(col_name)
                    continue
                param_key = f"param_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value
            if invalid_columns:
                msg = f"Предупреждение: колонки не существуют в таблице '{table_name}': {invalid_columns}"
                self.logger.warning(msg)
            if not where_clauses:
                msg = "Не указаны корректные условия для поиска"
                self.logger.error(msg)
                return False
            # Логируем операцию
            self.logger.info(f"Проверка существования записи в таблице '{table_name}' по условию: {condition}")
            # Собираем запрос
            stmt = table.select().where(*where_clauses).limit(1)
            with self.engine.connect() as conn:
                result = conn.execute(stmt, params)
                exists = result.fetchone() is not None
            status = "найдена" if exists else "не найдена"
            self.logger.info(f"Запись в таблице '{table_name}' по условию {condition} — {status}")
            return exists
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка при проверке существования записи в '{table_name}': {user_friendly_msg}")
            return False

    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """
        Удаляет записи из таблицы, удовлетворяющие условию.
        Логирует DML-операцию, предупреждения и ошибки.
        """
        if not self.is_connected():
            return False
        if table_name not in self.tables:
            msg = f"Таблица '{table_name}' не определена в метаданных приложения"
            print(msg)
            self.logger.error(msg)
            return False

        try:
            table = self.tables[table_name]
            where_clauses = []
            params = {}
            invalid_columns = []
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    invalid_columns.append(col_name)
                    continue
                param_key = f"param_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value
            if invalid_columns:
                msg = f"Предупреждение: колонки не существуют в таблице '{table_name}': {invalid_columns}"
                self.logger.warning(msg)
            if not where_clauses:
                msg = "Не указаны корректные условия для удаления"
                self.logger.error(msg)
                return False
            # Логируем DML-операцию
            self.logger.info(f"Выполнение DML: DELETE FROM \"{table_name}\" WHERE {condition}")
            stmt = table.delete().where(*where_clauses)
            with self.engine.begin() as conn:
                result = conn.execute(stmt, params)
                deleted_count = result.rowcount
                if deleted_count == 0:
                    msg = f"Условию {condition} не соответствует ни одна запись в таблице '{table_name}'"
                    self.logger.info(msg)
                else:
                    msg = f"Удалено {deleted_count} записей из таблицы '{table_name}'"
                    self.logger.info(msg)
                return True
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка при удалении из '{table_name}': {user_friendly_msg}")
            return False

    def update_data(self, table_name: str, condition: Dict[str, Any], new_values: Dict[str, Any]) -> bool:
        """
        Обновляет записи в таблице, удовлетворяющие условию.
        Логирует DML-операцию, предупреждения и ошибки.
        """
        if not self.is_connected():
            return False
        if table_name not in self.tables:
            msg = f"Таблица '{table_name}' не определена в метаданных приложения"
            self.logger.error(msg)
            return False
        if not new_values:
            msg = "Нет данных для обновления"
            self.logger.error(msg)
            return False
        try:
            table = self.tables[table_name]
            # Проверка существования колонок для обновления
            invalid_columns = []
            for col_name in new_values.keys():
                if not hasattr(table.c, col_name):
                    invalid_columns.append(col_name)
            if invalid_columns:
                msg = f"Предупреждение: колонки для обновления не существуют в таблице '{table_name}': {invalid_columns}"
                self.logger.warning(msg)
                return False  # Прекращаем, если есть невалидные колонки для SET
            # Подготовка параметров и условий
            params = {}
            for col_name, value in new_values.items():
                params[f"set_{col_name}"] = value
            where_clauses = []
            invalid_where_columns = []
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    invalid_where_columns.append(col_name)
                    continue
                param_key = f"where_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value
            if invalid_where_columns:
                msg = f"Предупреждение: колонки в условии WHERE не существуют: {invalid_where_columns}"
                self.logger.warning(msg)
            if not where_clauses:
                msg = "Не указаны корректные условия WHERE для обновления"
                self.logger.error(msg)
                return False
            # Логируем DML-операцию
            self.logger.info(f"Выполнение DML: UPDATE \"{table_name}\" SET {list(new_values.keys())} WHERE {condition}")
            set_clauses = {col: text(f":set_{col}") for col in new_values.keys()}
            stmt = table.update().where(*where_clauses).values(**set_clauses)
            with self.engine.begin() as conn:
                result = conn.execute(stmt, params)
                updated_count = result.rowcount
                if updated_count == 0:
                    msg = f"Условию {condition} не соответствует ни одна запись в таблице '{table_name}'"
                    self.logger.info(msg)
                else:
                    msg = f"Обновлено {updated_count} записей в таблице '{table_name}'"
                    self.logger.info(msg)
                return True
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка при обновлении '{table_name}': {user_friendly_msg}")
            return False

    def get_sorted_data(self, table_name: str, sort_columns: List[tuple], condition: Dict[str, Any] = None) -> List[
        Dict[str, Any]]:
        """
        Возвращает записи из таблицы, отсортированные по указанным столбцам.
        Логирует операцию и ошибки.
        """
        if not self.is_connected():
            return []
        if table_name not in self.tables:
            msg = f"Таблица '{table_name}' не определена в метаданных приложения"
            self.logger.error(msg)
            return []
        try:
            table = self.tables[table_name]
            stmt = table.select()
            # WHERE условия
            params = {}
            where_clauses = []
            invalid_where_columns = []
            if condition:
                for i, (col_name, value) in enumerate(condition.items()):
                    if hasattr(table.c, col_name):
                        param_key = f"where_{i}"
                        where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                        params[param_key] = value
                    else:
                        invalid_where_columns.append(col_name)
                if invalid_where_columns:
                    msg = f"Предупреждение: колонки в условии WHERE не существуют: {invalid_where_columns}"
                    self.logger.warning(msg)
                if where_clauses:
                    stmt = stmt.where(*where_clauses)
            # ORDER BY
            order_by_clauses = []
            invalid_sort_columns = []
            for col_name, asc in sort_columns:
                if hasattr(table.c, col_name):
                    col = getattr(table.c, col_name)
                    order_by_clauses.append(col.asc() if asc else col.desc())
                else:
                    invalid_sort_columns.append(col_name)
            if invalid_sort_columns:
                msg = f"Предупреждение: колонки для сортировки не существуют: {invalid_sort_columns}"
                self.logger.warning(msg)
            if order_by_clauses:
                stmt = stmt.order_by(*order_by_clauses)
            # Логируем операцию
            sort_info = [(col, "ASC" if asc else "DESC") for col, asc in sort_columns]
            where_info = condition if condition else "без условий"
            self.logger.info(f"Выполнение DML: SELECT * FROM \"{table_name}\" WHERE {where_info} ORDER BY {sort_info}")
            with self.engine.connect() as conn:
                result = conn.execute(stmt, params)
                rows = [dict(row._mapping) for row in result]
            msg = f"Получено {len(rows)} отсортированных строк из таблицы '{table_name}'"
            self.logger.info(msg)
            return rows
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка получения отсортированных данных из '{table_name}': {user_friendly_msg}")
            return []

    def execute_query(self, query: str, params: Dict[str, Any] = None, fetch: str = None) -> Any:
        """
        Выполняет произвольный SQL-запрос.
        Логирует запрос и ошибки, возвращает человеко-понятные сообщения.
        """
        if not self.is_connected():
            return None
        # Обрезаем запрос для лога (чтобы не засорять)
        query_for_log = query.strip()
        if len(query_for_log) > 100:
            query_for_log = query_for_log[:97] + "..."
        try:
            self.logger.info(f"Выполнение SQL-запроса: {query_for_log}")
            if params:
                self.logger.debug(f"Параметры: {params}")
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                if fetch == "one":
                    row = result.fetchone()
                    if row is None:
                        self.logger.info("Запрос вернул 0 строк (fetch='one')")
                        return None
                    result_data = dict(row._mapping) if fetch == "dict" else tuple(row)
                    self.logger.info("Запрос вернул 1 строку (fetch='one')")
                    return result_data
                elif fetch == "all" or fetch == "dict":
                    rows = [dict(row._mapping) for row in result] if fetch == "dict" else [tuple(row) for row in result]
                    self.logger.info(f"Запрос вернул {len(rows)} строк (fetch='{fetch}')")
                    return rows
                elif fetch is None:
                    rowcount = result.rowcount
                    self.logger.info(f"Запрос затронул {rowcount} строк (DML операция)")
                    return rowcount
                else:
                    # Неизвестный fetch — возвращаем как есть
                    data = result.fetchall()
                    self.logger.info(f"Запрос выполнен с нестандартным fetch='{fetch}'")
                    return data
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка выполнения SQL-запроса: {user_friendly_msg}")
            return None

    def get_joined_summary(
            self,
            left_table: str,
            right_table: str,
            join_on: tuple,
            columns: List[str] = None,
            condition: Dict[str, Any] = None,
            sort_columns: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Возвращает сводные данные из двух таблиц через JOIN.
        Логирует операцию и ошибки.
        """
        if not self.is_connected():
            msg = "Нет подключения к БД"
            self.logger.error(msg)
            return []
        # Псевдонимы таблиц
        left_alias = "t1"
        right_alias = "t2"
        try:
            # Проверка существования таблиц
            if not self.record_exists_ex_table(left_table):
                msg = f"Левая таблица '{left_table}' не существует в БД"
                self.logger.error(msg)
                return []
            if not self.record_exists_ex_table(right_table):
                msg = f"Правая таблица '{right_table}' не существует в БД"
                self.logger.error(msg)
                return []
            # Формируем SELECT
            if not columns:
                left_cols = self.get_column_names(left_table)
                right_cols = self.get_column_names(right_table)
                if not left_cols or not right_cols:
                    msg = f"Не удалось получить список колонок для JOIN {left_table} и {right_table}"
                    self.logger.error(msg)
                    return []
                select_cols = [f"{left_alias}.{col}" for col in left_cols] + [f"{right_alias}.{col}" for col in
                                                                              right_cols]
            else:
                select_cols = columns
            select_clause = ", ".join(select_cols)
            query = f"""SELECT {select_clause}
                FROM "{left_table}" {left_alias}
                JOIN "{right_table}" {right_alias} 
                  ON {left_alias}.{join_on[0]} = {right_alias}.{join_on[1]}"""
            params = {}
            where_clauses = []
            # WHERE условия
            if condition:
                for i, (col, value) in enumerate(condition.items()):
                    param_key = f"param_{i}"
                    if "." in col:
                        where_clauses.append(f"{col} = :{param_key}")
                    else:
                        left_cols = self.get_column_names(left_table)
                        right_cols = self.get_column_names(right_table)
                        if col in left_cols:
                            where_clauses.append(f"{left_alias}.{col} = :{param_key}")
                        elif col in right_cols:
                            where_clauses.append(f"{right_alias}.{col} = :{param_key}")
                        else:
                            where_clauses.append(f"{left_alias}.{col} = :{param_key}")
                    params[param_key] = value
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            # ORDER BY
            if sort_columns and isinstance(sort_columns, list):
                order_clauses = []
                for col, ascending in sort_columns:
                    direction = "ASC" if ascending else "DESC"
                    if "." not in col:
                        left_cols = self.get_column_names(left_table)
                        right_cols = self.get_column_names(right_table)
                        if col in left_cols:
                            col = f"{left_alias}.{col}"
                        elif col in right_cols:
                            col = f"{right_alias}.{col}"
                        else:
                            col = f"{left_alias}.{col}"
                    order_clauses.append(f"{col} {direction}")
                if order_clauses:
                    query += " ORDER BY " + ", ".join(order_clauses)
            # Логируем операцию
            query_for_log = query.strip()
            if len(query_for_log) > 150:
                query_for_log = query_for_log[:147] + "..."
            self.logger.info(f"Выполнение JOIN-запроса: {query_for_log}")
            if params:
                self.logger.debug(f"Параметры JOIN-запроса: {params}")
            # Выполняем запрос
            result = self.execute_query(query, params, fetch="dict")
            if result is None:
                msg = f"Не удалось выполнить JOIN между '{left_table}' и '{right_table}'"
                self.logger.error(msg)
                return []
            msg = f"Получено {len(result)} записей из JOIN таблиц '{left_table}' и '{right_table}'"
            self.logger.info(msg)
            return result
        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(
                f"Ошибка выполнения JOIN-запроса для '{left_table}' и '{right_table}': {user_friendly_msg}")
            return []

    def record_exists_ex_table(self, table_name: str) -> bool:
        """Вспомогательный метод: проверяет существование таблицы в БД (не в метаданных)."""
        if not self.is_connected():
            return False
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except:
            return False