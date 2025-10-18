# Миксины для класса DB

Этот каталог содержит миксины для организации функциональности класса DB. Каждый миксин отвечает за определенную область функциональности.

## Структура миксинов

### 1. ConnectionMixin (`connection_mixin.py`)

**Назначение**: Подключение к базе данных и базовые операции

**Методы**:

-   `format_db_error(error)` - форматирование ошибок БД
-   `connect()` - подключение к БД
-   `disconnect()` - отключение от БД
-   `is_connected()` - проверка состояния подключения

### 2. MetadataMixin (`metadata_mixin.py`)

**Назначение**: Работа с метаданными и схемой базы данных

**Методы**:

-   `_build_metadata()` - построение метаданных таблиц
-   `create_schema()` - создание схемы БД
-   `drop_schema()` - удаление схемы БД
-   `get_table_names()` - получение списка таблиц
-   `get_column_names(table_name)` - получение списка колонок
-   `get_column_info(table_name, column_name)` - информация о колонке
-   `_refresh_metadata()` - обновление метаданных

### 3. CrudMixin (`crud_mixin.py`)

**Назначение**: CRUD операции (Create, Read, Update, Delete)

**Методы**:

-   `get_table_data(table_name)` - получение всех данных таблицы
-   `insert_data(table_name, data)` - вставка данных
-   `update_data(table_name, condition, new_values)` - обновление данных
-   `delete_data(table_name, condition)` - удаление данных
-   `record_exists(table_name, condition)` - проверка существования записи
-   `_validate_data(table_name, data)` - валидация данных
-   `_check_foreign_key_exists(table_name, column_name, value)` - проверка внешних ключей
-   `get_sorted_data(...)` - получение отсортированных данных
-   `execute_query(query, params, fetch)` - выполнение SQL запросов
-   `count_records_filtered(table_name, condition)` - подсчет записей с фильтрацией

### 4. TableOperationsMixin (`table_operations_mixin.py`)

**Назначение**: Операции с таблицами (добавление/удаление колонок, переименование)

**Методы**:

-   `add_column(table_name, column_name, column_type, **kwargs)` - добавление колонки
-   `drop_column_safe(table_name, column_name, force)` - безопасное удаление колонки
-   `rename_table(old_name, new_name)` - переименование таблицы
-   `rename_column(table_name, old_name, new_name)` - переименование колонки
-   `alter_column_type(table_name, column_name, new_type, using_expr)` - изменение типа колонки
-   `set_column_nullable(table_name, column_name, nullable)` - установка NULL/NOT NULL
-   `set_column_default(table_name, column_name, default_value)` - установка значения по умолчанию
-   `get_column_dependencies(table_name, column_name)` - получение зависимостей колонки

### 5. ConstraintsMixin (`constraints_mixin.py`)

**Назначение**: Работа с ограничениями базы данных

**Методы**:

-   `add_constraint(table_name, constraint_name, constraint_type, **kwargs)` - добавление ограничения
-   `drop_constraint(table_name, constraint_name)` - удаление ограничения
-   `get_table_constraints(table_name)` - получение ограничений таблицы
-   `get_column_constraints(table_name, column_name)` - получение ограничений колонки
-   `get_predefined_joins()` - получение предопределенных соединений
-   `alter_column_constraints(...)` - изменение ограничений колонки

### 6. SearchMixin (`search_mixin.py`)

**Назначение**: Поиск и фильтрация данных

**Методы**:

-   `select_with_filters(...)` - универсальный SELECT с фильтрами
-   `execute_aggregate_query(...)` - выполнение агрегатных запросов
-   `text_search(table_name, column_name, pattern, search_type)` - текстовый поиск
-   `text_search_advanced(...)` - расширенный текстовый поиск
-   `execute_custom_query(sql_query)` - выполнение произвольных SQL запросов
-   `get_foreign_keys(table_name)` - получение внешних ключей
-   `get_joined_summary(...)` - выполнение JOIN между таблицами

### 7. StringOperationsMixin (`string_operations_mixin.py`)

**Назначение**: Строковые операции

**Методы**:

-   `string_functions_demo(table_name, column_name, function_name, **params)` - демонстрация строковых функций
-   `substring_function(table_name, column_name, start, length)` - извлечение подстроки
-   `trim_functions(table_name, column_name, trim_type, characters)` - удаление пробелов/символов
-   `pad_functions(table_name, column_name, length, pad_string, pad_type)` - дополнение строк
-   `concat_operator(table_name, columns, separator)` - конкатенация строк
-   `replace_function(table_name, column_name, old_string, new_string)` - замена подстрок
-   `case_function(table_name, column_name, cases, default_value)` - CASE выражения
-   `position_function(table_name, column_name, substring)` - поиск позиции подстроки
-   `split_function(table_name, column_name, delimiter)` - разделение строк

## Использование

```python
from Class_DB_refactored import DB

# Создание экземпляра
db = DB(host="localhost", port=5432, dbname="library_db", user="postgres", password="root")

# Подключение
if db.connect():
    # Все методы доступны через единый интерфейс
    tables = db.get_table_names()  # из MetadataMixin
    data = db.get_table_data("Books")  # из CrudMixin
    results = db.text_search("Books", "title", "%роман%", "LIKE")  # из SearchMixin
    upper_results = db.string_functions_demo("Books", "title", "UPPER")  # из StringOperationsMixin

    db.disconnect()  # из ConnectionMixin
```

## Преимущества миксинов

1. **Модульность**: Каждый миксин отвечает за свою область функциональности
2. **Переиспользование**: Миксины можно использовать в других классах
3. **Читаемость**: Код легче читать и понимать
4. **Тестирование**: Каждый миксин можно тестировать отдельно
5. **Расширяемость**: Легко добавлять новые миксины или изменять существующие
6. **Организация**: Логическое разделение функциональности

## Порядок наследования

Класс DB наследует миксины в следующем порядке:

1. ConnectionMixin - базовые операции подключения
2. MetadataMixin - работа с метаданными
3. CrudMixin - CRUD операции
4. TableOperationsMixin - операции с таблицами
5. ConstraintsMixin - работа с ограничениями
6. SearchMixin - поиск и фильтрация
7. StringOperationsMixin - строковые операции

Этот порядок важен для правильного разрешения методов при конфликтах имен.
