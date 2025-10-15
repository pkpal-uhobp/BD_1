from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData, inspect, UniqueConstraint, CheckConstraint, Boolean, Enum, ARRAY
from sqlalchemy import Table, Column, Integer, String, Numeric, Date, ForeignKey, text
import logging
from datetime import date
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy import func, select, asc, desc, text
from sqlalchemy import DDL
from sqlalchemy.exc import SQLAlchemyError


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
        self.logger = logging.getLogger(f"DB")
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
        """Подключается к базе данных и инициализирует метаданные."""
        self.logger.info("Попытка подключения к БД...")
        try:
            url = (
                f"postgresql+psycopg2://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.dbname}"
                f"?sslmode={self.sslmode}&connect_timeout={self.connect_timeout}"
            )

            self.engine = create_engine(url, future=True, pool_pre_ping=True)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            self.logger.info(f"✅ Подключено: {self.dbname}@{self.host}:{self.port}")
            self._build_metadata()
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения: {self.format_db_error(e)}")
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
            Column("address", String, nullable=False),
            Column("phone", String(20), nullable=False),
            Column("discount_category", DiscountCategory, default='Regular'),
            Column("discount_percent", Integer, default=0),
            UniqueConstraint("last_name", "first_name", "middle_name", "phone", name="uq_readers_full_info"),
            CheckConstraint("discount_percent BETWEEN 0 AND 100", name="chk_readers_discount_valid"),
        )
        self.tables["Issued_Books"] = Table(
            "Issued_Books", self.metadata,
            Column("recording_id", Integer, primary_key=True, autoincrement=True),
            Column("book_id", Integer, ForeignKey("Books.id_book", ondelete="CASCADE"), nullable=False),
            Column("reader_id", Integer, ForeignKey("Readers.reader_id", ondelete="CASCADE"), nullable=False),
            Column("issue_date", Date, nullable=False),
            Column("expected_return_date", Date, nullable=False),
            Column("actual_return_date", Date),
            Column("damage_type", DamageType, default='Нет', nullable=False),
            Column("damage_fine", Numeric(10, 2), default=0, nullable=False),
            Column("final_rental_cost", Numeric(10, 2)),
            Column("paid", Boolean, default=False, nullable=False),
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
        """Закрывает соединение с БД и очищает метаданные."""
        if not self.engine:
            self.logger.info("🔌 Соединение уже закрыто или не было установлено.")
            return

        try:
            self.engine.dispose()
            self.engine = None
            self.metadata = None
            self.tables.clear()
            self.logger.info("✅ Соединение с БД успешно закрыто.")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при закрытии соединения: {e}")

    def is_connected(self) -> bool:
        """Проверяет, активно ли соединение с БД (логирует только при ошибке)."""
        if self.engine is None:
            self.logger.warning("⚠️ Проверка подключения: соединение не активно.")
            return False
        return True

    def create_schema(self) -> bool:
        """Создаёт схему БД, если таблицы ещё не существуют."""
        if not self.is_connected():
            self.logger.warning("⚠️ Нет подключения — создание схемы невозможно.")
            return False

        try:
            inspector = inspect(self.engine)
            existing = set(inspector.get_table_names())
            expected = set(self.tables)

            if expected.issubset(existing):
                self.logger.info("Схема уже существует — все таблицы присутствуют.")
                return True

            self.logger.info("🛠 Создание таблиц схемы...")
            self.metadata.create_all(self.engine)

            missing = set(self.tables) - set(inspect(self.engine).get_table_names())
            if missing:
                self.logger.error(f"❌ Не удалось создать таблицы: {', '.join(missing)}")
                return False

            self.logger.info("✅ Схема успешно создана.")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка создания схемы: {self.format_db_error(e)}")
            return False

    def drop_schema(self) -> bool:
        """Удаляет все таблицы схемы БД."""
        if not self.is_connected():
            self.logger.warning("⚠️ Нет подключения — удаление схемы невозможно.")
            return False

        try:
            self.logger.info("🗑 Удаление всех таблиц схемы...")
            self.metadata.drop_all(self.engine)
            self.logger.info("✅ Схема успешно удалена.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления схемы: {self.format_db_error(e)}")
            return False

    def get_table_names(self) -> List[str]:
        """Возвращает список таблиц в БД."""
        if not self.is_connected():
            return []
        try:
            tables = inspect(self.engine).get_table_names()
            self.logger.info(f"📋 Таблицы в БД ({len(tables)}): {tables}")
            return tables
        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении списка таблиц: {self.format_db_error(e)}")
            return []

    def get_column_names(self, table_name: str) -> List[str]:
        """Возвращает список колонок указанной таблицы."""
        if not self.is_connected():
            return []

        try:
            insp = inspect(self.engine)
            if table_name not in insp.get_table_names():
                self.logger.error(f"❌ Таблица '{table_name}' не существует в БД.")
                return []

            columns = [col['name'] for col in insp.get_columns(table_name)]
            self.logger.info(f"📄 Колонки таблицы '{table_name}' ({len(columns)}): {columns}")
            return columns

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения колонок '{table_name}': {self.format_db_error(e)}")
            return []

    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Возвращает все данные из указанной таблицы в виде списка словарей."""
        if not self.is_connected():
            return []

        if table_name not in self.tables:
            self.logger.error(f"❌ Таблица '{table_name}' не определена в метаданных.")
            return []

        try:
            self.logger.info(f"📊 SELECT * FROM \"{table_name}\"")
            table = self.tables[table_name]
            with self.engine.connect() as conn:
                result = conn.execute(table.select())
                rows = [dict(row._mapping) for row in result]

            # Преобразуем списки (например, авторов) в строку
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, list):
                        row[key] = ', '.join(value)

            self.logger.info(f"✅ Получено {len(rows)} строк из '{table_name}'.")
            return rows

        except Exception as e:
            self.logger.error(f"❌ Ошибка чтения таблицы '{table_name}': {self.format_db_error(e)}")
            return []

    def _validate_data(self, table_name: str, data: Dict[str, Any]) -> List[str]:
        """
        Универсальная валидация данных перед вставкой/обновлением.
        Проверяет типы, NOT NULL, ENUM и CHECK-ограничения на основе метаданных SQLAlchemy.
        Возвращает список ошибок (пустой = всё корректно).
        """
        if table_name not in self.tables:
            return [f"❌ Таблица '{table_name}' не найдена в метаданных."]

        table = self.tables[table_name]
        errors = []

        for column in table.columns:
            col_name = column.name
            value = data.get(col_name)
            is_nullable = column.nullable

            # --- 1️⃣ Автоинкремент PK: можно не передавать
            if column.primary_key and column.autoincrement and value is None:
                continue

            # --- 2️⃣ NOT NULL + без default → ошибка, если значение не передано
            if not is_nullable and value is None and column.default is None:
                errors.append(f"Поле '{col_name}' обязательно (NOT NULL), но не заполнено.")
                continue

            # --- 3️⃣ Проверка типов
            py_type = {
                String: str,
                Enum: str,
                Integer: int,
                Numeric: (int, float),
                Date: (str, date),
                Boolean: bool,
                ARRAY: list
            }.get(type(column.type))

            if value is not None and py_type and not isinstance(value, py_type):
                errors.append(
                    f"Поле '{col_name}' имеет неверный тип. Ожидался {py_type}, получен {type(value)}."
                )

            # --- 4️⃣ Проверка формата даты (если строка)
            if isinstance(column.type, Date) and isinstance(value, str):
                from datetime import datetime
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    errors.append(f"Поле '{col_name}' должно быть в формате 'YYYY-MM-DD', получено '{value}'.")

            # --- 5️⃣ Проверка ENUM
            if isinstance(column.type, Enum) and value is not None:
                if value not in column.type.enums:
                    errors.append(
                        f"Поле '{col_name}' имеет недопустимое значение '{value}'. "
                        f"Допустимые: {list(column.type.enums)}."
                    )

        # --- 6️⃣ Проверка CHECK-ограничений (универсально!)
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint) and constraint.sqltext is not None:
                expr = str(constraint.sqltext)
                try:
                    # подставляем значения для проверки
                    expr_eval = expr
                    for k, v in data.items():
                        val = f"'{v}'" if isinstance(v, str) else v
                        expr_eval = expr_eval.replace(k, str(val))
                    if not eval(expr_eval):
                        errors.append(f"Нарушено ограничение CHECK: {expr}")
                except Exception:
                    # если проверку невозможно вычислить — просто пропускаем
                    pass

        return errors

    def _check_foreign_key_exists(self, table_name: str, column_name: str, value: Any) -> bool:
        """Универсально проверяет, существует ли запись с указанным значением во внешней таблице."""
        if not value or table_name not in self.tables:
            return False

        table = self.tables[table_name]
        column = getattr(table.c, column_name, None)
        if column is None or not self.is_connected():
            return False

        try:
            with self.engine.connect() as conn:
                return conn.execute(table.select().where(column == value).limit(1)).first() is not None
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки внешнего ключа {table_name}.{column_name}: {e}")
            return False

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Вставляет одну запись в таблицу с проверкой данных и учётом значений по умолчанию.
        Возвращает (успех, ошибка)."""
        if not self.is_connected():
            return False, "Нет подключения к базе данных."

        # --- Валидация ---
        errors = self._validate_data(table_name, data)
        if errors:
            for e in errors:
                self.logger.warning(f"⚠️ Ошибка валидации: {e}")
            return False, "; ".join(errors)

        try:
            table = self.tables[table_name]
            pk_col = self._get_primary_key_column(table_name)
            free_id = self._find_min_free_id(table_name)
            if free_id is None:
                msg = "❌ Не удалось найти свободный ID."
                self.logger.error(msg)
                return False, msg

            # --- Подготовка данных ---
            values = data.copy()
            values[pk_col] = free_id

            # Исключаем автоинкрементные поля
            insert_data = {
                col.name: values.get(col.name, col.default.arg if col.default is not None else None)
                for col in table.columns if not (col.primary_key and col.autoincrement)
            }

            self.logger.info(f"🟢 INSERT INTO {table_name} (ID={free_id}) ...")

            # --- Выполнение вставки ---
            with self.engine.begin() as conn:
                conn.execute(table.insert().values(**insert_data))

            self.logger.info(f"✅ Успешно вставлена запись с ID={free_id}.")
            return True, None

        except Exception as e:
            error_msg = f"Ошибка вставки в '{table_name}': {self.format_db_error(e)}"
            self.logger.error(f"❌ {error_msg}")
            return False, error_msg

    def _find_min_free_id(self, table_name: str) -> int:
        """Находит минимальный свободный ID в указанной таблице (или 1, если таблица пуста)."""
        if not self.is_connected():
            return 1

        try:
            pk = self._get_primary_key_column(table_name)
            with self.engine.connect() as conn:
                max_id = conn.execute(text(f'SELECT COALESCE(MAX("{pk}"), 0) FROM "{table_name}"')).scalar()
                result = conn.execute(text(f"""
                    SELECT MIN(id)
                    FROM generate_series(1, {max_id + 1}) AS g(id)
                    WHERE id NOT IN (SELECT "{pk}" FROM "{table_name}")
                """))
                return result.scalar() or max_id + 1

        except Exception as e:
            self.logger.error(f"❌ Ошибка поиска свободного ID: {self.format_db_error(e)}")
            # fallback — берём MAX+1
            try:
                with self.engine.connect() as conn:
                    max_id = conn.execute(text(f'SELECT COALESCE(MAX("{pk}"), 0) FROM "{table_name}"')).scalar()
                    return max_id + 1
            except Exception:
                return 1

    def _get_primary_key_column(self, table_name: str) -> str:
        """Возвращает имя первичного ключа таблицы (универсально, без жёстких привязок)."""
        if table_name not in self.tables:
            self.logger.error(f"❌ Таблица '{table_name}' не найдена в метаданных.")
            return "id"

        table = self.tables[table_name]
        pk_cols = [col.name for col in table.primary_key.columns]
        if pk_cols:
            return pk_cols[0]

        # Если PK не определён — пытаемся угадать по общепринятым именам
        for name in ("id", f"{table_name.lower()}_id", "pk"):
            if name in table.columns:
                return name

        self.logger.warning(f"⚠️ Первичный ключ не найден для таблицы '{table_name}'. Возвращено 'id'.")
        return "id"

    def record_exists(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """Проверяет, существует ли запись в таблице, удовлетворяющая условию."""
        if not self.is_connected() or table_name not in self.tables:
            return False

        table = self.tables[table_name]
        try:
            valid_conds = []
            for k, v in condition.items():
                col = getattr(table.c, k, None)
                if col is not None:
                    valid_conds.append(col == v)
                else:
                    self.logger.warning(f"⚠️ Колонка '{k}' отсутствует в таблице '{table_name}'.")

            if not valid_conds:
                self.logger.error(f"❌ Нет корректных условий для поиска в '{table_name}'.")
                return False

            stmt = table.select().where(*valid_conds).limit(1)
            self.logger.info(f"🔍 Проверка записи в '{table_name}' по условию {condition}")

            with self.engine.connect() as conn:
                exists = conn.execute(stmt).first() is not None

            self.logger.info(f"✅ Запись {'найдена' if exists else 'не найдена'} в '{table_name}'.")
            return exists

        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки записи в '{table_name}': {self.format_db_error(e)}")
            return False

    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """Удаляет записи из таблицы, удовлетворяющие условию."""
        if not self.is_connected() or table_name not in self.tables:
            return False

        table = self.tables[table_name]
        try:
            where_clauses = []
            for k, v in condition.items():
                col = getattr(table.c, k, None)
                if col is not None:
                    where_clauses.append(col == v)
                else:
                    self.logger.warning(f"⚠️ Колонка '{k}' отсутствует в таблице '{table_name}'.")

            if not where_clauses:
                self.logger.error(f"❌ Нет корректных условий для удаления в '{table_name}'.")
                return False

            stmt = table.delete().where(*where_clauses)
            self.logger.info(f"🗑 Удаление записей из '{table_name}' по условию {condition}")

            with self.engine.begin() as conn:
                result = conn.execute(stmt)
                count = result.rowcount or 0

            self.logger.info(f"✅ Удалено {count} записей из '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления из '{table_name}': {self.format_db_error(e)}")
            return False

    def update_data(self, table_name: str, condition: Dict[str, Any], new_values: Dict[str, Any]) -> bool:
        """Обновляет записи в таблице, удовлетворяющие условию."""
        if not self.is_connected() or table_name not in self.tables or not new_values:
            return False

        table = self.tables[table_name]
        try:
            # --- Проверка колонок для обновления ---
            valid_values = {}
            for col, val in new_values.items():
                if hasattr(table.c, col):
                    valid_values[col] = val
                else:
                    self.logger.warning(f"⚠️ Колонка '{col}' отсутствует в таблице '{table_name}'.")

            if not valid_values:
                self.logger.error(f"❌ Нет корректных колонок для обновления в '{table_name}'.")
                return False

            # --- Формируем WHERE ---
            where_clauses = []
            for k, v in condition.items():
                col = getattr(table.c, k, None)
                if col is not None:
                    where_clauses.append(col == v)
                else:
                    self.logger.warning(f"⚠️ Колонка '{k}' отсутствует в условии WHERE таблицы '{table_name}'.")

            if not where_clauses:
                self.logger.error(f"❌ Нет корректных условий WHERE для обновления в '{table_name}'.")
                return False

            # --- Выполнение обновления ---
            stmt = table.update().where(*where_clauses).values(**valid_values)
            self.logger.info(f"📝 UPDATE '{table_name}' SET {list(valid_values.keys())} WHERE {condition}")

            with self.engine.begin() as conn:
                result = conn.execute(stmt)
                count = result.rowcount or 0

            self.logger.info(f"✅ Обновлено {count} записей в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления '{table_name}': {self.format_db_error(e)}")
            return False

    from sqlalchemy import func, select, asc, desc, text

    def get_sorted_data(
            self,
            table_name: str,
            sort_columns: List[tuple],
            condition: Dict[str, Any] = None,
            aggregate_functions: Dict[str, str] = None,
            group_by: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Возвращает отсортированные данные с фильтрацией, группировкой и агрегатами."""
        if not self.is_connected() or table_name not in self.tables:
            return []

        table = self.tables[table_name]
        try:
            # --- SELECT ---
            if aggregate_functions:
                select_fields = []
                for alias, func_expr in aggregate_functions.items():
                    # Пример: aggregate_functions = {"total_books": "COUNT(id_book)"}
                    select_fields.append(text(f"{func_expr} AS {alias}"))
                stmt = select(*select_fields)
            else:
                stmt = select(table)

            # --- WHERE ---
            if condition:
                for col, val in condition.items():
                    if hasattr(table.c, col):
                        stmt = stmt.where(getattr(table.c, col) == val)
                    else:
                        self.logger.warning(f"⚠️ Колонка '{col}' не найдена в '{table_name}'")

            # --- GROUP BY ---
            if group_by:
                group_cols = [getattr(table.c, col) for col in group_by if hasattr(table.c, col)]
                if group_cols:
                    stmt = stmt.group_by(*group_cols)

            # --- ORDER BY ---
            if sort_columns:
                order_clauses = []
                for col, ascending in sort_columns:
                    if hasattr(table.c, col):
                        order_clauses.append(asc(getattr(table.c, col)) if ascending else desc(getattr(table.c, col)))
                if order_clauses:
                    stmt = stmt.order_by(*order_clauses)

            self.logger.info(f"📊 Выполнение запроса сортировки для '{table_name}'")
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                rows = [dict(row._mapping) for row in result]
            self.logger.info(f"✅ Получено {len(rows)} строк из '{table_name}'")
            return rows

        except Exception as e:
            self.logger.error(f"❌ Ошибка сортировки в '{table_name}': {self.format_db_error(e)}")
            return []

    def execute_query(self, query: str, params: Dict[str, Any] = None, fetch: str = None) -> Any:
        """Универсально выполняет SQL-запрос с логированием и безопасной обработкой ошибок."""
        if not self.is_connected():
            return None

        try:
            # Подготовка запроса к логированию
            short_query = (query.strip()[:100] + "...") if len(query.strip()) > 100 else query.strip()
            self.logger.info(f"🧠 SQL: {short_query}")
            if params:
                self.logger.debug(f"Параметры: {params}")

            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})

                if fetch in ("dict", "all"):
                    rows = [dict(row._mapping) for row in result]
                    self.logger.info(f"📦 Получено {len(rows)} строк (fetch='{fetch}')")
                    return rows

                elif fetch == "one":
                    row = result.fetchone()
                    self.logger.info(f"📦 Получена {'1 строка' if row else '0 строк'} (fetch='one')")
                    return dict(row._mapping) if row else None

                elif fetch is None:
                    count = result.rowcount or 0
                    self.logger.info(f"📝 DML: затронуто {count} строк")
                    return count

                else:
                    data = result.fetchall()
                    self.logger.info(f"⚙️ fetch='{fetch}', возвращено {len(data)} записей")
                    return data

        except Exception as e:
            self.logger.error(f"❌ Ошибка SQL: {self.format_db_error(e)}")
            return None

    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Возвращает список внешних ключей указанной таблицы."""
        if not self.is_connected():
            return []

        try:
            insp = inspect(self.engine)
            if table_name not in insp.get_table_names():
                self.logger.error(f"❌ Таблица '{table_name}' не существует в БД")
                return []

            fks = insp.get_foreign_keys(table_name)
            self.logger.info(f"🔗 Внешние ключи '{table_name}': {len(fks)} найдено")
            return fks

        except Exception as e:
            self.logger.error(f"⚠️ Ошибка получения внешних ключей '{table_name}': {self.format_db_error(e)}")
            return []

    def get_joined_summary(
            self,
            left_table: str,
            right_table: str,
            join_on: List[Tuple[str, str]],  # Теперь ожидаем список кортежей
            columns: List[str] = None,
            condition: Dict[str, Any] = None,
            sort_columns: List[tuple] = None,
            join_type: str = "INNER"
    ) -> List[Dict[str, Any]]:
        """Возвращает данные из двух таблиц через JOIN (INNER, LEFT, RIGHT, FULL, CROSS)."""
        if not self.is_connected():
            return []

        try:
            # Проверка таблиц
            if left_table not in self.tables or right_table not in self.tables:
                self.logger.error(f"❌ Одна из таблиц не найдена: {left_table}, {right_table}")
                return []

            left, right = self.tables[left_table], self.tables[right_table]

            # --- НАДЕЖНАЯ ОБРАБОТКА ПАРАМЕТРА join_on ---
            # Поддерживаем как старый формат (один кортеж), так и новый (список кортежей)
            if isinstance(join_on, tuple) and join_on and not isinstance(join_on[0], tuple):
                # Это старый формат: ('col1', 'col2')
                join_on_list = [join_on]
            elif isinstance(join_on, list):
                # Это новый формат: [('col1', 'col2'), ...]
                join_on_list = join_on
            else:
                self.logger.error(
                    f"❌ Неверный формат параметра join_on: {join_on}. Ожидался кортеж или список кортежей.")
                return []

            # ✅ ИСПРАВЛЕНО: Правильно обрабатываем список столбцов с префиксами
            if columns:
                selected_cols = []
                for col_str in columns:
                    if '.' in col_str:
                        prefix, column_name = col_str.split('.', 1)
                        if prefix == 't1' and hasattr(left.c, column_name):
                            selected_cols.append(getattr(left.c, column_name))
                        elif prefix == 't2' and hasattr(right.c, column_name):
                            selected_cols.append(getattr(right.c, column_name))
                        else:
                            self.logger.error(f"❌ Не удалось разобрать столбец для SELECT: {col_str}")
                            return []  # Прерываем, если столбец невалидный
                    else:  # Если префикса нет (на всякий случай)
                        if hasattr(left.c, col_str):
                            selected_cols.append(getattr(left.c, col_str))
                        elif hasattr(right.c, col_str):
                            selected_cols.append(getattr(right.c, col_str))
                        else:
                            self.logger.error(f"❌ Столбец '{col_str}' не найден ни в одной из таблиц.")
                            return []
            else:
                selected_cols = list(left.c) + list(right.c)

            stmt = select(*selected_cols)

            # --- ЛОГИКА ДЛЯ JOIN ---
            if join_type.upper() == "CROSS":
                stmt = stmt.select_from(left.join(right, isouter=False, full=False))
            else:
                join_map = {
                    "INNER": left.join,
                    "LEFT": left.join,
                    "RIGHT": lambda r, onclause: right.join(left, onclause, isouter=True),
                    "FULL": lambda r, onclause: left.join(r, onclause, full=True)
                }
                join_func = join_map.get(join_type.upper(), left.join)

                # Создаем список условий для JOIN
                on_clauses = []
                for left_col_name, right_col_name in join_on_list:
                    on_clauses.append(getattr(left.c, left_col_name) == getattr(right.c, right_col_name))

                # Объединяем условия через AND
                if not on_clauses:
                    self.logger.error("❌ Не предоставлено ни одного условия для JOIN.")
                    return []

                # Используем sqlalchemy.and_ для объединения нескольких условий
                from sqlalchemy import and_
                final_on_clause = and_(*on_clauses) if len(on_clauses) > 1 else on_clauses[0]

                stmt = stmt.select_from(join_func(right, final_on_clause))

            # WHERE
            if condition:
                for col, val in condition.items():
                    if hasattr(left.c, col):
                        stmt = stmt.where(getattr(left.c, col) == val)
                    elif hasattr(right.c, col):
                        stmt = stmt.where(getattr(right.c, col) == val)
                    else:
                        self.logger.warning(f"⚠️ Колонка '{col}' не найдена в '{left_table}' или '{right_table}'")

            # ORDER BY
            if sort_columns:
                order_exprs = []
                for col, asc_order in sort_columns:
                    for t in (left, right):
                        if hasattr(t.c, col):
                            order_exprs.append(asc(getattr(t.c, col)) if asc_order else desc(getattr(t.c, col)))
                            break
                if order_exprs:
                    stmt = stmt.order_by(*order_exprs)

            # Выполнение
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                rows = [dict(row._mapping) for row in result]

            self.logger.info(f"✅ JOIN '{join_type}' между '{left_table}' и '{right_table}' — {len(rows)} строк")
            return rows

        except Exception as e:
            self.logger.error(f"❌ Ошибка JOIN-запроса ({join_type}): {self.format_db_error(e)}")
            return []

    def record_exists_ex_table(self, table_name: str) -> bool:
        """Проверяет, существует ли таблица в базе данных (не только в метаданных)."""
        if not self.is_connected():
            return False
        try:
            insp = inspect(self.engine)
            exists = table_name in insp.get_table_names()
            self.logger.info(f"🔍 Таблица '{table_name}' {'существует' if exists else 'не найдена'} в БД")
            return exists
        except Exception as e:
            self.logger.error(f"⚠️ Ошибка проверки таблицы '{table_name}': {self.format_db_error(e)}")
            return False

    def count_records_filtered(self, table_name: str, condition: Dict[str, Any] = None) -> int:
        """Возвращает количество записей в таблице с учётом фильтров (WHERE)."""
        if not self.is_connected() or table_name not in self.tables:
            return 0

        try:
            table = self.tables[table_name]
            stmt = select(func.count()).select_from(table)

            # WHERE-условия
            if condition:
                for col, val in condition.items():
                    if hasattr(table.c, col):
                        stmt = stmt.where(getattr(table.c, col) == val)
                    else:
                        self.logger.warning(f"⚠️ Колонка '{col}' отсутствует в таблице '{table_name}'")

            # Выполнение
            with self.engine.connect() as conn:
                count = conn.execute(stmt).scalar_one()

            self.logger.info(f"🧮 Подсчитано {count} записей в '{table_name}' с фильтрацией: {condition or '{}'}")
            return count

        except Exception as e:
            self.logger.error(f"❌ Ошибка подсчёта записей '{table_name}': {self.format_db_error(e)}")
            return 0

    def _refresh_metadata(self):
        """Обновляет внутренние метаданные и структуру таблиц после изменений в БД (ALTER, DROP, CREATE)."""
        if not self.is_connected():
            self.logger.warning("⚠️ Невозможно обновить метаданные — отсутствует подключение к БД.")
            return

        try:
            md = MetaData()
            md.reflect(bind=self.engine)
            self.metadata = md
            self.tables = dict(md.tables)
            self.logger.info(f"🔄 Метаданные обновлены: {len(self.tables)} таблиц загружено.")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при обновлении метаданных: {self.format_db_error(e)}")

    def add_column(self, table_name: str, column_name: str, column_type, **kwargs) -> bool:
        """Добавляет новый столбец в таблицу (с поддержкой DEFAULT, CHECK, UNIQUE и NULL)."""
        if not self.is_connected():
            return False

        try:
            self.logger.info(f"🧩 ALTER TABLE '{table_name}': добавление колонки '{column_name}'")

            # Проверка существования таблицы
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"❌ Таблица '{table_name}' не существует в БД")
                return False

            # Формируем SQL-части
            type_str = column_type.compile(dialect=self.engine.dialect)
            nullable = "NULL" if kwargs.get("nullable", True) else "NOT NULL"

            default_val = kwargs.get("default")
            if default_val is not None:
                # Автоматически экранируем строки
                default = f"DEFAULT '{default_val}'" if isinstance(default_val, str) else f"DEFAULT {default_val}"
            else:
                default = ""

            check = f"CHECK ({kwargs['check']})" if "check" in kwargs else ""
            unique = "UNIQUE" if kwargs.get("unique", False) else ""

            # Собираем финальную строку SQL
            parts = [type_str, nullable, default, check, unique]
            column_def = " ".join(p for p in parts if p)
            sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_def};'
            self.logger.debug(f"Сгенерированный SQL: {sql}")

            # Выполнение
            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f"✅ Колонка '{column_name}' успешно добавлена в '{table_name}'")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления колонки '{column_name}': {self.format_db_error(e)}")
            return False

    def drop_column_safe(self, table_name: str, column_name: str, force: bool = False) -> bool:
        """
        Безопасное удаление столбца с проверкой зависимостей.
        force=True — удаляет столбец вместе с зависимостями (CASCADE).
        """
        if not self.is_connected():
            self.logger.error("❌ Нет подключения к БД.")
            return False

        try:
            # --- Проверка существования таблицы ---
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"❌ Таблица '{table_name}' не существует в БД.")
                return False

            # --- Проверка существования колонки ---
            columns = self.get_column_names(table_name)
            actual_col = next((c for c in columns if c.lower() == column_name.lower()), None)
            if not actual_col:
                self.logger.error(f"❌ Столбец '{column_name}' не найден в таблице '{table_name}'.")
                return False

            # --- Проверка зависимостей ---
            dependencies = self.get_column_dependencies(table_name, actual_col)
            if not force:
                if dependencies.get("foreign_keys"):
                    self.logger.error(
                        f"⚠️ Столбец '{actual_col}' участвует во внешних ключах: {dependencies['foreign_keys']}")
                    return False
                if dependencies.get("constraints"):
                    self.logger.warning(
                        f"⚠️ Столбец '{actual_col}' используется в ограничениях: {dependencies['constraints']}")
                if dependencies.get("indexes"):
                    self.logger.warning(f"⚠️ Столбец '{actual_col}' используется в индексах: {dependencies['indexes']}")

            # --- Удаление ---
            sql = f'ALTER TABLE "{table_name}" DROP COLUMN "{actual_col}"{" CASCADE" if force else ""};'
            self.logger.info(f"🧩 ALTER TABLE: удаление столбца '{actual_col}' из '{table_name}' (force={force})")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f"✅ Столбец '{actual_col}' успешно удалён из таблицы '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Ошибка при удалении столбца '{column_name}' из '{table_name}': {self.format_db_error(e)}")
            return False

    def get_column_dependencies(self, table_name: str, column_name: str) -> Dict[str, List[str]]:
        """
        Возвращает зависимости указанного столбца:
        - foreign_keys: внешние ключи
        - constraints: ограничения (CHECK)
        - indexes: индексы
        """
        deps = {'foreign_keys': [], 'constraints': [], 'indexes': []}

        if not self.is_connected():
            self.logger.warning("⚠️ Невозможно проверить зависимости — нет подключения к БД.")
            return deps

        try:
            insp = inspect(self.engine)

            # --- Внешние ключи ---
            for fk in insp.get_foreign_keys(table_name):
                if column_name in fk.get("constrained_columns", []):
                    ref_cols = ", ".join(fk.get("referred_columns", []))
                    deps["foreign_keys"].append(f"{fk['referred_table']}({ref_cols})")

            # --- CHECK-ограничения ---
            for chk in insp.get_check_constraints(table_name):
                sqltext = str(chk.get("sqltext", "")).lower()
                if column_name.lower() in sqltext:
                    deps["constraints"].append(chk.get("name", "(без имени)"))

            # --- Индексы ---
            for idx in insp.get_indexes(table_name):
                if column_name in idx.get("column_names", []):
                    deps["indexes"].append(idx.get("name", "(без имени)"))

            total = sum(len(v) for v in deps.values())
            self.logger.info(
                f"🔎 Зависимости столбца '{column_name}' в '{table_name}': {total} найдено "
                f"(FK={len(deps['foreign_keys'])}, CHECK={len(deps['constraints'])}, IDX={len(deps['indexes'])})"
            )

            return deps

        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа зависимостей '{table_name}.{column_name}': {self.format_db_error(e)}")
            return deps

    def rename_table(self, old_table_name: str, new_table_name: str) -> bool:
        """Переименовывает таблицу в БД с обновлением метаданных."""
        if not self.is_connected():
            self.logger.error("❌ Нет подключения к БД.")
            return False

        try:
            # --- Проверки существования ---
            if not self.record_exists_ex_table(old_table_name):
                self.logger.error(f"❌ Таблица '{old_table_name}' не существует.")
                return False
            if self.record_exists_ex_table(new_table_name):
                self.logger.error(f"⚠️ Таблица '{new_table_name}' уже существует.")
                return False

            # --- Выполнение ---
            sql = f'ALTER TABLE "{old_table_name}" RENAME TO "{new_table_name}";'
            self.logger.info(f"🔧 Переименование таблицы: '{old_table_name}' → '{new_table_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            # --- Обновление метаданных ---
            self._refresh_metadata()
            self.logger.info(f"✅ Таблица успешно переименована: '{old_table_name}' → '{new_table_name}'")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка переименования таблицы '{old_table_name}': {self.format_db_error(e)}")
            return False

    def rename_column(self, table_name: str, old_column_name: str, new_column_name: str) -> bool:
        """Переименовывает столбец в таблице с обновлением метаданных и проверкой зависимостей."""
        if not self.is_connected():
            self.logger.error("❌ Нет подключения к БД.")
            return False

        try:
            # --- Проверки существования таблицы ---
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"❌ Таблица '{table_name}' не существует.")
                return False

            columns = self.get_column_names(table_name)
            actual_old = next((c for c in columns if c.lower() == old_column_name.lower()), None)
            actual_new = next((c for c in columns if c.lower() == new_column_name.lower()), None)

            if not actual_old:
                self.logger.error(f"❌ Столбец '{old_column_name}' не найден в таблице '{table_name}'.")
                return False
            if actual_new:
                self.logger.error(f"⚠️ Столбец '{new_column_name}' уже существует в '{table_name}'.")
                return False

            # --- Проверка зависимостей (предупреждения, но не блокировка) ---
            deps = self.get_column_dependencies(table_name, actual_old)
            total_deps = sum(len(v) for v in deps.values())
            if total_deps > 0:
                self.logger.warning(
                    f"⚠️ Переименование '{actual_old}' затронет {total_deps} зависимостей "
                    f"(FK={len(deps['foreign_keys'])}, CHECK={len(deps['constraints'])}, IDX={len(deps['indexes'])})"
                )

            # --- Выполнение SQL ---
            sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{actual_old}" TO "{new_column_name}";'
            self.logger.info(f"🧩 Переименование столбца: '{table_name}.{actual_old}' → '{new_column_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            # --- Обновляем метаданные ---
            self._refresh_metadata()
            self.logger.info(f"✅ Столбец '{actual_old}' успешно переименован в '{new_column_name}' в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка переименования '{table_name}.{old_column_name}': {self.format_db_error(e)}")
            return False

    def alter_column_type(self, table_name: str, column_name: str, new_type) -> bool:
        """
        Изменяет тип данных столбца (с безопасным преобразованием и логированием).
        Поддерживает автоматическое определение USING для PostgreSQL.
        """
        if not self.is_connected():
            self.logger.error("❌ Нет подключения к БД.")
            return False

        try:
            # --- Проверки существования таблицы и столбца ---
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"❌ Таблица '{table_name}' не существует.")
                return False

            columns = self.get_column_names(table_name)
            actual_col = next((c for c in columns if c.lower() == column_name.lower()), None)
            if not actual_col:
                self.logger.error(f"❌ Столбец '{column_name}' не найден в таблице '{table_name}'.")
                return False

            # --- Получаем строковое представление нового типа ---
            type_str = new_type.compile(dialect=self.engine.dialect) if hasattr(new_type, "compile") else str(new_type)

            # --- Определяем текущий тип колонки ---
            inspector = inspect(self.engine)
            current_type = None
            for col in inspector.get_columns(table_name):
                if col["name"].lower() == actual_col.lower():
                    current_type = str(col["type"])
                    break

            # --- Подготавливаем USING (только для PostgreSQL) ---
            using_clause = ""
            if self.engine.dialect.name == "postgresql" and current_type:
                old = current_type.lower()
                new = type_str.lower()

                if "char" in old and "int" in new:
                    using_clause = f" USING {actual_col}::integer"
                elif "int" in old and "char" in new:
                    using_clause = f" USING {actual_col}::varchar"
                elif "num" in old and "int" in new:
                    using_clause = f" USING {actual_col}::integer"
                elif "int" in old and "num" in new:
                    using_clause = f" USING {actual_col}::numeric"
                elif "bool" in old and "char" in new:
                    using_clause = f" USING CASE WHEN {actual_col}=true THEN 'true' ELSE 'false' END"
                elif "date" in old and "char" in new:
                    using_clause = f" USING to_char({actual_col}, 'YYYY-MM-DD')"

            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{actual_col}" TYPE {type_str}{using_clause};'

            self.logger.info(f"🧩 Изменение типа столбца '{table_name}.{actual_col}' → {type_str}")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            # --- Обновляем метаданные ---
            self._refresh_metadata()

            self.logger.info(f"✅ Тип столбца '{actual_col}' успешно изменён на {type_str}.")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"❌ Ошибка изменения типа '{table_name}.{column_name}': {msg}")
            return False

    def set_column_nullable(self, table_name: str, column_name: str, nullable: bool) -> bool:
        """
        Устанавливает или снимает ограничение NOT NULL для столбца.
        Автоматически заполняет NULL значения перед установкой NOT NULL.
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            action = "DROP NOT NULL" if nullable else "SET NOT NULL"
            self.logger.info(f"{action} для столбца '{column_name}' в таблице '{table_name}'")

            # Проверяем наличие таблицы и колонки
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return False

            existing_columns = self.get_column_names(table_name)
            if column_name not in existing_columns:
                self.logger.error(f"Столбец '{column_name}' не существует в таблице '{table_name}'")
                return False

            # Если делаем NOT NULL — заменяем существующие NULL на безопасные значения
            if not nullable:
                inspector = inspect(self.engine)
                column_type = None
                for col in inspector.get_columns(table_name):
                    if col["name"].lower() == column_name.lower():
                        column_type = str(col["type"]).lower()
                        break

                if column_type:
                    # Подбираем подходящее значение по типу
                    if "int" in column_type:
                        default_value = "0"
                    elif "numeric" in column_type or "decimal" in column_type or "float" in column_type:
                        default_value = "0.0"
                    elif "bool" in column_type:
                        default_value = "FALSE"
                    elif "date" in column_type:
                        default_value = "CURRENT_DATE"
                    else:
                        default_value = "''"

                    update_sql = f'''
                        UPDATE "{table_name}" 
                        SET "{column_name}" = {default_value}
                        WHERE "{column_name}" IS NULL;
                    '''
                    with self.engine.begin() as conn:
                        result = conn.execute(text(update_sql))
                        if result.rowcount > 0:
                            self.logger.info(f"Заполнено {result.rowcount} NULL значений перед установкой NOT NULL.")

            # Формируем и выполняем основной SQL
            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" {action};'
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(
                f"✅ Ограничение NOT NULL успешно {'снято' if nullable else 'установлено'} для '{column_name}'")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"❌ Ошибка изменения ограничения NOT NULL: {msg}")
            return False

    def add_constraint(self, table_name: str, constraint_name: str, constraint_type: str, **kwargs) -> bool:
        """
        Добавляет ограничение (CHECK, UNIQUE, FOREIGN KEY) к таблице.
        Пример:
            db.add_constraint("Books", "chk_price", "CHECK", check_condition="price > 0")
            db.add_constraint("Users", "uq_email", "UNIQUE", columns=["email"])
            db.add_constraint("Orders", "fk_user", "FOREIGN_KEY",
                              columns="user_id", foreign_table="Users", foreign_columns="id")
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return False

            constraint_type = constraint_type.upper()
            sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" '

            # ✅ Универсальные шаблоны для трёх типов ограничений
            match constraint_type:
                case "CHECK":
                    cond = kwargs.get("check_condition")
                    if not cond:
                        self.logger.error("❌ Для CHECK-ограничения необходимо указать параметр 'check_condition'")
                        return False
                    sql += f"CHECK ({cond})"

                case "UNIQUE":
                    cols = kwargs.get("columns")
                    if not cols:
                        self.logger.error("❌ Для UNIQUE необходимо указать 'columns'")
                        return False
                    cols_str = ", ".join(f'"{c}"' for c in (cols if isinstance(cols, list) else [cols]))
                    sql += f"UNIQUE ({cols_str})"

                case "FOREIGN_KEY":
                    cols = kwargs.get("columns")
                    ref_table = kwargs.get("foreign_table")
                    ref_cols = kwargs.get("foreign_columns")

                    if not all([cols, ref_table, ref_cols]):
                        self.logger.error("❌ Для FOREIGN KEY нужны 'columns', 'foreign_table' и 'foreign_columns'")
                        return False

                    if not self.record_exists_ex_table(ref_table):
                        self.logger.error(f"Ссылочная таблица '{ref_table}' не существует")
                        return False

                    cols_str = ", ".join(f'"{c}"' for c in (cols if isinstance(cols, list) else [cols]))
                    ref_cols_str = ", ".join(f'"{c}"' for c in (ref_cols if isinstance(ref_cols, list) else [ref_cols]))
                    sql += f"FOREIGN KEY ({cols_str}) REFERENCES \"{ref_table}\" ({ref_cols_str})"

                case _:
                    self.logger.error(f"Неизвестный тип ограничения: {constraint_type}")
                    return False

            sql += ";"
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f"✅ Ограничение '{constraint_name}' успешно добавлено к '{table_name}'")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"❌ Ошибка добавления ограничения: {msg}")
            return False

    def drop_constraint(self, table_name: str, constraint_name: str) -> bool:
        """
        Удаляет ограничение из таблицы.
        Поддерживает все типы ограничений (CHECK, UNIQUE, FOREIGN KEY и т.д.)
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return False

            self.logger.info(f"Удаление ограничения '{constraint_name}' из таблицы '{table_name}'")

            # Проверяем существование ограничения (если метод get_table_constraints реализован)
            constraints = self.get_table_constraints(table_name)
            if not any(c.get("name") == constraint_name for c in constraints):
                self.logger.warning(f"⚠️ Ограничение '{constraint_name}' не найдено — возможно, оно уже удалено")
                return False

            sql = f'ALTER TABLE "{table_name}" DROP CONSTRAINT "{constraint_name}";'
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f"✅ Ограничение '{constraint_name}' успешно удалено из '{table_name}'")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"❌ Ошибка удаления ограничения '{constraint_name}': {msg}")
            return False

    def get_table_constraints(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Возвращает список ограничений (CHECK, UNIQUE, FOREIGN KEY) для таблицы.
        """
        if not self.is_connected():
            return []

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return []

            insp = inspect(self.engine)
            constraints = []

            # Обработчик добавления ограничения (чтобы не дублировать код)
            def add_constraint(name, type_, definition, columns=None, **extra):
                constraints.append({
                    "name": name,
                    "type": type_,
                    "definition": definition,
                    "columns": columns or [],
                    **extra
                })

            # --- CHECK ---
            for chk in insp.get_check_constraints(table_name):
                add_constraint(
                    chk["name"], "CHECK",
                    str(chk.get("sqltext", "")),
                )

            # --- UNIQUE ---
            for uq in insp.get_unique_constraints(table_name):
                cols = uq.get("column_names", [])
                add_constraint(
                    uq["name"], "UNIQUE",
                    f"UNIQUE ({', '.join(cols)})", cols
                )

            # --- FOREIGN KEY ---
            for fk in insp.get_foreign_keys(table_name):
                add_constraint(
                    fk["name"], "FOREIGN KEY",
                    f"FOREIGN KEY ({', '.join(fk['constrained_columns'])}) "
                    f"REFERENCES {fk['referred_table']}({', '.join(fk['referred_columns'])})",
                    fk["constrained_columns"],
                    foreign_table=fk["referred_table"],
                    foreign_columns=fk["referred_columns"]
                )

            self.logger.info(f"Найдено {len(constraints)} ограничений в '{table_name}'")
            return constraints

        except Exception as e:
            self.logger.error(f"Ошибка получения ограничений таблицы '{table_name}': {self.format_db_error(e)}")
            return []

    def set_column_default(self, table_name: str, column_name: str, default_value: Any) -> bool:
        """
        Устанавливает значение по умолчанию (DEFAULT) для столбца.
        """
        if not self.is_connected():
            return False

        try:
            # Проверки существования таблицы и столбца
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return False

            if column_name not in self.get_column_names(table_name):
                self.logger.error(f"Столбец '{column_name}' не найден в таблице '{table_name}'")
                return False

            # Форматируем значение
            if default_value is None:
                default_sql = "NULL"
            elif isinstance(default_value, str) and not default_value.upper().startswith(("CURRENT_", "NEXTVAL(")):
                default_sql = f"'{default_value}'"  # строка
            else:
                default_sql = str(default_value)  # число или SQL-выражение

            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET DEFAULT {default_sql};'
            self.logger.info(f"Установка DEFAULT {default_sql} для {table_name}.{column_name}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f"Значение по умолчанию успешно установлено для '{table_name}.{column_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка установки значения по умолчанию: {self.format_db_error(e)}")
            return False

    def select_with_filters(
            self,
            table_name: str,
            columns: List[str] = None,
            where_conditions: Dict[str, Any] = None,
            order_by: List[tuple] = None,
            group_by: List[str] = None,
            having_conditions: Dict[str, Any] = None,
            limit: int = None,
            offset: int = None
    ) -> List[Dict[str, Any]]:
        """
        Универсальный SELECT с фильтрами, сортировкой, группировкой, HAVING и пагинацией.
        """
        if not self.is_connected() or table_name not in self.tables:
            return []

        try:
            table = self.tables[table_name]
            stmt = table.select()

            # --- Колонки ---
            if columns:
                valid_cols = [getattr(table.c, c) for c in columns if hasattr(table.c, c)]
                if not valid_cols:
                    self.logger.warning(f"Указанные колонки не найдены в '{table_name}'")
                    return []
                stmt = stmt.with_only_columns(*valid_cols)

            params, i = {}, 0

            # --- Универсальный генератор условий ---
            def _make_conditions(conds, prefix):
                nonlocal i
                if not conds:
                    return []
                exprs = []
                for col, val in conds.items():
                    if hasattr(table.c, col):
                        key = f"{prefix}_{i}"
                        exprs.append(getattr(table.c, col) == text(f":{key}"))
                        params[key] = val
                        i += 1
                    else:
                        self.logger.warning(f"Колонка '{col}' не найдена ({prefix})")
                return exprs

            # WHERE
            where_expr = _make_conditions(where_conditions, "where")
            if where_expr:
                stmt = stmt.where(*where_expr)

            # GROUP BY
            if group_by:
                group_cols = [getattr(table.c, c) for c in group_by if hasattr(table.c, c)]
                if group_cols:
                    stmt = stmt.group_by(*group_cols)

            # HAVING
            having_expr = _make_conditions(having_conditions, "having")
            if having_expr:
                stmt = stmt.having(*having_expr)

            # ORDER BY
            if order_by:
                order_expr = [
                    getattr(table.c, col).asc() if asc else getattr(table.c, col).desc()
                    for col, asc in order_by if hasattr(table.c, col)
                ]
                if order_expr:
                    stmt = stmt.order_by(*order_expr)

            # LIMIT / OFFSET
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)

            self.logger.info(f"Выполнение SELECT из '{table_name}'")
            with self.engine.connect() as conn:
                result = conn.execute(stmt, params)
                rows = [dict(row._mapping) for row in result]

            self.logger.info(f"Получено {len(rows)} строк из '{table_name}'")
            return rows

        except Exception as e:
            self.logger.error(f"Ошибка SELECT с фильтрами: {self.format_db_error(e)}")
            return []

    def execute_aggregate_query(
            self,
            query: str,
            aggregate_functions: Dict[str, str] = None,
            group_by: List[str] = None,
            having: str = None
    ) -> Any:
        """
        Выполняет SQL-запрос с агрегатными функциями, группировкой и HAVING.
        Позволяет динамически модифицировать исходный SELECT.
        """
        if not self.is_connected():
            return None

        try:
            base_query = query.strip()
            self.logger.info("Выполнение агрегатного запроса...")

            # Если заданы агрегатные функции — перестраиваем SELECT
            if aggregate_functions:
                select_clause = ", ".join(
                    f"{func} AS {alias}" for alias, func in aggregate_functions.items()
                )

                # Ищем FROM (безопасно и регистронезависимо)
                upper_query = base_query.upper()
                from_idx = upper_query.find("FROM")

                if from_idx == -1:
                    self.logger.error("Ошибка: в запросе отсутствует ключевое слово FROM")
                    return None

                base_query = f"SELECT {select_clause} {base_query[from_idx:]}"
                self.logger.debug(f"Агрегатный SELECT: {base_query}")

            # Добавляем GROUP BY
            if group_by:
                base_query += " GROUP BY " + ", ".join(f'"{col}"' for col in group_by)

            # Добавляем HAVING
            if having:
                base_query += f" HAVING {having}"

            # Выполняем через основной метод
            result = self.execute_query(base_query, fetch="dict")
            count = len(result) if isinstance(result, list) else 1 if result else 0
            self.logger.info(f"Агрегатный запрос успешно выполнен — получено {count} строк")
            return result

        except Exception as e:
            self.logger.error(f"Ошибка выполнения агрегатного запроса: {self.format_db_error(e)}")
            return None

    def text_search(
            self,
            table_name: str,
            column_name: str,
            search_pattern: str,
            search_type: str = "LIKE"
    ) -> List[Dict[str, Any]]:
        """
        Выполняет текстовый поиск (LIKE, ILIKE, POSIX REGEX, NOT LIKE).
        """
        if not self.is_connected():
            return []

        try:
            table = self.tables.get(table_name)
            if not table or not hasattr(table.c, column_name):
                self.logger.error(f"Таблица '{table_name}' или колонка '{column_name}' не найдена")
                return []

            column = getattr(table.c, column_name)
            stmt = table.select()
            search_type = search_type.upper()

            # Карта операторов поиска
            ops = {
                "LIKE": column.like,
                "ILIKE": column.ilike,
                "NOT_LIKE": lambda p: ~column.like(p),
                "NOT_ILIKE": lambda p: ~column.ilike(p),
                "REGEX": lambda p: column.op("~")(p),
                "IREGEX": lambda p: column.op("~*")(p),
                "NOT_REGEX": lambda p: column.op("!~")(p),
                "NOT_IREGEX": lambda p: column.op("!~*")(p),
            }

            if search_type not in ops:
                self.logger.error(f"❌ Неизвестный тип поиска: {search_type}")
                return []

            stmt = stmt.where(ops[search_type](search_pattern))

            self.logger.info(f"🔍 Поиск в '{table_name}.{column_name}' ({search_type}) с шаблоном '{search_pattern}'")

            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                rows = [dict(row._mapping) for row in result]

            self.logger.info(f"✅ Найдено {len(rows)} строк по '{search_pattern}' ({search_type})")
            return rows

        except Exception as e:
            self.logger.error(f"Ошибка текстового поиска: {self.format_db_error(e)}")
            return []

    def string_functions_demo(
            self,
            table_name: str,
            column_name: str,
            function_name: str,
            **params
    ) -> List[Dict[str, Any]]:
        """
        Демонстрация строковых SQL-функций PostgreSQL:
        UPPER, LOWER, LENGTH, SUBSTRING, TRIM, LTRIM, RTRIM,
        REPLACE, CONCAT, CONCAT_WS.
        """
        if not self.is_connected():
            return []

        try:
            func = function_name.upper()
            col = f'"{column_name}"'
            func_sql = None

            # Карта стандартных функций без параметров
            basic_funcs = {
                "UPPER": f"UPPER({col}) AS upper_result",
                "LOWER": f"LOWER({col}) AS lower_result",
                "LENGTH": f"LENGTH({col}) AS length_result",
                "TRIM": f"TRIM({col}) AS trim_result",
                "LTRIM": f"LTRIM({col}) AS ltrim_result",
                "RTRIM": f"RTRIM({col}) AS rtrim_result"
            }

            if func in basic_funcs:
                func_sql = basic_funcs[func]

            elif func == "SUBSTRING":
                start = params.get("start", 1)
                length = params.get("length")
                func_sql = (
                    f"SUBSTRING({col} FROM {start} FOR {length}) AS substring_result"
                    if length else f"SUBSTRING({col} FROM {start}) AS substring_result"
                )

            elif func == "REPLACE":
                old_str = params.get("old_str", " ")
                new_str = params.get("new_str", "")
                func_sql = f"REPLACE({col}, '{old_str}', '{new_str}') AS replace_result"

            elif func == "CONCAT":
                concat_str = params.get("concat_str", "")
                func_sql = f"CONCAT({col}, '{concat_str}') AS concat_result"

            elif func == "CONCAT_WS":
                sep = params.get("separator", " ")
                concat_str = params.get("concat_str", "")
                func_sql = f"CONCAT_WS('{sep}', {col}, '{concat_str}') AS concat_ws_result"

            else:
                self.logger.error(f"Неизвестная строковая функция: {func}")
                return []

            query = f"SELECT {col}, {func_sql} FROM \"{table_name}\" WHERE {col} IS NOT NULL LIMIT 10"
            self.logger.info(f"Выполнение строковой функции: {func} на '{table_name}.{column_name}'")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")
            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка строковой функции: {self.format_db_error(e)}")
            return []

    def substring_function(self, table_name: str, column_name: str, start: int, length: int = None) -> List[
        Dict[str, Any]]:
        """
        Извлекает подстроку из значений указанного столбца.
        Пример: SUBSTRING(column FROM start [FOR length])
        """
        if not self.is_connected():
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            for_clause = f" FOR {length}" if length else ""
            query = f"SELECT {col}, SUBSTRING({col} FROM {start}{for_clause}) AS substring_result FROM {table}"

            self.logger.info(f"Выполнение SUBSTRING для {table_name}.{column_name} (start={start}, length={length})")
            result = self.execute_query(query, fetch="dict")

            self.logger.info(f"Результатов: {len(result) if result else 0}")
            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка выполнения SUBSTRING: {self.format_db_error(e)}")
            return []

    def trim_functions(self, table_name: str, column_name: str, trim_type: str = "BOTH", characters: str = None) -> \
    List[Dict[str, Any]]:
        """
        Удаляет пробелы или указанные символы с начала, конца или обеих сторон строки.

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            trim_type: "BOTH" (по умолчанию), "LEADING" или "TRAILING"
            characters: Символы для удаления (по умолчанию пробелы)

        Returns:
            List[Dict]: Результаты запроса с колонкой trim_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            trim_type = trim_type.upper().strip()
            if trim_type not in {"BOTH", "LEADING", "TRAILING"}:
                self.logger.warning(f"Некорректный trim_type '{trim_type}', используется BOTH по умолчанию")
                trim_type = "BOTH"

            col = f'"{column_name}"'
            table = f'"{table_name}"'

            if characters:
                query = f"SELECT {col}, TRIM({trim_type} '{characters}' FROM {col}) AS trim_result FROM {table}"
            else:
                query = f"SELECT {col}, TRIM({trim_type} FROM {col}) AS trim_result FROM {table}"

            self.logger.info(f"Выполнение TRIM для {table_name}.{column_name} ({trim_type}, chars={characters})")

            result = self.execute_query(query, fetch='dict')
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"Ошибка выполнения TRIM: {msg}")
            return []

    def pad_functions(self, table_name: str, column_name: str, length: int,
                      pad_string: str = ' ', pad_type: str = "RPAD") -> List[Dict[str, Any]]:
        """
        Дополняет строки указанными символами до заданной длины (LPAD или RPAD).

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            length: Общая длина итоговой строки
            pad_string: Символ или строка для дополнения
            pad_type: Тип дополнения ("LPAD" — слева, "RPAD" — справа)

        Returns:
            List[Dict]: Результаты запроса с колонкой pad_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            pad_type = pad_type.upper().strip()
            if pad_type not in {"LPAD", "RPAD"}:
                self.logger.warning(f"Некорректный pad_type '{pad_type}', используется RPAD по умолчанию")
                pad_type = "RPAD"

            # Проверяем входные значения
            if not isinstance(length, int) or length <= 0:
                self.logger.error("Параметр 'length' должен быть положительным целым числом")
                return []

            if not isinstance(pad_string, str) or len(pad_string) == 0:
                self.logger.warning("Пустая строка pad_string, используется пробел по умолчанию")
                pad_string = " "

            col = f'"{column_name}"'
            table = f'"{table_name}"'

            query = f"SELECT {col}, {pad_type}({col}, {length}, '{pad_string}') AS pad_result FROM {table}"

            self.logger.info(
                f"Выполнение {pad_type} для {table_name}.{column_name}, длина={length}, pad='{pad_string}'")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"Ошибка выполнения {pad_type}: {msg}")
            return []

    def concat_operator(self, table_name: str, columns: List[str], separator: str = ' ') -> List[Dict[str, Any]]:
        """
        Объединяет значения нескольких столбцов через оператор || (конкатенация строк в SQL).

        Args:
            table_name: Имя таблицы
            columns: Список столбцов для объединения
            separator: Разделитель между значениями (по умолчанию пробел)

        Returns:
            List[Dict[str, Any]]: Результаты с полем concat_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            # Проверяем наличие таблицы в метаданных
            if table_name not in self.tables:
                self.logger.error(f"Таблица '{table_name}' не найдена в метаданных")
                return []

            # Проверяем колонки
            valid_columns = []
            invalid_columns = []
            for col in columns:
                if hasattr(self.tables[table_name].c, col):
                    valid_columns.append(f'"{col}"')
                else:
                    invalid_columns.append(col)

            if invalid_columns:
                self.logger.warning(f"Некорректные колонки пропущены: {invalid_columns}")

            if not valid_columns:
                self.logger.error("Нет корректных колонок для объединения")
                return []

            # Формируем SQL-выражение
            if separator:
                concat_expr = f" || '{separator}' || ".join(valid_columns)
            else:
                concat_expr = " || ".join(valid_columns)

            query = f'SELECT {concat_expr} AS concat_result FROM "{table_name}"'

            self.logger.info(
                f"Выполнение конкатенации столбцов {valid_columns} через '{separator}' в таблице '{table_name}'")

            result = self.execute_query(query, fetch="dict")

            self.logger.info(f"Результатов: {len(result) if result else 0}")
            return result or []

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f"Ошибка конкатенации строк: {msg}")
            return []

    def get_column_constraints(self, table_name: str, column_name: str) -> Dict[str, Any]:
        """
        Извлекает и парсит ограничения для указанного столбца из схемы БД.
        Возвращает словарь с правилами валидации, включая кросс-полевую логику.
        """
        if not self.is_connected():
            return {}

        constraints = {
            'nullable': True,
            'default': None,
            'data_type': None,
            'max_length': None,
            'precision': None,
            'scale': None,
            'allowed_values': None,
            'min_value': None,
            'max_value': None,
            'array_item_type': None,
            'min_elements': None,
            'max_elements': None,
            'cross_field_checks': [],
        }

        try:
            inspector = inspect(self.engine)

            # Проверяем существование таблицы и колонки
            if table_name not in self.tables or column_name not in self.tables[table_name].c:
                self.logger.error(f"Таблица '{table_name}' или столбец '{column_name}' не найдены.")
                return constraints

            column = self.tables[table_name].c[column_name]

            # --- 1. Базовые свойства ---
            constraints['nullable'] = column.nullable

            from sqlalchemy.sql.elements import TextClause
            default_val = None
            if column.default is not None and hasattr(column.default, 'arg'):
                arg = column.default.arg
                if isinstance(arg, TextClause):
                    default_val = str(arg.text)
                elif callable(arg):
                    default_val = arg.__name__
                else:
                    default_val = str(arg)
            constraints['default'] = default_val

            col_type = column.type
            type_name = type(col_type).__name__
            constraints['data_type'] = type_name

            # --- 2. Типы и характеристики ---
            if isinstance(col_type, String):
                constraints['max_length'] = col_type.length
            elif isinstance(col_type, Numeric):
                constraints['precision'] = col_type.precision
                constraints['scale'] = col_type.scale
            elif isinstance(col_type, Enum):
                constraints['allowed_values'] = list(col_type.enums)
            elif isinstance(col_type, ARRAY):
                constraints['array_item_type'] = type(col_type.item_type).__name__
                item_type = col_type.item_type
                if isinstance(item_type, String):
                    constraints['max_length'] = item_type.length
                elif isinstance(item_type, Numeric):
                    constraints['precision'] = item_type.precision
                    constraints['scale'] = item_type.scale
                elif isinstance(item_type, Enum):
                    constraints['allowed_values'] = list(item_type.enums)

            # --- 3. Парсинг CHECK ограничений ---
            check_constraints = inspector.get_check_constraints(table_name)
            import re

            # Собираем все другие колонки таблицы
            all_other_columns = [col.name for col in self.tables[table_name].columns if col.name != column_name]
            other_columns_pattern = '|'.join(map(re.escape, all_other_columns)) if all_other_columns else None

            for chk in check_constraints:
                sqltext = chk.get('sqltext')
                if not sqltext or column_name not in sqltext:
                    continue

                # --- Правило 1: сравнение с другим столбцом, если текущее поле не NULL ---
                if other_columns_pattern:
                    pattern_nullable_compare = re.compile(
                        rf"\(\s*{re.escape(column_name)}\s*IS\s+NULL\s*\)\s*OR\s*\(\s*{re.escape(column_name)}\s*([><=]+)\s*({other_columns_pattern})\s*\)",
                        re.IGNORECASE
                    )
                    match = pattern_nullable_compare.search(sqltext)
                    if match:
                        constraints['cross_field_checks'].append({
                            'type': 'compare_if_not_null',
                            'operator': match.group(1).strip(),
                            'reference_column': match.group(2).strip(),
                            'message': f"Значение должно быть {match.group(1).strip()} значения поля '{match.group(2).strip()}' (если указано)"
                        })
                        continue

                    # --- Правило 2: простое сравнение между полями ---
                    pattern_simple_compare = re.compile(
                        rf"{re.escape(column_name)}\s*([><=]+)\s*({other_columns_pattern})\s*(?:AND|$|\))",
                        re.IGNORECASE
                    )
                    match = pattern_simple_compare.search(sqltext)
                    if match:
                        constraints['cross_field_checks'].append({
                            'type': 'compare',
                            'operator': match.group(1).strip(),
                            'reference_column': match.group(2).strip(),
                            'message': f"Значение должно быть {match.group(1).strip()} значения поля '{match.group(2).strip()}'"
                        })
                        continue

                    # --- Новое правило 3: равенство или оба NULL ---
                    pattern_equal_or_null = re.compile(
                        rf"\(\s*{re.escape(column_name)}\s*=\s*({other_columns_pattern})\s*\)\s*OR\s*\(\s*{re.escape(column_name)}\s+IS\s+NULL\s+AND\s*\1\s+IS\s+NULL\s*\)",
                        re.IGNORECASE
                    )
                    match = pattern_equal_or_null.search(sqltext)
                    if match:
                        constraints['cross_field_checks'].append({
                            'type': 'equal_or_both_null',
                            'reference_column': match.group(1),
                            'message': f"Поле должно совпадать с '{match.group(1)}' или оба быть NULL"
                        })
                        continue

                    # --- Правило 4: согласованность NULL/NOT NULL между полями ---
                    if re.search(rf"{re.escape(column_name)}\s+IS\s+NULL", sqltext, re.IGNORECASE):
                        null_part_cols = set(re.findall(r"(\w+)\s+IS\s+NULL", sqltext, re.IGNORECASE))
                        not_null_part_cols = set(re.findall(r"(\w+)\s+IS\s+NOT\s+NULL", sqltext, re.IGNORECASE))
                        if null_part_cols == not_null_part_cols:
                            constraints['cross_field_checks'].append({
                                'type': 'null_consistency',
                                'reference_columns': list(null_part_cols),
                                'message': "Заполненность этого поля должна быть согласована с другими полями"
                            })
                            continue

                # --- Правило 5: простые диапазоны и списки ---
                between_match = re.search(rf"{re.escape(column_name)}\s+BETWEEN\s+([\d.-]+)\s+AND\s+([\d.-]+)",
                                          sqltext, re.IGNORECASE)
                if between_match and type_name in ['Integer', 'Numeric', 'Date']:
                    constraints['min_value'] = float(between_match.group(1))
                    constraints['max_value'] = float(between_match.group(2))
                    continue

                min_match = re.search(rf"{re.escape(column_name)}\s*>=\s*([\d.-]+)", sqltext)
                if min_match:
                    constraints['min_value'] = float(min_match.group(1))

                max_match = re.search(rf"{re.escape(column_name)}\s*<=\s*([\d.-]+)", sqltext)
                if max_match:
                    constraints['max_value'] = float(max_match.group(1))

                in_match = re.search(rf"{re.escape(column_name)}\s+IN\s*\((.*?)\)", sqltext, re.IGNORECASE)
                if in_match:
                    values_str = in_match.group(1)
                    allowed = [v.strip().strip("'\"") for v in values_str.split(',')]
                    if constraints['allowed_values'] is None:
                        constraints['allowed_values'] = allowed
                    else:
                        constraints['allowed_values'] = sorted(list(set(constraints['allowed_values'] + allowed)))

            # --- Короткий лог ---
            self.logger.info(
                f"[CONSTRAINTS] {table_name}.{column_name}: type={constraints['data_type']}, "
                f"nullable={constraints['nullable']}, default={constraints['default']}, "
                f"range=({constraints['min_value']}, {constraints['max_value']}), "
                f"cross_checks={len(constraints['cross_field_checks'])}"
            )

            return constraints

        except Exception as e:
            user_friendly_msg = self.format_db_error(e)
            self.logger.error(f"Ошибка получения ограничений для '{table_name}.{column_name}': {user_friendly_msg}")
            return constraints

    def get_predefined_joins(self) -> Dict[Tuple[str, str], Tuple[str, str]]:
        """
        Анализирует внешние ключи в метаданных и возвращает словарь
        для предопределенных соединений JOIN.

        Для каждой связи создаются две записи, чтобы соединение можно было
        выполнить в любом направлении (A,B и B,A).

        Returns:
            Dict[Tuple[str, str], Tuple[str, str]]: Словарь, где ключ -
            это кортеж из имен таблиц, а значение - кортеж из имен колонок для JOIN.
        """
        predefined_joins = {}
        if not self.tables:
            self.logger.warning("⚠️ Метаданные таблиц не загружены. Невозможно сгенерировать соединения.")
            return predefined_joins

        for table in self.tables.values():
            for fk in table.foreign_keys:
                # Таблица, в которой находится внешний ключ
                local_table_name = table.name
                # Колонка с внешним ключом
                local_column_name = fk.parent.name

                # Таблица, на которую ссылается внешний ключ
                referenced_table_name = fk.column.table.name
                # Колонка, на которую ссылается внешний ключ
                referenced_column_name = fk.column.name

                # Создаем запись для прямого соединения (local, referenced)
                predefined_joins[(local_table_name, referenced_table_name)] = (local_column_name, referenced_column_name)

                # И для обратного соединения (referenced, local)
                predefined_joins[(referenced_table_name, local_table_name)] = (referenced_column_name, local_column_name)

        self.logger.info(f"🔗 Сгенерирован словарь соединений: {predefined_joins}")
        return predefined_joins