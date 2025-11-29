"""
Миксин для операций с таблицами (добавление/удаление колонок, переименование)
"""

import logging
from sqlalchemy import inspect, text
from typing import Dict, List, Any


class TableOperationsMixin:
    """Миксин для операций с таблицами"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
    def add_column(self, table_name: str, column_name: str, column_type, **kwargs) -> bool:
        """Добавляет новый столбец и поэтапно применяет ограничения, чтобы это работало для таблиц с данными.

        Этапы:
          1) Добавляем столбец без жёстких ограничений (всегда NULL, с DEFAULT если задан)
          2) Проставляем DEFAULT существующим строкам (UPDATE ... WHERE col IS NULL)
          3) По очереди добавляем CHECK/NOT NULL/UNIQUE/PRIMARY KEY/FOREIGN KEY
        """
        if not self.is_connected():
            return False

        try:
            self.logger.info(f"🧩 ALTER TABLE '{table_name}': добавление колонки '{column_name}'")

            if not self.record_exists_ex_table(table_name):
                self.logger.error(f" Таблица '{table_name}' не существует в БД")
                return False

            type_str = column_type.compile(dialect=self.engine.dialect)
            # Определим, является ли тип целочисленным, чтобы уметь авто-заполнять PK
            try:
                from sqlalchemy import Integer as SAInt, SmallInteger as SASmallInt, BigInteger as SABigInt
                is_integer_type = isinstance(column_type, (SAInt, SASmallInt, SABigInt))
            except Exception:
                is_integer_type = False
            default_val = kwargs.get("default")

            # 1) Добавляем столбец максимально мягко: допускаем NULL
            default_sql = (
                f" DEFAULT '{default_val}'" if isinstance(default_val, str) else f" DEFAULT {default_val}"
            ) if default_val is not None else ""
            add_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {type_str}{default_sql};'

            with self.engine.begin() as conn:
                self.logger.debug(add_sql)
                conn.execute(text(add_sql))

                # 2) Проставляем DEFAULT существующим строкам, если он задан
                if default_val is not None:
                    upd_sql = text(
                        f'UPDATE "{table_name}" SET "{column_name}" = :def WHERE "{column_name}" IS NULL'
                    )
                    conn.execute(upd_sql, {"def": default_val})

                # 3) CHECK
                if "check" in kwargs and kwargs["check"]:
                    ck_name = f'ck_{table_name}_{column_name}'
                    ck_sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{ck_name}" CHECK ({kwargs["check"]});'
                    self.logger.debug(ck_sql)
                    conn.execute(text(ck_sql))

                # 4) NOT NULL (позже, если потребуется для PK)
                if kwargs.get("nullable") is False and not kwargs.get("primary_key"):
                    nn_sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET NOT NULL;'
                    self.logger.debug(nn_sql)
                    conn.execute(text(nn_sql))

                # 5) UNIQUE
                if kwargs.get("unique"):
                    # Предпроверка дубликатов
                    dup_sql = text(
                        f'SELECT "{column_name}", COUNT(*) FROM "{table_name}" '
                        f'WHERE "{column_name}" IS NOT NULL GROUP BY "{column_name}" HAVING COUNT(*)>1'
                    )
                    dups = conn.execute(dup_sql).fetchall()
                    if dups:
                        self.logger.error(" Невозможно создать UNIQUE — найдены дубликаты")
                        return False
                    uq_name = f'uq_{table_name}_{column_name}'
                    uq_sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{uq_name}" UNIQUE ("{column_name}");'
                    self.logger.debug(uq_sql)
                    conn.execute(text(uq_sql))

                # 6) PRIMARY KEY
                if kwargs.get("primary_key"):
                    # Если есть NULL, попробуем авто-заполнить последовательностью для целочисленного типа
                    null_cnt = conn.execute(text(
                        f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column_name}" IS NULL'
                    )).scalar() or 0
                    if null_cnt > 0 and is_integer_type:
                        self.logger.info("Авто-заполнение значений для нового PK целочисленного типа")
                        fill_sql = (
                            f'UPDATE "{table_name}" t SET "{column_name}" = s.rn '
                            f'FROM (SELECT ctid, ROW_NUMBER() OVER () AS rn FROM "{table_name}") s '
                            f'WHERE t.ctid = s.ctid AND t."{column_name}" IS NULL'
                        )
                        self.logger.debug(fill_sql)
                        conn.execute(text(fill_sql))
                        null_cnt = 0
                    # Повторная проверка NULL
                    if null_cnt > 0:
                        self.logger.error(" Невозможно создать PRIMARY KEY — есть NULL значения и тип нецелочисленный для авто-заполнения")
                        return False
                    dup_cnt = conn.execute(text(
                        f'SELECT COUNT(*) FROM (SELECT "{column_name}" FROM "{table_name}" GROUP BY "{column_name}" HAVING COUNT(*)>1) t'
                    )).scalar() or 0
                    if dup_cnt > 0:
                        self.logger.error(" Невозможно создать PRIMARY KEY — есть дубликаты")
                        return False
                    # Установим NOT NULL перед созданием PK
                    conn.execute(text(
                        f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET NOT NULL;'
                    ))
                    pk_name = f'pk_{table_name}_{column_name}'
                    pk_sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{pk_name}" PRIMARY KEY ("{column_name}");'
                    self.logger.debug(pk_sql)
                    conn.execute(text(pk_sql))

                    # 6.1) AUTOINCREMENT (PostgreSQL IDENTITY)
                    if kwargs.get("autoincrement") and is_integer_type:
                        try:
                            ident_sql = (
                                f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" '
                                f'ADD GENERATED BY DEFAULT AS IDENTITY'
                            )
                            self.logger.debug(ident_sql)
                            conn.execute(text(ident_sql))
                            # Выставим следующий номер = max+1
                            max_val = conn.execute(text(
                                f'SELECT COALESCE(MAX("{column_name}"), 0) FROM "{table_name}"'
                            )).scalar() or 0
                            setval_sql = text(
                                "SELECT setval(pg_get_serial_sequence(:t,:c), :m, true)"
                            )
                            conn.execute(setval_sql, {"t": table_name, "c": column_name, "m": max_val})
                        except Exception as e:
                            self.logger.warning(f"⚠ Не удалось включить IDENTITY для {table_name}.{column_name}: {self.format_db_error(e)}")

                # 7) FOREIGN KEY
                if "foreign_key" in kwargs and kwargs["foreign_key"]:
                    ref_table, ref_column = kwargs["foreign_key"].split(".", 1)
                    fk_name = f'fk_{table_name}_{column_name}_{ref_table}_{ref_column}'
                    # Добавляем NOT VALID, затем валидируем — это безопаснее на больших таблицах
                    fk_sql = (
                        f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{fk_name}" '
                        f'FOREIGN KEY ("{column_name}") REFERENCES "{ref_table}"("{ref_column}") NOT VALID;'
                    )
                    self.logger.debug(fk_sql)
                    conn.execute(text(fk_sql))
                    try:
                        val_sql = f'ALTER TABLE "{table_name}" VALIDATE CONSTRAINT "{fk_name}";'
                        self.logger.debug(val_sql)
                        conn.execute(text(val_sql))
                    except Exception as e:
                        # Если валидация не прошла, оставляем NOT VALID и сообщаем пользователю, что нужно заполнить данные
                        self.logger.warning(f"️ Валидация FK не прошла, ограничение оставлено NOT VALID: {self.format_db_error(e)}")

            self._refresh_metadata()
            self.logger.info(f" Колонка '{column_name}' успешно добавлена в '{table_name}'")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка добавления колонки '{column_name}': {self.format_db_error(e)}")
            return False

    def drop_column_safe(self, table_name: str, column_name: str, force: bool = False) -> bool:
        """
        Безопасное удаление столбца с проверкой зависимостей.
        force=True — удаляет столбец вместе с зависимостями (CASCADE).
        """
        if not self.is_connected():
            self.logger.error(" Нет подключения к БД.")
            return False

        try:
            # --- Проверка существования таблицы ---
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f" Таблица '{table_name}' не существует в БД.")
                return False

            # --- Проверка существования колонки ---
            columns = self.get_column_names(table_name)
            actual_col = next((c for c in columns if c.lower() == column_name.lower()), None)
            if not actual_col:
                self.logger.error(f" Столбец '{column_name}' не найден в таблице '{table_name}'.")
                return False

            # --- Проверка зависимостей ---
            dependencies = self.get_column_dependencies(table_name, actual_col)
            if not force:
                if dependencies.get("foreign_keys"):
                    self.logger.error(
                        f"️ Столбец '{actual_col}' участвует во внешних ключах: {dependencies['foreign_keys']}")
                    return False
                if dependencies.get("constraints"):
                    self.logger.warning(
                        f"️ Столбец '{actual_col}' используется в ограничениях: {dependencies['constraints']}")
                if dependencies.get("indexes"):
                    self.logger.warning(f"️ Столбец '{actual_col}' используется в индексах: {dependencies['indexes']}")

            # --- Удаление ---
            sql = f'ALTER TABLE "{table_name}" DROP COLUMN "{actual_col}"{" CASCADE" if force else ""};'
            self.logger.info(f" ALTER TABLE: удаление столбца '{actual_col}' из '{table_name}' (force={force})")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f" Столбец '{actual_col}' успешно удалён из таблицы '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(
                f" Ошибка при удалении столбца '{column_name}' из '{table_name}': {self.format_db_error(e)}")
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
            self.logger.warning("️ Невозможно проверить зависимости — нет подключения к БД.")
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
            self.logger.error(f" Ошибка анализа зависимостей '{table_name}.{column_name}': {self.format_db_error(e)}")
            return deps

    def rename_table(self, old_table_name: str, new_table_name: str) -> bool:
        """Переименовывает таблицу в БД с обновлением метаданных."""
        if not self.is_connected():
            self.logger.error(" Нет подключения к БД.")
            return False

        try:
            # --- Проверки существования ---
            if not self.record_exists_ex_table(old_table_name):
                self.logger.error(f" Таблица '{old_table_name}' не существует.")
                return False
            if self.record_exists_ex_table(new_table_name):
                self.logger.error(f" Таблица '{new_table_name}' уже существует.")
                return False

            # --- Выполнение ---
            sql = f'ALTER TABLE "{old_table_name}" RENAME TO "{new_table_name}";'
            self.logger.info(f"Переименование таблицы: '{old_table_name}' → '{new_table_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            # --- Обновление метаданных ---
            self._refresh_metadata()
            self.logger.info(f" Таблица успешно переименована: '{old_table_name}' → '{new_table_name}'")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка переименования таблицы '{old_table_name}': {self.format_db_error(e)}")
            return False

    def rename_column(self, table_name: str, old_column_name: str, new_column_name: str) -> bool:
        """Переименовывает столбец в таблице с обновлением метаданных и проверкой зависимостей."""
        if not self.is_connected():
            self.logger.error(" Нет подключения к БД.")
            return False

        try:
            # --- Проверки существования таблицы ---
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f" Таблица '{table_name}' не существует.")
                return False

            columns = self.get_column_names(table_name)
            actual_old = next((c for c in columns if c.lower() == old_column_name.lower()), None)
            actual_new = next((c for c in columns if c.lower() == new_column_name.lower()), None)

            if not actual_old:
                self.logger.error(f" Столбец '{old_column_name}' не найден в таблице '{table_name}'.")
                return False
            if actual_new:
                self.logger.error(f"️ Столбец '{new_column_name}' уже существует в '{table_name}'.")
                return False

            # --- Проверка зависимостей (предупреждения, но не блокировка) ---
            deps = self.get_column_dependencies(table_name, actual_old)
            total_deps = sum(len(v) for v in deps.values())
            if total_deps > 0:
                self.logger.warning(
                    f"️ Переименование '{actual_old}' затронет {total_deps} зависимостей "
                    f"(FK={len(deps['foreign_keys'])}, CHECK={len(deps['constraints'])}, IDX={len(deps['indexes'])})"
                )

            # --- Выполнение SQL ---
            sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{actual_old}" TO "{new_column_name}";'
            self.logger.info(f" Переименование столбца: '{table_name}.{actual_old}' → '{new_column_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            # --- Обновляем метаданные ---
            self._refresh_metadata()
            self.logger.info(f" Столбец '{actual_old}' успешно переименован в '{new_column_name}' в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка переименования '{table_name}.{old_column_name}': {self.format_db_error(e)}")
            return False

    def alter_column_type(self, table_name: str, column_name: str, new_type: str, using_expr: str = None):
        """
        Простое и надежное изменение типа столбца.
        Запрещает изменение типа для FK/PK столбцов.
        """
        if not self.is_connected():
            self.logger.error(" Нет подключения к базе данных.")
            return "Нет подключения к базе данных."

        try:
            new_type = (new_type or "").strip()
            if not new_type:
                return "Не указан новый тип столбца"

            insp = inspect(self.engine)
            if table_name not in insp.get_table_names():
                self.logger.error(f" Таблица '{table_name}' не найдена.")
                return f"Таблица '{table_name}' не найдена."

            # Проверяем наличие колонки
            columns = [c['name'] for c in insp.get_columns(table_name)]
            if column_name not in columns:
                self.logger.error(f" Колонка '{column_name}' не найдена в '{table_name}'.")
                return f"Колонка '{column_name}' не найдена в '{table_name}'."

            with self.engine.begin() as conn:
                # =====================================================
                # 🔎 Проверка ограничений - запрещаем изменение типа для FK/PK
                # =====================================================
                
                # Проверяем PRIMARY KEY
                pk_check = conn.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = :tbl AND kcu.column_name = :col
                """), {"tbl": table_name, "col": column_name}).first()
                
                # Проверяем FOREIGN KEY
                fk_check = conn.execute(text("""
                    SELECT 1 FROM information_schema.key_column_usage
                    WHERE column_name = :col AND table_name = :tbl AND position_in_unique_constraint IS NOT NULL
                """), {"tbl": table_name, "col": column_name}).first()

                # Запрещаем изменение типа для FK/PK столбцов
                if pk_check:
                    return "Невозможно изменить тип: столбец является PRIMARY KEY"
                if fk_check:
                    return "Невозможно изменить тип: столбец является FOREIGN KEY"

                # =====================================================
                # 🎯 Обработка типов
                # =====================================================
                
                # Получаем текущий тип столбца
                current_type_info = conn.execute(text("""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = :tbl AND column_name = :col
                """), {"tbl": table_name, "col": column_name}).first()
                
                if not current_type_info:
                    return f"Не удалось получить информацию о типе столбца '{column_name}'"
                
                current_type = current_type_info[0].upper()
                
                # Обработка __AUTO_ENUM__ - создаем автоматический ENUM
                if new_type == "__AUTO_ENUM__":
                    # Получаем уникальные значения из столбца
                    unique_values = conn.execute(text(f"""
                        SELECT DISTINCT "{column_name}" FROM "{table_name}" 
                        WHERE "{column_name}" IS NOT NULL ORDER BY "{column_name}"
                    """)).fetchall()
                    
                    if not unique_values:
                        return "Нельзя создать ENUM из пустого столбца"
                    
                    # Создаем ENUM с уникальными значениями
                    enum_values = []
                    for val in unique_values:
                        if val[0] is not None:
                            # Экранируем одинарные кавычки
                            escaped_val = str(val[0]).replace("'", "''")
                            enum_values.append(f"'{escaped_val}'")
                    
                    enum_name = f"enum_{table_name}_{column_name}"
                    
                    # Создаём ENUM-тип
                    create_enum_sql = f"CREATE TYPE {enum_name} AS ENUM ({', '.join(enum_values)});"
                    self.logger.info(f" Создание ENUM-типа: {enum_name}")
                    conn.execute(text(create_enum_sql))
                    
                    # Простое USING выражение - всегда через text
                    using_expr = f'"{column_name}"::text::{enum_name}'
                    alter_sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE {enum_name} USING {using_expr};'
                
                # Обработка обычных типов
                else:
                    # Простые USING выражения для основных типов
                    if not using_expr:
                        if current_type in ['INTEGER', 'BIGINT', 'SMALLINT', 'NUMERIC', 'DECIMAL', 'FLOAT', 'REAL', 'DOUBLE']:
                            if new_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                                using_expr = f'"{column_name}"::text'
                            else:
                                using_expr = f'"{column_name}"::{new_type}'
                        elif current_type == 'BOOLEAN':
                            if new_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                                using_expr = f'CASE WHEN "{column_name}" THEN \'true\' ELSE \'false\' END'
                            else:
                                using_expr = f'"{column_name}"::{new_type}'
                        else:
                            using_expr = f'"{column_name}"::{new_type}'
                    
                    alter_sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE {new_type}'
                    if using_expr:
                        alter_sql += f' USING {using_expr}'
                    alter_sql += ';'

                # =====================================================
                # 🚀 Выполнение изменения
                # =====================================================
                self.logger.info(f"Изменение типа: '{table_name}.{column_name}' → '{new_type}'")
                self.logger.debug(f"SQL: {alter_sql}")
                conn.execute(text(alter_sql))

            # Обновляем метаданные
            self._refresh_metadata()
            self.logger.info(f" Тип столбца '{column_name}' успешно изменён на '{new_type}' в '{table_name}'.")
            return True

        except Exception as e:
            error_msg = f"Ошибка изменения типа столбца '{table_name}.{column_name}': {self.format_db_error(e)}"
            self.logger.error(f" {error_msg}")
            return error_msg

    def set_column_nullable(self, table_name: str, column_name: str, nullable: bool) -> bool:
        """Устанавливает возможность NULL для столбца."""
        if not self.is_connected():
            self.logger.error(" Нет подключения к БД.")
            return False

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f" Таблица '{table_name}' не существует.")
                return False

            columns = self.get_column_names(table_name)
            if column_name not in columns:
                self.logger.error(f" Столбец '{column_name}' не найден в '{table_name}'.")
                return False

            # Проверяем, есть ли NULL значения, если пытаемся сделать NOT NULL
            if not nullable:
                with self.engine.connect() as conn:
                    null_count = conn.execute(text(
                        f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column_name}" IS NULL'
                    )).scalar() or 0
                    
                    if null_count > 0:
                        self.logger.error(f"  Невозможно установить NOT NULL: найдено {null_count} NULL значений.")
                        return False

            # Выполняем изменение
            action = "DROP NOT NULL" if nullable else "SET NOT NULL"
            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" {action};'
            self.logger.info(f"{action} для столбца '{table_name}.{column_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f" Столбец '{column_name}' успешно изменён в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f"  Ошибка изменения NULL для '{table_name}.{column_name}': {self.format_db_error(e)}")
            return False

    def set_column_default(self, table_name: str, column_name: str, default_value: Any) -> bool:
        """Устанавливает значение по умолчанию для столбца."""
        if not self.is_connected():
            self.logger.error("  Нет подключения к БД.")
            return False

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"  Таблица '{table_name}' не существует.")
                return False

            columns = self.get_column_names(table_name)
            if column_name not in columns:
                self.logger.error(f"  Столбец '{column_name}' не найден в '{table_name}'.")
                return False

            # Формируем SQL для установки DEFAULT
            if default_value is None:
                sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" DROP DEFAULT;'
            else:
                if isinstance(default_value, str):
                    default_str = f"'{default_value}'"
                else:
                    default_str = str(default_value)
                sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET DEFAULT {default_str};'

            self.logger.info(f"Установка DEFAULT для столбца '{table_name}.{column_name}'")
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f" DEFAULT для столбца '{column_name}' успешно установлен в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f"  Ошибка установки DEFAULT для '{table_name}.{column_name}': {self.format_db_error(e)}")
            return False

