from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData, text, Column, Integer, String, Date, ForeignKey, CheckConstraint, \
    Numeric, Table, inspect, UniqueConstraint
from sqlalchemy import Table, Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint, Boolean, Enum, ARRAY, \
    text
import logging
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError
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

    def connect(self) -> bool:
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

            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            print(f"Подключено к {self.dbname} на {self.host}:{self.port}")

            # Инициализируем метаданные после подключения
            self._build_metadata()
            return True

        except SQLAlchemyError as e:
            print(f"Ошибка подключения: {e}")
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
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.metadata = None
            self.tables = {}
            print("Соединение закрыто")

    def is_connected(self) -> bool:
        return self.engine is not None

    def create_schema(self) -> bool:
        if not self.is_connected():
            print("Нет подключения к БД")
            return False
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            expected_tables = set(self.tables.keys())
            if expected_tables.issubset(existing_tables):
                print("Схема уже существует — все таблицы созданы ранее")
                return True
            self.metadata.create_all(self.engine)
            inspector = inspect(self.engine)
            existing_tables_after = set(inspector.get_table_names())
            if expected_tables.issubset(existing_tables_after):
                print("Схема успешно создана")
                return True
            else:
                missing = expected_tables - existing_tables_after
                print(f"Не удалось создать таблицы: {missing}")
                return False

        except SQLAlchemyError as e:
            print(f"Ошибка создания схемы: {e}")
            return False

    def drop_schema(self) -> bool:
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        try:
            self.metadata.drop_all(self.engine)
            print("Схема удалена")
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка сброса схемы: {e}")
            return False

    def get_table_names(self) -> List[str]:
        if not self.is_connected():
            print("Нет подключения к БД")
            return []

        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except SQLAlchemyError as e:
            print(f"Ошибка получения списка таблиц: {e}")
            return []

    def get_column_names(self, table_name: str) -> List[str]:
        if not self.is_connected():
            print("Нет подключения к БД")
            return []
        try:
            inspector = inspect(self.engine)
            if table_name not in inspector.get_table_names():
                print(f"Таблица '{table_name}' не существует")
                return []
            columns = inspector.get_columns(table_name)
            return [col['name'] for col in columns]
        except SQLAlchemyError as e:
            print(f"Ошибка получения колонок таблицы '{table_name}': {e}")
            return []
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        if not self.is_connected():
            print("Нет подключения к БД")
            return []

        try:
            if table_name not in self.tables:
                print(f"Таблица '{table_name}' не определена в метаданных")
                return []

            table = self.tables[table_name]

            with self.engine.connect() as conn:
                result = conn.execute(table.select())
                rows = [dict(row._mapping) for row in result]  # _mapping — для совместимости с SQLAlchemy 2.0+

            print(f"Получено {len(rows)} строк из таблицы '{table_name}'")
            return rows

        except SQLAlchemyError as e:
            print(f"Ошибка получения данных из таблицы '{table_name}': {e}")
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

            # ✅ ПРОПУСКАЕМ автоинкрементные PK, если значение не передано
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
        Перед вставкой проводится валидация.
        """
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        # Валидация данных
        validation_errors = self._validate_data(table_name, data)
        if validation_errors:
            print("Ошибки валидации данных:")
            for err in validation_errors:
                print(f"  - {err}")
            return False

        try:
            table = self.tables[table_name]

            # Проверка внешних ключей (для Issued_Books)
            if table_name == "Issued_Books":
                if not self._check_foreign_key_exists("Books", "id_book", data.get("book_id")):
                    print(f"Книга с id_book = {data.get('book_id')} не существует")
                    return False
                if not self._check_foreign_key_exists("Readers", "reader_id", data.get("reader_id")):
                    print(f"Читатель с reader_id = {data.get('reader_id')} не существует")
                    return False

            # Вставка с транзакцией
            with self.engine.begin() as conn:
                result = conn.execute(table.insert().values(**data))
                print(f"Успешно вставлена 1 запись в таблицу '{table_name}' (ID: {result.inserted_primary_key[0] if result.inserted_primary_key else 'неизвестен'})")
                return True

        except SQLAlchemyError as e:
            print(f"Ошибка при вставке данных в '{table_name}': {e}")
            return False

    def record_exists(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """
        Проверяет, существует ли запись в таблице, удовлетворяющая условию.
        Условие передаётся как словарь: {"column_name": value, ...}
        Возвращает True, если хотя бы одна запись найдена, иначе False.
        Использует подготовленные выражения и LIMIT 1 для эффективности.
        """
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        if table_name not in self.tables:
            print(f"Таблица '{table_name}' не определена в метаданных")
            return False

        try:
            table = self.tables[table_name]

            # Строим WHERE условие
            where_clauses = []
            params = {}
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    print(f"Предупреждение: колонка '{col_name}' не существует в таблице '{table_name}'")
                    continue
                param_key = f"param_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value

            if not where_clauses:
                print("Не указаны корректные условия для поиска")
                return False

            # Собираем запрос
            stmt = table.select().where(*where_clauses).limit(1)

            with self.engine.connect() as conn:
                result = conn.execute(stmt, params)
                exists = result.fetchone() is not None

            return exists

        except SQLAlchemyError as e:
            print(f"Ошибка при проверке существования записи в '{table_name}': {e}")
            return False

    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """
        Удаляет записи из таблицы, удовлетворяющие условию.
        Если удалено 0 записей — выводит предупреждение.
        """
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        if table_name not in self.tables:
            print(f"Таблица '{table_name}' не определена в метаданных")
            return False

        try:
            table = self.tables[table_name]

            where_clauses = []
            params = {}
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    print(f"Предупреждение: колонка '{col_name}' не существует в таблице '{table_name}'")
                    continue
                param_key = f"param_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value

            if not where_clauses:
                print("Не указаны корректные условия для удаления")
                return False

            stmt = table.delete().where(*where_clauses)

            with self.engine.begin() as conn:
                result = conn.execute(stmt, params)
                deleted_count = result.rowcount

                if deleted_count == 0:
                    print(f"Условию {condition} не соответствует ни одна запись в таблице '{table_name}'")
                else:
                    print(f"Удалено {deleted_count} записей из таблицы '{table_name}'")

                return True

        except SQLAlchemyError as e:
            print(f"Ошибка при удалении данных из '{table_name}': {e}")
            return False

    def update_data(self, table_name: str, condition: Dict[str, Any], new_values: Dict[str, Any]) -> bool:
        """
        Обновляет записи в таблице, удовлетворяющие условию.
        condition: словарь с условиями WHERE {"column": value, ...}
        new_values: словарь с новыми значениями {"column": new_value, ...}
        Возвращает True, если запрос выполнен успешно.
        """
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        if table_name not in self.tables:
            print(f"Таблица '{table_name}' не определена в метаданных")
            return False
        if not new_values:
            print("Нет данных для обновления")
            return False
        try:
            table = self.tables[table_name]
            for col_name in new_values.keys():
                if not hasattr(table.c, col_name):
                    print(f"Предупреждение: колонка '{col_name}' не существует в таблице '{table_name}'")
                    return False
            params = {}
            for col_name, value in new_values.items():
                params[f"set_{col_name}"] = value
            where_clauses = []
            for i, (col_name, value) in enumerate(condition.items()):
                if not hasattr(table.c, col_name):
                    print(f"Предупреждение: колонка '{col_name}' не существует в таблице '{table_name}'")
                    continue
                param_key = f"where_{i}"
                where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                params[param_key] = value
            if not where_clauses:
                print("Не указаны корректные условия WHERE для обновления")
                return False
            set_clauses = {col: text(f":set_{col}") for col in new_values.keys()}
            stmt = table.update().where(*where_clauses).values(**set_clauses)
            with self.engine.begin() as conn:
                result = conn.execute(stmt, params)
                updated_count = result.rowcount
                if updated_count == 0:
                    print(f"Условию {condition} не соответствует ни одна запись в таблице '{table_name}'")
                else:
                    print(f"Обновлено {updated_count} записей в таблице '{table_name}'")
                return True

        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении данных в '{table_name}': {e}")
            return False
    def get_sorted_data(self, table_name: str, sort_columns: List[tuple], condition: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Сортировка по нескольким столбцам.
        sort_columns: список кортежей [("column1", True), ("column2", False), ...]
        """
        if not self.is_connected() or table_name not in self.tables:
            return []

        try:
            table = self.tables[table_name]
            stmt = table.select()

            # WHERE
            params = {}
            if condition:
                where_clauses = []
                for i, (col_name, value) in enumerate(condition.items()):
                    if hasattr(table.c, col_name):
                        param_key = f"where_{i}"
                        where_clauses.append(getattr(table.c, col_name) == text(f":{param_key}"))
                        params[param_key] = value
                if where_clauses:
                    stmt = stmt.where(*where_clauses)
            order_by_clauses = []
            for col_name, asc in sort_columns:
                if hasattr(table.c, col_name):
                    col = getattr(table.c, col_name)
                    order_by_clauses.append(col.asc() if asc else col.desc())

            if order_by_clauses:
                stmt = stmt.order_by(*order_by_clauses)

            with self.engine.connect() as conn:
                result = conn.execute(stmt, params)
                return [dict(row._mapping) for row in result]

        except Exception as e:
            print(f"Ошибка: {e}")
            return []

    def execute_query(self, query: str, params: Dict[str, Any] = None, fetch: str = None) -> Any:
        """
        Выполняет произвольный SQL-запрос.
        :param query: SQL-запрос
        :param params: параметры для подстановки (защита от SQL-инъекций)
        :param fetch: "one", "all", "dict" или None
        :return: результат в зависимости от fetch
        """
        if not self.is_connected():
            print("❌ Нет подключения к БД")
            return None

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})

                if fetch == "one":
                    row = result.fetchone()
                    return row if row is None else dict(row._mapping) if fetch == "dict" else tuple(row)
                elif fetch == "all":
                    return [dict(row._mapping) for row in result] if fetch == "dict" else [tuple(row) for row in result]
                elif fetch == "dict":
                    return [dict(row._mapping) for row in result]
                else:
                    return result.rowcount  # для INSERT/UPDATE/DELETE

        except SQLAlchemyError as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
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

        :param left_table: имя левой таблицы (например, "Issued_Books")
        :param right_table: имя правой таблицы (например, "Books")
        :param join_on: кортеж вида ("left_col", "right_col"), например ("book_id", "id_book")
        :param columns: список выбираемых столбцов в формате ["table_alias.column", ...]
                       Если не указано — выбираются все столбцы из обеих таблиц
        :param condition: словарь условий для WHERE, например {"genre": "Роман"}
        :param sort_columns: список кортежей [("column", bool), ...], где bool: True=ASC, False=DESC
        :return: список словарей
        """
        if not self.is_connected():
            print("❌ Нет подключения к БД")
            return []

        # Псевдонимы таблиц
        left_alias = "t1"
        right_alias = "t2"

        try:
            # Формируем SELECT
            if not columns:
                # Выбираем все столбцы из обеих таблиц
                left_cols = self.get_column_names(left_table)
                right_cols = self.get_column_names(right_table)
                select_cols = [f"{left_alias}.{col}" for col in left_cols] + [f"{right_alias}.{col}" for col in right_cols]
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
                        # Явное указание таблицы: "t1.col" или "t2.col"
                        where_clauses.append(f"{col} = :{param_key}")
                    else:
                        # Автоматически определяем, к какой таблице относится столбец
                        left_cols = self.get_column_names(left_table)
                        right_cols = self.get_column_names(right_table)
                        if col in left_cols:
                            where_clauses.append(f"{left_alias}.{col} = :{param_key}")
                        elif col in right_cols:
                            where_clauses.append(f"{right_alias}.{col} = :{param_key}")
                        else:
                            # По умолчанию — левая таблица
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
                        # Автоматическое определение таблицы
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

            # Выполняем запрос
            result = self.execute_query(query, params, fetch="dict")

            if result is None:
                return []

            print(f"✅ Получено {len(result)} записей из JOIN таблиц '{left_table}' и '{right_table}'")
            return result

        except SQLAlchemyError as e:
            print(f"❌ Ошибка выполнения JOIN-запроса: {e}")
            return []
