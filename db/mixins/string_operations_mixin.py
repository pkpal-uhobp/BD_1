"""
Миксин для строковых операций
"""

import logging
from typing import List, Dict, Any
from sqlalchemy import text, Table, Column, Integer, String, DateTime, Text
from datetime import datetime


class StringOperationsMixin:
    """Миксин для строковых операций"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем логгер для этого миксина
        self.logger = logging.getLogger("DB")
    
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

    def substring_function(self, table_name: str, column_name: str, start: int, length: int = None) -> List[Dict[str, Any]]:
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

    def trim_functions(self, table_name: str, column_name: str, trim_type: str = "BOTH", characters: str = None) -> List[Dict[str, Any]]:
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

    def replace_function(self, table_name: str, column_name: str, old_string: str, new_string: str) -> List[Dict[str, Any]]:
        """
        Заменяет все вхождения подстроки в значениях указанного столбца.

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            old_string: Подстрока для замены
            new_string: Новая подстрока

        Returns:
            List[Dict]: Результаты с полем replace_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            
            # Экранируем специальные символы
            old_escaped = old_string.replace("'", "''")
            new_escaped = new_string.replace("'", "''")
            
            query = f"SELECT {col}, REPLACE({col}, '{old_escaped}', '{new_escaped}') AS replace_result FROM {table}"

            self.logger.info(f"Выполнение REPLACE для {table_name}.{column_name}: '{old_string}' -> '{new_string}'")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка выполнения REPLACE: {self.format_db_error(e)}")
            return []

    def case_function(self, table_name: str, column_name: str, cases: Dict[str, str], default_value: str = None) -> List[Dict[str, Any]]:
        """
        Выполняет CASE выражение для значений указанного столбца.

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            cases: Словарь {условие: результат}
            default_value: Значение по умолчанию

        Returns:
            List[Dict]: Результаты с полем case_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            
            # Формируем CASE выражение
            case_parts = []
            for condition, result in cases.items():
                case_parts.append(f"WHEN {condition} THEN '{result}'")
            
            case_expr = "CASE " + " ".join(case_parts)
            if default_value is not None:
                case_expr += f" ELSE '{default_value}'"
            case_expr += " END"
            
            query = f"SELECT {col}, {case_expr} AS case_result FROM {table}"

            self.logger.info(f"Выполнение CASE для {table_name}.{column_name}")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка выполнения CASE: {self.format_db_error(e)}")
            return []

    def position_function(self, table_name: str, column_name: str, substring: str) -> List[Dict[str, Any]]:
        """
        Находит позицию подстроки в значениях указанного столбца.

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            substring: Подстрока для поиска

        Returns:
            List[Dict]: Результаты с полем position_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            
            # Экранируем специальные символы
            substring_escaped = substring.replace("'", "''")
            
            query = f"SELECT {col}, POSITION('{substring_escaped}' IN {col}) AS position_result FROM {table}"

            self.logger.info(f"Выполнение POSITION для {table_name}.{column_name}: поиск '{substring}'")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка выполнения POSITION: {self.format_db_error(e)}")
            return []

    def split_function(self, table_name: str, column_name: str, delimiter: str = ' ') -> List[Dict[str, Any]]:
        """
        Разделяет строки по указанному разделителю.

        Args:
            table_name: Имя таблицы
            column_name: Имя колонки
            delimiter: Разделитель

        Returns:
            List[Dict]: Результаты с полем split_result
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            
            # Экранируем специальные символы
            delimiter_escaped = delimiter.replace("'", "''")
            
            query = f"SELECT {col}, STRING_TO_ARRAY({col}, '{delimiter_escaped}') AS split_result FROM {table}"

            self.logger.info(f"Выполнение STRING_TO_ARRAY для {table_name}.{column_name}: разделитель '{delimiter}'")

            result = self.execute_query(query, fetch="dict")
            self.logger.info(f"Результатов: {len(result) if result else 0}")

            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка выполнения STRING_TO_ARRAY: {self.format_db_error(e)}")
            return []

    def create_string_results_table(self, table_name: str = "string_function_results") -> bool:
        """
        Создает таблицу для сохранения результатов строковых функций.
        
        Args:
            table_name: Имя таблицы для результатов
            
        Returns:
            bool: True если таблица создана успешно
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            # Проверяем, существует ли таблица
            if self.record_exists_ex_table(table_name):
                self.logger.info(f"Таблица '{table_name}' уже существует")
                return True

            # Создаем таблицу для результатов строковых функций
            create_sql = f"""
            CREATE TABLE "{table_name}" (
                id SERIAL PRIMARY KEY,
                source_table VARCHAR(100) NOT NULL,
                source_column VARCHAR(100) NOT NULL,
                function_name VARCHAR(50) NOT NULL,
                function_params TEXT,
                original_value TEXT,
                result_value TEXT,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            self.logger.info(f"Создание таблицы результатов строковых функций: {table_name}")
            
            with self.engine.begin() as conn:
                conn.execute(text(create_sql))
            
            # Обновляем метаданные
            self._refresh_metadata()
            
            self.logger.info(f" Таблица '{table_name}' успешно создана")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания таблицы результатов: {self.format_db_error(e)}")
            return False

    def save_string_function_result(self, 
                                  source_table: str,
                                  source_column: str, 
                                  function_name: str,
                                  original_value: str,
                                  result_value: str,
                                  function_params: str = None,
                                  results_table: str = "string_function_results") -> bool:
        """
        Сохраняет результат выполнения строковой функции в таблицу результатов.
        
        Args:
            source_table: Исходная таблица
            source_column: Исходный столбец
            function_name: Название функции
            original_value: Исходное значение
            result_value: Результат функции
            function_params: Параметры функции (JSON строка)
            results_table: Таблица для сохранения результатов
            
        Returns:
            bool: True если результат сохранен успешно
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            # Убеждаемся, что таблица результатов существует
            if not self.record_exists_ex_table(results_table):
                if not self.create_string_results_table(results_table):
                    return False

            # Подготавливаем данные для вставки
            insert_sql = f"""
            INSERT INTO "{results_table}" 
            (source_table, source_column, function_name, function_params, original_value, result_value)
            VALUES (:source_table, :source_column, :function_name, :function_params, :original_value, :result_value)
            """
            
            params = {
                'source_table': source_table,
                'source_column': source_column,
                'function_name': function_name,
                'function_params': function_params or '',
                'original_value': str(original_value) if original_value is not None else '',
                'result_value': str(result_value) if result_value is not None else ''
            }
            
            with self.engine.begin() as conn:
                conn.execute(text(insert_sql), params)
            
            self.logger.info(f"Результат функции {function_name} сохранен в {results_table}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка сохранения результата: {self.format_db_error(e)}")
            return False

    def save_string_function_results_batch(self,
                                         source_table: str,
                                         source_column: str,
                                         function_name: str,
                                         results: List[Dict[str, Any]],
                                         function_params: str = None,
                                         results_table: str = "string_function_results") -> bool:
        """
        Сохраняет результаты выполнения строковой функции пакетом.
        
        Args:
            source_table: Исходная таблица
            source_column: Исходный столбец
            function_name: Название функции
            results: Список результатов с исходными и результирующими значениями
            function_params: Параметры функции (JSON строка)
            results_table: Таблица для сохранения результатов
            
        Returns:
            bool: True если результаты сохранены успешно
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        if not results:
            self.logger.warning("Нет результатов для сохранения")
            return True

        try:
            # Убеждаемся, что таблица результатов существует
            if not self.record_exists_ex_table(results_table):
                if not self.create_string_results_table(results_table):
                    return False

            # Подготавливаем данные для пакетной вставки
            insert_sql = f"""
            INSERT INTO "{results_table}" 
            (source_table, source_column, function_name, function_params, original_value, result_value)
            VALUES (:source_table, :source_column, :function_name, :function_params, :original_value, :result_value)
            """
            
            batch_data = []
            for result in results:
                # Определяем исходное и результирующее значение
                original_value = result.get(source_column, '')
                result_value = ''
                
                # Ищем результирующее значение по различным возможным ключам
                for key in result.keys():
                    if key != source_column and ('result' in key.lower() or 'output' in key.lower()):
                        result_value = result[key]
                        break
                
                # Если не нашли по ключу, берем последнее значение (обычно это результат)
                if not result_value and len(result) > 1:
                    values = list(result.values())
                    if len(values) >= 2:
                        result_value = values[1]  # Второе значение обычно результат
                
                batch_data.append({
                    'source_table': source_table,
                    'source_column': source_column,
                    'function_name': function_name,
                    'function_params': function_params or '',
                    'original_value': str(original_value) if original_value is not None else '',
                    'result_value': str(result_value) if result_value is not None else ''
                })
            
            # Выполняем пакетную вставку
            with self.engine.begin() as conn:
                conn.execute(text(insert_sql), batch_data)
            
            self.logger.info(f"Сохранено {len(batch_data)} результатов функции {function_name} в {results_table}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка пакетного сохранения результатов: {self.format_db_error(e)}")
            return False

    def get_string_function_results(self, 
                                  results_table: str = "string_function_results",
                                  function_name: str = None,
                                  source_table: str = None,
                                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получает сохраненные результаты строковых функций.
        
        Args:
            results_table: Таблица с результатами
            function_name: Фильтр по названию функции
            source_table: Фильтр по исходной таблице
            limit: Максимальное количество записей
            
        Returns:
            List[Dict]: Список результатов
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            # Проверяем существование таблицы
            if not self.record_exists_ex_table(results_table):
                self.logger.warning(f"Таблица '{results_table}' не существует")
                return []

            # Формируем запрос с фильтрами
            where_conditions = []
            params = {}
            
            if function_name:
                where_conditions.append("function_name = :function_name")
                params['function_name'] = function_name
                
            if source_table:
                where_conditions.append("source_table = :source_table")
                params['source_table'] = source_table
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
            SELECT id, source_table, source_column, function_name, function_params,
                   original_value, result_value, execution_time, created_at
            FROM "{results_table}"
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            params['limit'] = limit
            
            result = self.execute_query(query, fetch="dict", params=params)
            self.logger.info(f"Получено {len(result) if result else 0} записей из {results_table}")
            
            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка получения результатов: {self.format_db_error(e)}")
            return []

    def clear_string_function_results(self, 
                                    results_table: str = "string_function_results",
                                    function_name: str = None,
                                    source_table: str = None) -> bool:
        """
        Очищает сохраненные результаты строковых функций.
        
        Args:
            results_table: Таблица с результатами
            function_name: Фильтр по названию функции
            source_table: Фильтр по исходной таблице
            
        Returns:
            bool: True если очистка выполнена успешно
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            # Проверяем существование таблицы
            if not self.record_exists_ex_table(results_table):
                self.logger.warning(f"Таблица '{results_table}' не существует")
                return True

            # Формируем запрос с фильтрами
            where_conditions = []
            params = {}
            
            if function_name:
                where_conditions.append("function_name = :function_name")
                params['function_name'] = function_name
                
            if source_table:
                where_conditions.append("source_table = :source_table")
                params['source_table'] = source_table
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            delete_sql = f'DELETE FROM "{results_table}" {where_clause}'
            
            with self.engine.begin() as conn:
                result = conn.execute(text(delete_sql), params)
                deleted_count = result.rowcount
            
            self.logger.info(f"Удалено {deleted_count} записей из {results_table}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка очистки результатов: {self.format_db_error(e)}")
            return False

    def update_string_values_in_table(self, 
                                    table_name: str,
                                    column_name: str,
                                    function_name: str,
                                    **params) -> bool:
        """
        Обновляет значения в исходной таблице, применяя строковую функцию.
        
        Args:
            table_name: Имя таблицы
            column_name: Имя столбца
            function_name: Название функции
            **params: Параметры функции
            
        Returns:
            bool: True если обновление выполнено успешно
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return False

        try:
            # Формируем SQL для обновления
            update_sql = self._build_update_sql(table_name, column_name, function_name, **params)
            
            if not update_sql:
                self.logger.error(f"Не удалось сформировать SQL для функции {function_name}")
                return False
            
            self.logger.info(f"Обновление значений в {table_name}.{column_name} функцией {function_name}")
            self.logger.debug(f"SQL: {update_sql}")
            
            with self.engine.begin() as conn:
                result = conn.execute(text(update_sql))
                updated_count = result.rowcount
            
            self.logger.info(f" Обновлено {updated_count} записей в {table_name}.{column_name}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления значений: {self.format_db_error(e)}")
            return False

    def _build_update_sql(self, table_name: str, column_name: str, function_name: str, **params) -> str:
        """
        Строит SQL запрос для обновления значений в таблице.
        
        Args:
            table_name: Имя таблицы
            column_name: Имя столбца
            function_name: Название функции
            **params: Параметры функции
            
        Returns:
            str: SQL запрос для обновления
        """
        col = f'"{column_name}"'
        table = f'"{table_name}"'
        func = function_name.upper()
        
        # Формируем выражение функции
        function_expr = None
        
        if func == "UPPER":
            function_expr = f"UPPER({col})"
        elif func == "LOWER":
            function_expr = f"LOWER({col})"
        elif func == "TRIM":
            trim_type = params.get("trim_type", "BOTH")
            chars = params.get("chars")
            if chars:
                function_expr = f"TRIM({trim_type} '{chars}' FROM {col})"
            else:
                function_expr = f"TRIM({trim_type} FROM {col})"
        elif func == "SUBSTRING":
            start = params.get("start", 1)
            length = params.get("length")
            if length:
                function_expr = f"SUBSTRING({col} FROM {start} FOR {length})"
            else:
                function_expr = f"SUBSTRING({col} FROM {start})"
        elif func in ["LPAD", "RPAD"]:
            length = params.get("length", 10)
            pad_string = params.get("pad_string", " ")
            function_expr = f"{func}({col}, {length}, '{pad_string}')"
        elif func == "REPLACE":
            old_string = params.get("old_string", "")
            new_string = params.get("new_string", "")
            # Экранируем специальные символы
            old_escaped = old_string.replace("'", "''")
            new_escaped = new_string.replace("'", "''")
            function_expr = f"REPLACE({col}, '{old_escaped}', '{new_escaped}')"
        elif func == "CONCAT":
            concat_string = params.get("concat_string", "")
            concat_escaped = concat_string.replace("'", "''")
            function_expr = f"CONCAT({col}, '{concat_escaped}')"
        else:
            self.logger.error(f"Неподдерживаемая функция: {func}")
            return ""
        
        # Формируем полный UPDATE запрос
        update_sql = f'UPDATE {table} SET {col} = {function_expr} WHERE {col} IS NOT NULL'
        
        return update_sql

    def preview_string_function_update(self, 
                                     table_name: str,
                                     column_name: str,
                                     function_name: str,
                                     limit: int = 10,
                                     **params) -> List[Dict[str, Any]]:
        """
        Показывает предварительный просмотр изменений перед обновлением.
        
        Args:
            table_name: Имя таблицы
            column_name: Имя столбца
            function_name: Название функции
            limit: Количество записей для предварительного просмотра
            **params: Параметры функции
            
        Returns:
            List[Dict]: Список записей с исходными и новыми значениями
        """
        if not self.is_connected():
            self.logger.error("Нет подключения к БД")
            return []

        try:
            col = f'"{column_name}"'
            table = f'"{table_name}"'
            func = function_name.upper()
            
            # Формируем выражение функции
            function_expr = None
            
            if func == "UPPER":
                function_expr = f"UPPER({col})"
            elif func == "LOWER":
                function_expr = f"LOWER({col})"
            elif func == "TRIM":
                trim_type = params.get("trim_type", "BOTH")
                chars = params.get("chars")
                if chars:
                    function_expr = f"TRIM({trim_type} '{chars}' FROM {col})"
                else:
                    function_expr = f"TRIM({trim_type} FROM {col})"
            elif func == "SUBSTRING":
                start = params.get("start", 1)
                length = params.get("length")
                if length:
                    function_expr = f"SUBSTRING({col} FROM {start} FOR {length})"
                else:
                    function_expr = f"SUBSTRING({col} FROM {start})"
            elif func in ["LPAD", "RPAD"]:
                length = params.get("length", 10)
                pad_string = params.get("pad_string", " ")
                function_expr = f"{func}({col}, {length}, '{pad_string}')"
            elif func == "REPLACE":
                old_string = params.get("old_string", "")
                new_string = params.get("new_string", "")
                old_escaped = old_string.replace("'", "''")
                new_escaped = new_string.replace("'", "''")
                function_expr = f"REPLACE({col}, '{old_escaped}', '{new_escaped}')"
            elif func == "CONCAT":
                concat_string = params.get("concat_string", "")
                concat_escaped = concat_string.replace("'", "''")
                function_expr = f"CONCAT({col}, '{concat_escaped}')"
            else:
                self.logger.error(f"Неподдерживаемая функция: {func}")
                return []
            
            # Формируем запрос для предварительного просмотра
            preview_sql = f"""
            SELECT 
                {col} as original_value,
                {function_expr} as new_value
            FROM {table}
            WHERE {col} IS NOT NULL
            LIMIT {limit}
            """
            
            self.logger.info(f"Предварительный просмотр {func} для {table_name}.{column_name}")
            
            result = self.execute_query(preview_sql, fetch="dict")
            return result or []

        except Exception as e:
            self.logger.error(f"Ошибка предварительного просмотра: {self.format_db_error(e)}")
            return []
