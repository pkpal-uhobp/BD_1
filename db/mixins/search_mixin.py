"""
Миксин для поиска и фильтрации данных
"""

import logging
from sqlalchemy import func, select, asc, desc, text, inspect
from typing import List, Dict, Any, Optional


class SearchMixin:
    """Миксин для поиска и фильтрации данных"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
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
        search_query: str,
        search_type: str = "LIKE",
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Универсальный поиск по столбцу для любых типов данных.
        Поддерживает все типы: строки, числа, даты, boolean, enum, array, json и др.
        """
        if not self.is_connected():
            return []

        try:
            # Экранируем поисковый запрос для безопасности
            escaped_query = search_query.replace("'", "''")
            
            # Определяем тип поиска
            search_type = search_type.upper()
            if search_type == "LIKE" and not case_sensitive:
                search_type = "ILIKE"
            elif search_type == "NOT_LIKE" and not case_sensitive:
                search_type = "NOT_ILIKE"

            # Формируем SQL запрос в зависимости от типа поиска
            if search_type == "LIKE":
                # Чувствительный к регистру LIKE (без автоматических %)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text LIKE \'{escaped_query}\''
            elif search_type == "ILIKE":
                # Нечувствительный к регистру ILIKE (без автоматических %)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text ILIKE \'{escaped_query}\''
            elif search_type == "NOT_LIKE":
                # НЕ LIKE (чувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text NOT LIKE \'{escaped_query}\''
            elif search_type == "NOT_ILIKE":
                # НЕ ILIKE (нечувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text NOT ILIKE \'{escaped_query}\''
            elif search_type == "REGEX":
                # Регулярное выражение (чувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text ~ \'{escaped_query}\''
            elif search_type == "IREGEX":
                # Регулярное выражение (нечувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text ~* \'{escaped_query}\''
            elif search_type == "NOT_REGEX":
                # НЕ регулярное выражение (чувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text !~ \'{escaped_query}\''
            elif search_type == "NOT_IREGEX":
                # НЕ регулярное выражение (нечувствительный к регистру)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text !~* \'{escaped_query}\''
            else:
                # По умолчанию используем ILIKE (без автоматических %)
                sql_query = f'SELECT * FROM "{table_name}" WHERE "{column_name}"::text ILIKE \'{escaped_query}\''

            self.logger.info(f" Поиск в '{table_name}.{column_name}' ({search_type}) с запросом '{search_query}'")
            self.logger.info(f"📝 SQL: {sql_query}")

            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                rows = [dict(row._mapping) for row in result]

            self.logger.info(f" Найдено {len(rows)} строк по '{search_query}' ({search_type})")
            return rows

        except Exception as e:
            self.logger.error(f"Ошибка текстового поиска: {self.format_db_error(e)}")
            return []
    

    def text_search_advanced(self, table_name: str, column_name: str, search_query: str, 
                   search_type: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Выполняет поиск по тексту в указанном столбце таблицы.
        
        Args:
            table_name: Имя таблицы
            column_name: Имя столбца для поиска
            search_query: Поисковый запрос
            search_type: Тип поиска (LIKE, SIMILAR_TO, NOT_SIMILAR_TO, ~, ~*, !~, !~*)
            case_sensitive: Учитывать ли регистр (только для LIKE)
            
        Returns:
            Список словарей с найденными записями
        """
        if not self.is_connected():
            self.logger.error(" Нет подключения к базе данных")
            return []
            
        try:
            # Проверяем существование таблицы через inspect
            insp = inspect(self.engine)
            if table_name not in insp.get_table_names():
                self.logger.error(f" Таблица '{table_name}' не найдена")
                return []
            
            # Проверяем существование столбца
            columns = [col['name'] for col in insp.get_columns(table_name)]
            if column_name not in columns:
                self.logger.error(f" Столбец '{column_name}' не найден в таблице '{table_name}'")
                return []
            
            # Формируем SQL запрос в зависимости от типа поиска
            # Преобразуем столбец в текст для универсального поиска
            # Используем COALESCE для обработки NULL значений
            column_as_text = f'COALESCE(CAST("{column_name}" AS TEXT), \'\')'
            
            if search_type == "SIMILAR_TO":
                # SIMILAR TO поиск (SQL standard regex)
                where_clause = f'{column_as_text} SIMILAR TO :search_query'
                escaped_query = search_query
                
            elif search_type == "NOT_SIMILAR_TO":
                # NOT SIMILAR TO поиск
                where_clause = f'{column_as_text} NOT SIMILAR TO :search_query'
                escaped_query = search_query
                
            elif "LIKE" in search_type:
                # LIKE поиск
                if case_sensitive:
                    # Чувствительный к регистру
                    where_clause = f'{column_as_text} LIKE :search_query'
                else:
                    # Нечувствительный к регистру
                    where_clause = f'LOWER({column_as_text}) LIKE LOWER(:search_query)'
                    
                # Экранируем специальные символы для LIKE
                escaped_query = search_query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
                
            elif "~" in search_type:
                # POSIX регулярные выражения
                if "!~" in search_type:
                    # НЕ соответствует регулярному выражению
                    if "*" in search_type:
                        # Нечувствительный к регистру
                        where_clause = f'{column_as_text} !~* :search_query'
                    else:
                        # Чувствительный к регистру
                        where_clause = f'{column_as_text} !~ :search_query'
                else:
                    # Соответствует регулярному выражению
                    if "*" in search_type:
                        # Нечувствительный к регистру
                        where_clause = f'{column_as_text} ~* :search_query'
                    else:
                        # Чувствительный к регистру
                        where_clause = f'{column_as_text} ~ :search_query'
                        
                escaped_query = search_query
            else:
                self.logger.error(f" Неподдерживаемый тип поиска: {search_type}")
                return []
            
            # Формируем полный SQL запрос
            sql_query = f'SELECT * FROM "{table_name}" WHERE {where_clause}'
            
            self.logger.info(f" Выполняется поиск: {sql_query} с параметром: {escaped_query}")
            
            # Выполняем запрос
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query), {"search_query": escaped_query})
                rows = result.fetchall()
                
                # Преобразуем результат в список словарей
                columns = result.keys()
                results = []
                
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Обрабатываем специальные типы данных
                        if hasattr(value, 'isoformat'):  # datetime/date
                            value = value.isoformat()
                        elif isinstance(value, (list, tuple)):  # массивы
                            value = list(value)
                        row_dict[col] = value
                    results.append(row_dict)
                
                self.logger.info(f" Найдено {len(results)} записей")
                return results
                
        except Exception as e:
            self.logger.error(f" Ошибка поиска по тексту: {self.format_db_error(e)}")
            return []

    def execute_custom_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Выполняет произвольный SQL запрос и возвращает результаты.
        
        Args:
            sql_query: SQL запрос для выполнения
            
        Returns:
            Список словарей с результатами запроса
        """
        if not self.is_connected():
            self.logger.error(" Нет подключения к базе данных")
            return []
            
        try:
            self.logger.info(f" Выполняется SQL запрос: {sql_query}")
            
            # Выполняем запрос
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                rows = result.fetchall()
                
                # Преобразуем результат в список словарей
                columns = result.keys()
                results = []
                
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Обрабатываем специальные типы данных
                        if hasattr(value, 'isoformat'):  # datetime/date
                            value = value.isoformat()
                        elif isinstance(value, (list, tuple)):  # массивы
                            value = list(value)
                        elif isinstance(value, (int, float)):  # числа
                            value = value
                        elif value is None:
                            value = None
                        else:
                            value = str(value)
                        row_dict[col] = value
                    results.append(row_dict)
                
                self.logger.info(f" Запрос выполнен успешно. Найдено {len(results)} записей")
                return results
                
        except Exception as e:
            self.logger.error(f" Ошибка выполнения SQL запроса: {self.format_db_error(e)}")
            return []

    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Возвращает информацию о внешних ключах для указанной таблицы.
        """
        if not self.is_connected():
            return []

        try:
            if not self.record_exists_ex_table(table_name):
                self.logger.error(f"Таблица '{table_name}' не существует")
                return []

            insp = inspect(self.engine)
            foreign_keys = []

            for fk in insp.get_foreign_keys(table_name):
                foreign_keys.append({
                    "name": fk.get("name"),
                    "constrained_columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", []),
                    "ondelete": fk.get("ondelete"),
                    "onupdate": fk.get("onupdate")
                })

            self.logger.info(f"Найдено {len(foreign_keys)} внешних ключей в '{table_name}'")
            return foreign_keys

        except Exception as e:
            self.logger.error(f"Ошибка получения внешних ключей для '{table_name}': {self.format_db_error(e)}")
            return []

    def get_joined_summary(
            self,
            left_table: str = None,
            right_table: str = None,
            table1: str = None,
            table2: str = None,
            join_on: str = None,
            join_condition: str = None,
            join_type: str = "INNER",
            columns: List[str] = None,
            sort_columns: List[tuple] = None,
            order_by: List[tuple] = None,
            where_conditions: Dict[str, Any] = None,
            limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Выполняет JOIN между двумя таблицами с возможностью фильтрации и сортировки.
        """
        if not self.is_connected():
            return []

        try:
            # Определяем имена таблиц (поддержка старых и новых параметров)
            table1_name = left_table or table1
            table2_name = right_table or table2
            
            if not table1_name or not table2_name:
                self.logger.error("Не указаны имена таблиц для соединения")
                return []
                
            if not self.record_exists_ex_table(table1_name) or not self.record_exists_ex_table(table2_name):
                self.logger.error("Одна или обе таблицы не существуют")
                return []

            # Используем предопределенные соединения или пользовательское условие
            if join_on:
                # Обрабатываем join_on как список кортежей или строку
                if isinstance(join_on, list):
                    # Если это список кортежей, формируем условие JOIN
                    join_conditions = []
                    for col1, col2 in join_on:
                        join_conditions.append(f'"{table1_name}"."{col1}" = "{table2_name}"."{col2}"')
                    join_clause = " AND ".join(join_conditions)
                else:
                    # Если это строка, используем как есть
                    join_clause = join_on
            elif join_condition:
                join_clause = join_condition
            else:
                predefined_joins = self.get_predefined_joins()
                join_key = (table1_name, table2_name)
                if join_key not in predefined_joins:
                    self.logger.error(f"Не найдено предопределенное соединение между '{table1_name}' и '{table2_name}'")
                    return []
                
                col1, col2 = predefined_joins[join_key]
                join_clause = f'"{table1_name}"."{col1}" = "{table2_name}"."{col2}"'

            # Формируем SELECT
            if columns:
                # Обрабатываем колонки с префиксами t1/t2
                processed_columns = []
                for col in columns:
                    if col.startswith("t1."):
                        # Заменяем t1 на реальное имя левой таблицы
                        col_name = col[3:]  # убираем "t1."
                        processed_columns.append(f'"{table1_name}"."{col_name}"')
                    elif col.startswith("t2."):
                        # Заменяем t2 на реальное имя правой таблицы
                        col_name = col[3:]  # убираем "t2."
                        processed_columns.append(f'"{table2_name}"."{col_name}"')
                    else:
                        # Если колонка уже содержит имя таблицы, используем как есть
                        processed_columns.append(f'"{col}"')
                select_clause = ", ".join(processed_columns)
            else:
                select_clause = f'"{table1_name}".*, "{table2_name}".*'

            # Базовый запрос с поддержкой типа соединения
            join_keyword = join_type.upper() if join_type else "INNER"
            sql = f'SELECT {select_clause} FROM "{table1_name}" {join_keyword} JOIN "{table2_name}" ON {join_clause}'

            # WHERE условия
            if where_conditions:
                where_clauses = []
                for col, val in where_conditions.items():
                    if "." in col:
                        where_clauses.append(f'"{col}" = :{col.replace(".", "_")}')
                    else:
                        where_clauses.append(f'"{table1_name}"."{col}" = :{col}')
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            # ORDER BY (поддержка sort_columns и order_by)
            order_columns = sort_columns or order_by
            if order_columns:
                order_clauses = []
                for col, asc in order_columns:
                    # Обрабатываем колонки с префиксами t1/t2
                    if col.startswith("t1."):
                        col_name = col[3:]  # убираем "t1."
                        order_clauses.append(f'"{table1_name}"."{col_name}" {"ASC" if asc else "DESC"}')
                    elif col.startswith("t2."):
                        col_name = col[3:]  # убираем "t2."
                        order_clauses.append(f'"{table2_name}"."{col_name}" {"ASC" if asc else "DESC"}')
                    elif "." in col:
                        order_clauses.append(f'"{col}" {"ASC" if asc else "DESC"}')
                    else:
                        # Если колонка без префикса, пытаемся определить к какой таблице она принадлежит
                        # Сначала проверяем левую таблицу, потом правую
                        if self.record_exists_ex_table(table1_name):
                            table1_cols = self.get_table_columns(table1_name)
                            if isinstance(table1_cols, list) and len(table1_cols) > 0:
                                if isinstance(table1_cols[0], dict):
                                    table1_col_names = [col['name'] for col in table1_cols]
                                else:
                                    table1_col_names = table1_cols
                                if col in table1_col_names:
                                    order_clauses.append(f'"{table1_name}"."{col}" {"ASC" if asc else "DESC"}')
                                    continue
                        
                        if self.record_exists_ex_table(table2_name):
                            table2_cols = self.get_table_columns(table2_name)
                            if isinstance(table2_cols, list) and len(table2_cols) > 0:
                                if isinstance(table2_cols[0], dict):
                                    table2_col_names = [col['name'] for col in table2_cols]
                                else:
                                    table2_col_names = table2_cols
                                if col in table2_col_names:
                                    order_clauses.append(f'"{table2_name}"."{col}" {"ASC" if asc else "DESC"}')
                                    continue
                        
                        # Если не найдена ни в одной таблице, используем левую по умолчанию
                        order_clauses.append(f'"{table1_name}"."{col}" {"ASC" if asc else "DESC"}')
                if order_clauses:
                    sql += " ORDER BY " + ", ".join(order_clauses)

            # LIMIT
            if limit:
                sql += f" LIMIT {limit}"

            self.logger.info(f"Выполнение JOIN: {sql}")
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), where_conditions or {})
                rows = [dict(row._mapping) for row in result]

            self.logger.info(f"Получено {len(rows)} строк из JOIN")
            return rows

        except Exception as e:
            self.logger.error(f"Ошибка выполнения JOIN: {self.format_db_error(e)}")
            return []
