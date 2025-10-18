"""
Миксин для CRUD операций (Create, Read, Update, Delete)
"""

import logging
from sqlalchemy import func, select, asc, desc, text, inspect
from typing import List, Dict, Any, Optional, Tuple
from datetime import date


class CrudMixin:
    """Миксин для CRUD операций с базой данных"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
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
            from sqlalchemy import String, Integer, Numeric, Date, Boolean, Enum, ARRAY
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
        from sqlalchemy import CheckConstraint
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

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
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

    def get_sorted_data(
            self,
            table_name: str,
            sort_columns: List[tuple],
            condition: Dict[str, Any] = None,
            aggregate_functions: Dict[str, str] = None,
            group_by: List[str] = None,
            columns: List[str] = None
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
                if columns:
                    valid_cols = [getattr(table.c, c) for c in columns if hasattr(table.c, c)]
                    if not valid_cols:
                        valid_cols = [table]
                    stmt = select(*valid_cols)
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
            self.logger.info(f"🔧 Выполнение SQL: {query[:100]}...")
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params or {})

                if fetch == "one":
                    return result.fetchone()
                elif fetch == "all":
                    return result.fetchall()
                elif fetch == "scalar":
                    return result.scalar()
                elif fetch == "dict":
                    return [dict(row._mapping) for row in result.fetchall()]
                else:
                    return result.rowcount

        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения SQL: {self.format_db_error(e)}")
            return None

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
