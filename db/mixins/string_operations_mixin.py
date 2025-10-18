"""
Миксин для строковых операций
"""

import logging
from typing import List, Dict, Any


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
