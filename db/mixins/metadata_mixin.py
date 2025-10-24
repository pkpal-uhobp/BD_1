"""
Миксин для работы с метаданными и схемой базы данных
"""

import logging
from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric, Date, ForeignKey, Boolean, Enum, ARRAY, UniqueConstraint, CheckConstraint, inspect, text
from typing import List, Dict, Any, Optional


class MetadataMixin:
    """Миксин для работы с метаданными и схемой базы данных"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
    def _build_metadata(self):
        """Строит метаданные для всех таблиц базы данных"""
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

    def create_schema(self) -> bool:
        """Создаёт схему БД, если таблицы ещё не существуют."""
        if not self.is_connected():
            self.logger.warning(" Нет подключения — создание схемы невозможно.")
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
                self.logger.error(f" Не удалось создать таблицы: {', '.join(missing)}")
                return False

            self.logger.info(" Схема успешно создана.")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка создания схемы: {self.format_db_error(e)}")
            return False

    def drop_schema(self) -> bool:
        """Удаляет все таблицы схемы БД вместе с пользовательскими типами ENUM и последовательностями."""
        if not self.is_connected():
            self.logger.warning(" Нет подключения — удаление схемы невозможно.")
            return False

        try:
            self.logger.info(" Удаление всех таблиц схемы...")
            self.metadata.drop_all(self.engine)

            # Дополнительно удалим пользовательские ENUM-типы и наши последовательности
            with self.engine.begin() as conn:
                # --- ENUM типы ---
                enum_rows = conn.execute(text("""
                                              SELECT n.nspname, t.typname
                                              FROM pg_type t
                                                       JOIN pg_namespace n ON n.oid = t.typnamespace
                                              WHERE t.typtype = 'e'
                                              """)).fetchall()

                for schema_name, type_name in enum_rows:
                    try:
                        conn.execute(text(f'DROP TYPE IF EXISTS "{schema_name}"."{type_name}" CASCADE'))
                    except Exception as e:
                        self.logger.warning(
                            f" Не удалось удалить тип {schema_name}.{type_name}: {self.format_db_error(e)}"
                        )

                # --- Последовательности, созданные для PK ---
                seq_rows = conn.execute(text("""
                                             SELECT sequence_schema, sequence_name
                                             FROM information_schema.sequences
                                             WHERE sequence_name LIKE 'seq_%'
                                             """)).fetchall()

                for seq_schema, seq_name in seq_rows:
                    try:
                        conn.execute(text(f'DROP SEQUENCE IF EXISTS "{seq_schema}"."{seq_name}" CASCADE'))
                    except Exception as e:
                        self.logger.warning(
                            f" Не удалось удалить последовательность {seq_schema}.{seq_name}: {self.format_db_error(e)}"
                        )

            self.logger.info(" Схема успешно очищена (все таблицы, типы и последовательности удалены).")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка удаления схемы: {self.format_db_error(e)}")
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
            self.logger.error(f" Ошибка при получении списка таблиц: {self.format_db_error(e)}")
            return []

    def get_column_names(self, table_name: str) -> List[str]:
        """Возвращает список колонок указанной таблицы."""
        if not self.is_connected():
            return []

        try:
            insp = inspect(self.engine)
            if table_name not in insp.get_table_names():
                self.logger.error(f" Таблица '{table_name}' не существует в БД.")
                return []

            columns = [col['name'] for col in insp.get_columns(table_name)]
            self.logger.info(f" Колонки таблицы '{table_name}' ({len(columns)}): {columns}")
            return columns

        except Exception as e:
            self.logger.error(f" Ошибка получения колонок '{table_name}': {self.format_db_error(e)}")
            return []

    def get_tables(self) -> List[str]:
        """Возвращает список таблиц в БД (алиас для get_table_names)."""
        return self.get_table_names()
        
    def get_table_columns(self, table_name: str) -> List[str]:
        """Возвращает список колонок указанной таблицы (алиас для get_column_names)."""
        return self.get_column_names(table_name)
        
    def get_column_info(self, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о столбце."""
        if not self.is_connected():
            return None
            
        try:
            insp = inspect(self.engine)
            columns = insp.get_columns(table_name)
            
            for col in columns:
                if col['name'] == column_name:
                    return {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col['default'],
                        'primary_key': col.get('primary_key', False)
                    }
            return None
            
        except Exception as e:
            self.logger.error(f" Ошибка получения информации о столбце '{table_name}.{column_name}': {self.format_db_error(e)}")
            return None

    def _refresh_metadata(self):
        """Обновляет внутренние метаданные и структуру таблиц после изменений в БД (ALTER, DROP, CREATE)."""
        if not self.is_connected():
            self.logger.warning(" Невозможно обновить метаданные — отсутствует подключение к БД.")
            return

        try:
            md = MetaData()
            md.reflect(bind=self.engine)
            self.metadata = md
            self.tables = dict(md.tables)
            self.logger.info(f" Метаданные обновлены: {len(self.tables)} таблиц загружено.")
        except Exception as e:
            self.logger.error(f" Ошибка при обновлении метаданных: {self.format_db_error(e)}")
