"""
Миксин для работы с ограничениями базы данных
"""

import logging
from sqlalchemy import inspect, text
from typing import List, Dict, Any, Tuple
import re


class ConstraintsMixin:
    """Миксин для работы с ограничениями базы данных"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
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

            #  Универсальные шаблоны для трёх типов ограничений
            match constraint_type:
                case "CHECK":
                    cond = kwargs.get("check_condition")
                    if not cond:
                        self.logger.error(" Для CHECK-ограничения необходимо указать параметр 'check_condition'")
                        return False
                    sql += f"CHECK ({cond})"

                case "UNIQUE":
                    cols = kwargs.get("columns")
                    if not cols:
                        self.logger.error(" Для UNIQUE необходимо указать 'columns'")
                        return False
                    cols_str = ", ".join(f'"{c}"' for c in (cols if isinstance(cols, list) else [cols]))
                    sql += f"UNIQUE ({cols_str})"

                case "FOREIGN_KEY":
                    cols = kwargs.get("columns")
                    ref_table = kwargs.get("foreign_table")
                    ref_cols = kwargs.get("foreign_columns")

                    if not all([cols, ref_table, ref_cols]):
                        self.logger.error(" Для FOREIGN KEY нужны 'columns', 'foreign_table' и 'foreign_columns'")
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
            self.logger.info(f" Ограничение '{constraint_name}' успешно добавлено к '{table_name}'")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f" Ошибка добавления ограничения: {msg}")
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
                self.logger.warning(f" Ограничение '{constraint_name}' не найдено — возможно, оно уже удалено")
                return False

            sql = f'ALTER TABLE "{table_name}" DROP CONSTRAINT "{constraint_name}";'
            self.logger.debug(f"SQL → {sql}")

            with self.engine.begin() as conn:
                conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f" Ограничение '{constraint_name}' успешно удалено из '{table_name}'")
            return True

        except Exception as e:
            msg = self.format_db_error(e)
            self.logger.error(f" Ошибка удаления ограничения '{constraint_name}': {msg}")
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
            from sqlalchemy import String, Numeric, Enum, ARRAY
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
            self.logger.warning(" Метаданные таблиц не загружены. Невозможно сгенерировать соединения.")
            return predefined_joins

        for table in self.tables.values():
            for fk in table.foreign_keys:
                # Получаем имена таблиц
                parent_table = fk.column.table.name
                child_table = table.name
                
                # Получаем имена колонок
                parent_column = fk.column.name
                child_column = fk.parent.name
                
                # Создаем записи для обоих направлений соединения
                predefined_joins[(child_table, parent_table)] = (child_column, parent_column)
                predefined_joins[(parent_table, child_table)] = (parent_column, child_column)

        self.logger.info(f"Сгенерировано {len(predefined_joins)} предопределенных соединений")
        return predefined_joins

    def alter_column_constraints(self, table_name: str, column_name: str,
                                nullable: bool = None, default: Any = None,
                                check_condition: str = None) -> bool:
        """
        Изменяет ограничения столбца: NULL/NOT NULL, DEFAULT, CHECK.
        """
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

            with self.engine.begin() as conn:
                # Изменение NULL/NOT NULL
                if nullable is not None:
                    if not nullable:
                        # Проверяем наличие NULL значений
                        null_count = conn.execute(text(
                            f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column_name}" IS NULL'
                        )).scalar() or 0
                        
                        if null_count > 0:
                            self.logger.error(f" Невозможно установить NOT NULL: найдено {null_count} NULL значений.")
                            return False

                    action = "DROP NOT NULL" if nullable else "SET NOT NULL"
                    sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" {action};'
                    self.logger.info(f"{action} для столбца '{table_name}.{column_name}'")
                    conn.execute(text(sql))

                # Изменение DEFAULT
                if default is not None:
                    if default is None:
                        sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" DROP DEFAULT;'
                    else:
                        if isinstance(default, str) and not default.upper().startswith(("CURRENT_", "NEXTVAL(")):
                            default_sql = f"'{default}'"
                        else:
                            default_sql = str(default)
                        sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET DEFAULT {default_sql};'
                    
                    self.logger.info(f"Изменение DEFAULT для столбца '{table_name}.{column_name}'")
                    conn.execute(text(sql))

                # Добавление CHECK ограничения
                if check_condition:
                    constraint_name = f'chk_{table_name}_{column_name}'
                    sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" CHECK ({check_condition});'
                    self.logger.info(f"Добавление CHECK ограничения для столбца '{table_name}.{column_name}'")
                    conn.execute(text(sql))

            self._refresh_metadata()
            self.logger.info(f" Ограничения столбца '{column_name}' успешно изменены в '{table_name}'.")
            return True

        except Exception as e:
            self.logger.error(f" Ошибка изменения ограничений столбца '{table_name}.{column_name}': {self.format_db_error(e)}")
            return False
