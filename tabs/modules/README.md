# Модульная структура диалоговых окон

Диалоговые окна организованы по функциональным группам для лучшей структуры и поддержки кода.

## Структура модулей

```
tabs/
├── menu.py                    # Главное меню приложения
└── modules/
    ├── __init__.py           # Инициализация модулей
    ├── README.md             # Документация модулей
    ├── data_operations/      # CRUD операции с данными
    │   ├── __init__.py
    │   ├── add_dialog.py     # Добавление записей
    │   ├── update_dialog.py  # Редактирование записей
    │   ├── delete_dialog.py  # Удаление записей
    │   └── get_table.py      # Просмотр таблиц
    ├── table_operations/     # Операции с таблицами
    │   ├── __init__.py
    │   ├── add_column.py     # Добавление столбцов
    │   ├── drop_column_dialog.py  # Удаление столбцов
    │   ├── rename_dialog.py  # Переименование
    │   └── change_type_dialog.py  # Изменение типов
    ├── search_operations/    # Операции поиска
    │   ├── __init__.py
    │   ├── text_search_dialog.py      # Текстовый поиск
    │   └── advanced_select_dialog.py  # Расширенный SELECT
    ├── string_operations/    # Строковые операции
    │   ├── __init__.py
    │   └── string_functions_dialog.py # Строковые функции
    └── constraints/          # Ограничения
        ├── __init__.py
        ├── constraints_basic_dialog.py        # Базовые ограничения
        └── constraints_dialog_standalone.py   # Автономные ограничения
```

## Группы диалогов

### 1. Data Operations (Операции с данными)

**Назначение:** CRUD операции с записями в таблицах

**Диалоги:**

-   `AddRecordDialog` - добавление новых записей
-   `EditRecordDialog` - редактирование существующих записей
-   `DeleteRecordDialog` - удаление записей
-   `ShowTableDialog` - просмотр содержимого таблиц

**Импорт:**

```python
from tabs.modules.data_operations import AddRecordDialog, EditRecordDialog, DeleteRecordDialog, ShowTableDialog
```

### 2. Table Operations (Операции с таблицами)

**Назначение:** Управление структурой таблиц и столбцов

**Диалоги:**

-   `AddColumnDialog` - добавление новых столбцов
-   `ConstraintsDialog` - управление ограничениями столбцов
-   `DropColumnDialog` - удаление столбцов
-   `RenameDialog` - переименование таблиц и столбцов
-   `ChangeTypeDialog` - изменение типов данных столбцов

**Импорт:**

```python
from tabs.modules.table_operations import AddColumnDialog, DropColumnDialog, RenameDialog, ChangeTypeDialog
```

### 3. Search Operations (Операции поиска)

**Назначение:** Поиск и фильтрация данных

**Диалоги:**

-   `TextSearchDialog` - текстовый поиск по таблицам
-   `AdvancedSelectDialog` - расширенные SELECT запросы
-   `AggregateFunctionDialog` - агрегатные функции

**Импорт:**

```python
from tabs.modules.search_operations import TextSearchDialog, AdvancedSelectDialog, AggregateFunctionDialog
```

### 4. String Operations (Строковые операции)

**Назначение:** Работа со строковыми функциями PostgreSQL

**Диалоги:**

-   `StringFunctionsDialog` - UPPER, LOWER, SUBSTRING, TRIM, LPAD, RPAD, CONCAT

**Импорт:**

```python
from tabs.modules.string_operations import StringFunctionsDialog
```

### 5. Constraints (Ограничения)

**Назначение:** Управление ограничениями базы данных

**Диалоги:**

-   `ConstraintsBasicDialog` - базовые ограничения
-   `ConstraintsDialogStandalone` - автономные ограничения

**Импорт:**

```python
from tabs.modules.constraints import ConstraintsBasicDialog, ConstraintsDialogStandalone
```

## Преимущества модульной структуры

### 1. Логическая организация

-   Диалоги сгруппированы по функциональности
-   Легко найти нужный диалог
-   Понятная структура проекта

### 2. Упрощенная навигация

-   Четкое разделение ответственности
-   Быстрый доступ к нужным компонентам
-   Улучшенная читаемость кода

### 3. Модульность

-   Каждая группа может развиваться независимо
-   Легко добавлять новые диалоги
-   Простое тестирование отдельных модулей

### 4. Переиспользование

-   Модули можно использовать в других проектах
-   Стандартизированные интерфейсы
-   Гибкая архитектура

### 5. Поддержка

-   Изолированные изменения
-   Меньше конфликтов при разработке
-   Простое сопровождение кода

## Использование

### Импорт конкретного диалога

```python
from tabs.modules.data_operations import AddRecordDialog

dialog = AddRecordDialog(db_instance, parent=self)
dialog.exec()
```

### Импорт всех диалогов группы

```python
from tabs.modules.data_operations import *

# Теперь доступны все диалоги группы
dialog = AddRecordDialog(db_instance, parent=self)
```

### Импорт из разных групп

```python
from tabs.modules.data_operations import AddRecordDialog
from tabs.modules.search_operations import TextSearchDialog
from tabs.modules.string_operations import StringFunctionsDialog
```

## Миграция

Все импорты в `menu.py` обновлены для работы с новой структурой:

**Было:**

```python
from tabs.add_dialog import AddRecordDialog
from tabs.text_search_dialog import TextSearchDialog
```

**Стало:**

```python
from tabs.modules.data_operations import AddRecordDialog
from tabs.modules.search_operations import TextSearchDialog
```

## Статистика

| Группа            | Количество диалогов | Основная функция            |
| ----------------- | ------------------- | --------------------------- |
| Data Operations   | 4                   | CRUD операции               |
| Table Operations  | 4                   | Управление структурой       |
| Search Operations | 3                   | Поиск и фильтрация          |
| String Operations | 1                   | Строковые функции           |
| Constraints       | 2                   | Ограничения БД              |
| **Итого**         | **14**              | **Полная функциональность** |

## Совместимость

✅ **Полная обратная совместимость**  
✅ **Все функции работают как прежде**  
✅ **Улучшенная организация кода**  
✅ **Готово к расширению**
