from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, MetaData, text, Column, Integer, String, Date, ForeignKey, CheckConstraint, \
    Numeric, Table, inspect
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
                 connect_timeout: int = 5):
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
        """Строим метаданные и привязываем их к engine"""
        self.metadata = MetaData()

        self.tables["Books"] = Table(
            "Books", self.metadata,
            Column("id_book", Integer, primary_key=True, autoincrement=True),
            Column("Название", String(255), nullable=False),
            Column("Автор", String(255), nullable=False),
            Column("Жанр", String(100)),
            Column("Залоговая_стоимость", Numeric(10, 2), nullable=False),
            Column("Базовая_стоимость_проката", Numeric(10, 2), nullable=False),
            CheckConstraint("Залоговая_стоимость >= 0", name="chk_books_deposit"),
            CheckConstraint("Базовая_стоимость_проката >= 0", name="chk_books_rent"),
        )

        self.tables["Читатели"] = Table(
            "Читатели", self.metadata,
            Column("Код_читателя", Integer, primary_key=True, autoincrement=True),
            Column("Фамилия", String(100), nullable=False),
            Column("Имя", String(100), nullable=False),
            Column("Отчество", String(100)),
            Column("Адрес", String),
            Column("Телефон", String(20)),
            Column("Категория_скидки", String(50)),
            Column("Процент_скидки", Integer, default=0),
            CheckConstraint("Процент_скидки BETWEEN 0 AND 100", name="chk_readers_discount"),
        )

        self.tables["Выданные_книги"] = Table(
            "Выданные_книги", self.metadata,
            Column("ID_выдачи", Integer, primary_key=True, autoincrement=True),
            Column("Код_книги", Integer, ForeignKey("Книги.Код_книги", ondelete="CASCADE"), nullable=False),
            Column("Код_читателя", Integer, ForeignKey("Читатели.Код_читателя", ondelete="CASCADE"), nullable=False),
            Column("Дата_выдачи", Date, nullable=False),
            Column("Ожидаемая_дата_возврата", Date, nullable=False),
            Column("Фактическая_дата_возврата", Date),
            Column("Штраф_за_повреждение", Numeric(10, 2), default=0),
            Column("Итоговая_стоимость_проката", Numeric(10, 2)),
            CheckConstraint("Штраф_за_повреждение >= 0", name="chk_issued_damage_fine"),
        )

        # Привязываем метаданные к engine
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

    # Новые методы для работы с данными
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Вставка данных в указанную таблицу"""
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        try:
            with self.engine.begin() as connection:
                connection.execute(
                    self.tables[table_name].insert().values(**data)
                )
            print(f"Данные добавлены в таблицу {table_name}")
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка при вставке данных: {e}")
            return False

    def update_data(self, table_name: str, condition: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Обновление данных в таблице"""
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        try:
            table = self.tables[table_name]
            where_clause = self._build_where_condition(table, condition)

            with self.engine.begin() as connection:
                connection.execute(
                    table.update()
                    .where(where_clause)
                    .values(**new_data)
                )
            print(f"Данные в таблице {table_name} обновлены")
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка при обновлении данных: {e}")
            return False

    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """Удаление данных из таблицы"""
        if not self.is_connected():
            print("Нет подключения к БД")
            return False

        try:
            table = self.tables[table_name]
            where_clause = self._build_where_condition(table, condition)

            with self.engine.begin() as connection:
                connection.execute(
                    table.delete().where(where_clause)
                )
            print(f"Данные из таблицы {table_name} удалены")
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении данных: {e}")
            return False

    def _build_where_condition(self, table: Table, condition: Dict[str, Any]):
        """Построение условия WHERE из словаря"""
        from sqlalchemy import and_
        return and_(*[getattr(table.c, key) == value for key, value in condition.items()])

    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Any]:
        """Выполнение произвольного SQL-запроса"""
        if not self.is_connected():
            print("Нет подключения к БД")
            return []

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def show_tables_structure(self):
        if not self.is_connected():
            print("Нет подключения к БД")
            return

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        for table_name in tables:
            print(f"Таблица: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  Колонка: {column['name']}, Тип: {column['type']}, Nullable: {column['nullable']}")

# Пример использования
db=DB()
db.connect()
db.create_schema()