from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTextEdit, QComboBox, QListWidget,
                             QCheckBox, QGroupBox, QMessageBox, QListWidgetItem,
                             QAbstractItemView, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter, QWidget, QSpinBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import re
from .aggregate_functions_dialog import AggregateFunctionsDialog
from .date_functions_dialog import DateFunctionsDialog
from .string_functions_dialog import StringFunctionsDialog
from .math_functions_dialog import MathFunctionsDialog
from .special_functions_dialog import SpecialFunctionsDialog
from .case_expression_dialog import CaseExpressionDialog
from .subquery_dialog import SubqueryDialog
from .window_functions_dialog import WindowFunctionsDialog

class AdvancedSelectDialog(QDialog):
    query_executed = pyqtSignal(str)

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Расширенный SELECT запрос")
        self.resize(1400, 900)
        
        # Инициализация переменных
        self.tables = {}
        self.joins = []
        self.aggregate_functions = []
        self.date_functions = []
        self.string_functions = []
        self.math_functions = []
        self.special_functions = []
        self.window_functions = []
        
        self.init_ui()
        self.load_tables()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Создаем сплиттер для разделения на верхнюю и нижнюю части
        splitter = QSplitter(Qt.Vertical)
        
        # Верхняя часть - настройки запроса
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Создаем область прокрутки для всех настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Группа выбора таблиц
        tables_group = QGroupBox("Выбор таблиц")
        tables_layout = QVBoxLayout()
        
        # Кнопки управления таблицами
        tables_buttons_layout = QHBoxLayout()
        self.add_table_btn = QPushButton("Добавить таблицу")
        self.add_table_btn.clicked.connect(self.add_table)
        self.remove_table_btn = QPushButton("Удалить таблицу")
        self.remove_table_btn.clicked.connect(self.remove_table)
        tables_buttons_layout.addWidget(self.add_table_btn)
        tables_buttons_layout.addWidget(self.remove_table_btn)
        tables_buttons_layout.addStretch()
        
        tables_layout.addLayout(tables_buttons_layout)
        
        # Список таблиц
        self.tables_list = QListWidget()
        self.tables_list.setMaximumHeight(120)
        tables_layout.addWidget(self.tables_list)
        
        tables_group.setLayout(tables_layout)
        scroll_layout.addWidget(tables_group)
        
        # Группа JOIN
        join_group = QGroupBox("JOIN")
        join_layout = QVBoxLayout()
        
        # Кнопки управления JOIN
        join_buttons_layout = QHBoxLayout()
        self.add_join_btn = QPushButton("Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join)
        self.remove_join_btn = QPushButton("Удалить JOIN")
        self.remove_join_btn.clicked.connect(self.remove_join)
        join_buttons_layout.addWidget(self.add_join_btn)
        join_buttons_layout.addWidget(self.remove_join_btn)
        join_buttons_layout.addStretch()
        
        join_layout.addLayout(join_buttons_layout)
        
        # Список JOIN
        self.joins_list = QListWidget()
        self.joins_list.setMaximumHeight(120)
        join_layout.addWidget(self.joins_list)
        
        join_group.setLayout(join_layout)
        scroll_layout.addWidget(join_group)
        
        # Группа выбора столбцов
        columns_group = QGroupBox("Выбор столбцов")
        columns_layout = QVBoxLayout()
        
        # Кнопки для столбцов
        columns_buttons_layout = QHBoxLayout()
        self.select_all_columns_btn = QPushButton("Выбрать все")
        self.select_all_columns_btn.clicked.connect(self.select_all_columns)
        self.deselect_all_columns_btn = QPushButton("Снять выделение")
        self.deselect_all_columns_btn.clicked.connect(self.deselect_all_columns)
        columns_buttons_layout.addWidget(self.select_all_columns_btn)
        columns_buttons_layout.addWidget(self.deselect_all_columns_btn)
        columns_buttons_layout.addStretch()
        
        columns_layout.addLayout(columns_buttons_layout)
        
        # Таблица столбцов
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(4)
        self.columns_table.setHorizontalHeaderLabels(["Выбрать", "Таблица", "Столбец", "Псевдоним"])
        self.columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.columns_table.setMaximumHeight(200)
        columns_layout.addWidget(self.columns_table)
        
        columns_group.setLayout(columns_layout)
        scroll_layout.addWidget(columns_group)
        
        # Группа функций
        functions_group = QGroupBox("Функции")
        functions_layout = QVBoxLayout()
        
        # Агрегатные функции
        agg_layout = QHBoxLayout()
        agg_label = QLabel("Агрегатные функции:")
        self.add_aggregate_btn = QPushButton("Добавить агрегатную функцию")
        self.add_aggregate_btn.clicked.connect(self.add_aggregate_function)
        agg_layout.addWidget(agg_label)
        agg_layout.addWidget(self.add_aggregate_btn)
        agg_layout.addStretch()
        functions_layout.addLayout(agg_layout)
        
        self.aggregate_list = QListWidget()
        self.aggregate_list.setMaximumHeight(80)
        functions_layout.addWidget(self.aggregate_list)
        
        agg_remove_layout = QHBoxLayout()
        self.remove_aggregate_btn = QPushButton("Удалить выбранное")
        self.remove_aggregate_btn.clicked.connect(self.remove_aggregate_function)
        self.remove_all_aggregates_btn = QPushButton("Удалить все")
        self.remove_all_aggregates_btn.clicked.connect(self.remove_all_aggregates)
        agg_remove_layout.addWidget(self.remove_aggregate_btn)
        agg_remove_layout.addWidget(self.remove_all_aggregates_btn)
        agg_remove_layout.addStretch()
        functions_layout.addLayout(agg_remove_layout)
        
        # Функции даты
        date_layout = QHBoxLayout()
        date_label = QLabel("Функции даты:")
        self.add_date_function_btn = QPushButton("Добавить функцию даты")
        self.add_date_function_btn.clicked.connect(self.add_date_function)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.add_date_function_btn)
        date_layout.addStretch()
        functions_layout.addLayout(date_layout)
        
        self.date_functions_list = QListWidget()
        self.date_functions_list.setMaximumHeight(80)
        functions_layout.addWidget(self.date_functions_list)
        
        date_remove_layout = QHBoxLayout()
        self.remove_date_function_btn = QPushButton("Удалить выбранное")
        self.remove_date_function_btn.clicked.connect(self.remove_date_function)
        self.remove_all_date_functions_btn = QPushButton("Удалить все")
        self.remove_all_date_functions_btn.clicked.connect(self.remove_all_date_functions)
        date_remove_layout.addWidget(self.remove_date_function_btn)
        date_remove_layout.addWidget(self.remove_all_date_functions_btn)
        date_remove_layout.addStretch()
        functions_layout.addLayout(date_remove_layout)
        
        # Строковые функции
        string_layout = QHBoxLayout()
        string_label = QLabel("Строковые функции:")
        self.add_string_function_btn = QPushButton("Добавить строковую функцию")
        self.add_string_function_btn.clicked.connect(self.add_string_function)
        string_layout.addWidget(string_label)
        string_layout.addWidget(self.add_string_function_btn)
        string_layout.addStretch()
        functions_layout.addLayout(string_layout)
        
        self.string_functions_list = QListWidget()
        self.string_functions_list.setMaximumHeight(80)
        functions_layout.addWidget(self.string_functions_list)
        
        string_remove_layout = QHBoxLayout()
        self.remove_string_function_btn = QPushButton("Удалить выбранное")
        self.remove_string_function_btn.clicked.connect(self.remove_string_function)
        self.remove_all_string_functions_btn = QPushButton("Удалить все")
        self.remove_all_string_functions_btn.clicked.connect(self.remove_all_string_functions)
        string_remove_layout.addWidget(self.remove_string_function_btn)
        string_remove_layout.addWidget(self.remove_all_string_functions_btn)
        string_remove_layout.addStretch()
        functions_layout.addLayout(string_remove_layout)
        
        # Математические функции
        math_layout = QHBoxLayout()
        math_label = QLabel("Математические функции:")
        self.add_math_function_btn = QPushButton("Добавить математическую функцию")
        self.add_math_function_btn.clicked.connect(self.add_math_function)
        math_layout.addWidget(math_label)
        math_layout.addWidget(self.add_math_function_btn)
        math_layout.addStretch()
        functions_layout.addLayout(math_layout)
        
        self.math_functions_list = QListWidget()
        self.math_functions_list.setMaximumHeight(80)
        functions_layout.addWidget(self.math_functions_list)
        
        math_remove_layout = QHBoxLayout()
        self.remove_math_function_btn = QPushButton("Удалить выбранное")
        self.remove_math_function_btn.clicked.connect(self.remove_math_function)
        self.remove_all_math_functions_btn = QPushButton("Удалить все")
        self.remove_all_math_functions_btn.clicked.connect(self.remove_all_math_functions)
        math_remove_layout.addWidget(self.remove_math_function_btn)
        math_remove_layout.addWidget(self.remove_all_math_functions_btn)
        math_remove_layout.addStretch()
        functions_layout.addLayout(math_remove_layout)
        
        # Специальные функции
        special_layout = QHBoxLayout()
        special_label = QLabel("Специальные функции:")
        self.add_special_function_btn = QPushButton("Добавить специальную функцию")
        self.add_special_function_btn.clicked.connect(self.add_special_function)
        special_layout.addWidget(special_label)
        special_layout.addWidget(self.add_special_function_btn)
        special_layout.addStretch()
        functions_layout.addLayout(special_layout)
        
        self.special_functions_list = QListWidget()
        self.special_functions_list.setMaximumHeight(80)
        functions_layout.addWidget(self.special_functions_list)
        
        special_remove_layout = QHBoxLayout()
        self.remove_special_function_btn = QPushButton("Удалить выбранное")
        self.remove_special_function_btn.clicked.connect(self.remove_special_function)
        self.remove_all_special_functions_btn = QPushButton("Удалить все")
        self.remove_all_special_functions_btn.clicked.connect(self.remove_all_special_functions)
        special_remove_layout.addWidget(self.remove_special_function_btn)
        special_remove_layout.addWidget(self.remove_all_special_functions_btn)
        special_remove_layout.addStretch()
        functions_layout.addLayout(special_remove_layout)
        
        functions_group.setLayout(functions_layout)
        scroll_layout.addWidget(functions_group)
        
        # Группа WHERE
        where_group = QGroupBox("WHERE условия")
        where_layout = QVBoxLayout()
        
        where_label = QLabel("Условия фильтрации (например: age > 18 AND city = 'Moscow'):")
        where_layout.addWidget(where_label)
        
        self.where_edit = QTextEdit()
        self.where_edit.setMaximumHeight(80)
        where_layout.addWidget(self.where_edit)
        
        where_group.setLayout(where_layout)
        scroll_layout.addWidget(where_group)
        
        # Группа GROUP BY и HAVING
        group_tab_layout = QVBoxLayout()
        
        # GROUP BY
        group_by_layout = QHBoxLayout()
        group_by_label = QLabel("GROUP BY:")
        self.group_by_combo = QComboBox()
        self.group_by_combo.setEditable(True)
        self.add_group_by_btn = QPushButton("Добавить")
        self.add_group_by_btn.clicked.connect(self.add_group_by)
        group_by_layout.addWidget(group_by_label)
        group_by_layout.addWidget(self.group_by_combo)
        group_by_layout.addWidget(self.add_group_by_btn)
        group_tab_layout.addLayout(group_by_layout)
        
        self.group_by_list = QListWidget()
        self.group_by_list.setMaximumHeight(60)
        group_tab_layout.addWidget(self.group_by_list)
        
        group_by_remove_layout = QHBoxLayout()
        self.remove_group_by_btn = QPushButton("Удалить выбранное")
        self.remove_group_by_btn.clicked.connect(self.remove_group_by)
        self.remove_all_group_by_btn = QPushButton("Удалить все")
        self.remove_all_group_by_btn.clicked.connect(self.remove_all_group_by)
        group_by_remove_layout.addWidget(self.remove_group_by_btn)
        group_by_remove_layout.addWidget(self.remove_all_group_by_btn)
        group_by_remove_layout.addStretch()
        group_tab_layout.addLayout(group_by_remove_layout)
        
        # HAVING
        having_label = QLabel("HAVING условие:")
        group_tab_layout.addWidget(having_label)
        
        self.having_edit = QLineEdit()
        self.having_edit.setPlaceholderText("Например: COUNT(*) > 5")
        group_tab_layout.addWidget(self.having_edit)
        
        group_group = QGroupBox("GROUP BY и HAVING")
        group_group.setLayout(group_tab_layout)
        scroll_layout.addWidget(group_group)
        
        # Группа оконных функций
        window_functions_group = QGroupBox("Оконные функции")
        window_functions_layout = QVBoxLayout()
        
        window_buttons_layout = QHBoxLayout()
        self.add_window_function_btn = QPushButton("Добавить оконную функцию")
        self.add_window_function_btn.clicked.connect(self.add_window_function)
        window_buttons_layout.addWidget(self.add_window_function_btn)
        window_buttons_layout.addStretch()
        window_functions_layout.addLayout(window_buttons_layout)
        
        self.window_functions_list = QListWidget()
        self.window_functions_list.setMaximumHeight(80)
        window_functions_layout.addWidget(self.window_functions_list)
        
        window_remove_layout = QHBoxLayout()
        self.remove_window_function_btn = QPushButton("Удалить выбранное")
        self.remove_window_function_btn.clicked.connect(self.remove_window_function)
        self.remove_all_window_functions_btn = QPushButton("Удалить все")
        self.remove_all_window_functions_btn.clicked.connect(self.remove_all_window_functions)
        window_remove_layout.addWidget(self.remove_window_function_btn)
        window_remove_layout.addWidget(self.remove_all_window_functions_btn)
        window_remove_layout.addStretch()
        window_functions_layout.addLayout(window_remove_layout)
        
        window_functions_group.setLayout(window_functions_layout)
        scroll_layout.addWidget(window_functions_group)
        
        # Группа ORDER BY
        order_group = QGroupBox("ORDER BY")
        order_layout = QVBoxLayout()
        
        order_controls_layout = QHBoxLayout()
        order_label = QLabel("Сортировка по:")
        self.order_by_combo = QComboBox()
        self.order_by_combo.setEditable(True)
        self.order_direction_combo = QComboBox()
        self.order_direction_combo.addItems(["ASC", "DESC"])
        self.add_order_by_btn = QPushButton("Добавить")
        self.add_order_by_btn.clicked.connect(self.add_order_by)
        order_controls_layout.addWidget(order_label)
        order_controls_layout.addWidget(self.order_by_combo)
        order_controls_layout.addWidget(self.order_direction_combo)
        order_controls_layout.addWidget(self.add_order_by_btn)
        order_layout.addLayout(order_controls_layout)
        
        self.order_by_list = QListWidget()
        self.order_by_list.setMaximumHeight(60)
        order_layout.addWidget(self.order_by_list)
        
        order_remove_layout = QHBoxLayout()
        self.remove_order_by_btn = QPushButton("Удалить выбранное")
        self.remove_order_by_btn.clicked.connect(self.remove_order_by)
        self.remove_all_order_by_btn = QPushButton("Удалить все")
        self.remove_all_order_by_btn.clicked.connect(self.remove_all_order_by)
        order_remove_layout.addWidget(self.remove_order_by_btn)
        order_remove_layout.addWidget(self.remove_all_order_by_btn)
        order_remove_layout.addStretch()
        order_layout.addLayout(order_remove_layout)
        
        order_group.setLayout(order_layout)
        scroll_layout.addWidget(order_group)
        
        # Группа LIMIT
        limit_group = QGroupBox("LIMIT")
        limit_layout = QHBoxLayout()
        
        limit_label = QLabel("Ограничение количества строк:")
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(0)
        self.limit_spinbox.setMaximum(1000000)
        self.limit_spinbox.setValue(0)
        self.limit_spinbox.setSpecialValueText("Нет ограничения")
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_spinbox)
        limit_layout.addStretch()
        
        limit_group.setLayout(limit_layout)
        scroll_layout.addWidget(limit_group)
        
        # Группа DISTINCT
        distinct_group = QGroupBox("DISTINCT")
        distinct_layout = QHBoxLayout()
        
        self.distinct_checkbox = QCheckBox("Выбрать только уникальные строки (DISTINCT)")
        distinct_layout.addWidget(self.distinct_checkbox)
        distinct_layout.addStretch()
        
        distinct_group.setLayout(distinct_layout)
        scroll_layout.addWidget(distinct_group)
        
        scroll.setWidget(scroll_content)
        top_layout.addWidget(scroll)
        
        splitter.addWidget(top_widget)
        
        # Нижняя часть - SQL запрос и кнопки
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # SQL запрос
        sql_label = QLabel("Сгенерированный SQL запрос:")
        bottom_layout.addWidget(sql_label)
        
        self.sql_edit = QTextEdit()
        self.sql_edit.setMaximumHeight(150)
        font = QFont("Courier New", 10)
        self.sql_edit.setFont(font)
        bottom_layout.addWidget(self.sql_edit)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Сгенерировать SQL")
        self.generate_btn.clicked.connect(self.generate_sql)
        
        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_query)
        
        self.clear_btn = QPushButton("Очистить все")
        self.clear_btn.clicked.connect(self.clear_all)
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.execute_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        bottom_layout.addLayout(buttons_layout)
        
        splitter.addWidget(bottom_widget)
        
        # Устанавливаем пропорции сплиттера
        splitter.setSizes([600, 300])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def load_tables(self):
        """Загрузка списка таблиц из базы данных"""
        try:
            tables = self.db_manager.get_tables()
            self.available_tables = tables
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицы: {str(e)}")

    def add_table(self):
        """Добавление таблицы"""
        from PyQt5.QtWidgets import QInputDialog
        
        if not hasattr(self, 'available_tables'):
            QMessageBox.warning(self, "Предупреждение", "Список таблиц не загружен")
            return
        
        table_name, ok = QInputDialog.getItem(self, "Выбор таблицы", 
                                               "Выберите таблицу:", 
                                               self.available_tables, 0, False)
        if ok and table_name:
            # Проверяем, не добавлена ли уже таблица
            if table_name in self.tables:
                QMessageBox.warning(self, "Предупреждение", "Таблица уже добавлена")
                return
            
            # Запрашиваем псевдоним
            alias, ok = QInputDialog.getText(self, "Псевдоним таблицы", 
                                             f"Введите псевдоним для таблицы {table_name} (или оставьте пустым):")
            if ok:
                self.tables[table_name] = alias if alias else None
                display_text = f"{table_name} AS {alias}" if alias else table_name
                self.tables_list.addItem(display_text)
                self.populate_columns()

    def remove_table(self):
        """Удаление выбранной таблицы"""
        current_item = self.tables_list.currentItem()
        if current_item:
            # Извлекаем имя таблицы из текста
            text = current_item.text()
            table_name = text.split(" AS ")[0] if " AS " in text else text
            
            # Удаляем таблицу из словаря
            if table_name in self.tables:
                del self.tables[table_name]
            
            # Удаляем элемент из списка
            self.tables_list.takeItem(self.tables_list.row(current_item))
            self.populate_columns()

    def populate_columns(self):
        """Заполнение списка столбцов из выбранных таблиц"""
        self.columns_table.setRowCount(0)
        
        # Очищаем списки функций при изменении таблиц
        self.aggregate_functions.clear()
        self.aggregate_list.clear()
        self.date_functions.clear()
        self.date_functions_list.clear()
        self.string_functions.clear()
        self.string_functions_list.clear()
        self.math_functions.clear()
        self.math_functions_list.clear()
        self.special_functions.clear()
        self.special_functions_list.clear()
        self.window_functions.clear()
        self.window_functions_list.clear()
        
        for table_name in self.tables.keys():
            try:
                columns = self.db_manager.get_columns(table_name)
                for column in columns:
                    row_position = self.columns_table.rowCount()
                    self.columns_table.insertRow(row_position)
                    
                    # Чекбокс для выбора
                    checkbox = QCheckBox()
                    self.columns_table.setCellWidget(row_position, 0, checkbox)
                    
                    # Имя таблицы
                    table_item = QTableWidgetItem(table_name)
                    table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                    self.columns_table.setItem(row_position, 1, table_item)
                    
                    # Имя столбца
                    column_item = QTableWidgetItem(column)
                    column_item.setFlags(column_item.flags() & ~Qt.ItemIsEditable)
                    self.columns_table.setItem(row_position, 2, column_item)
                    
                    # Псевдоним (редактируемый)
                    alias_item = QTableWidgetItem("")
                    self.columns_table.setItem(row_position, 3, alias_item)
                    
            except Exception as e:
                QMessageBox.warning(self, "Предупреждение", 
                                  f"Не удалось загрузить столбцы для таблицы {table_name}: {str(e)}")
        
        # Обновляем доступные столбцы для GROUP BY и ORDER BY
        self.update_available_columns()

    def update_available_columns(self):
        """Обновление списка доступных столбцов для GROUP BY и ORDER BY"""
        self.group_by_combo.clear()
        self.order_by_combo.clear()
        
        for row in range(self.columns_table.rowCount()):
            table = self.columns_table.item(row, 1).text()
            column = self.columns_table.item(row, 2).text()
            alias = self.tables.get(table)
            
            if alias:
                column_ref = f"{alias}.{column}"
            else:
                column_ref = f"{table}.{column}"
            
            self.group_by_combo.addItem(column_ref)
            self.order_by_combo.addItem(column_ref)

    def select_all_columns(self):
        """Выбрать все столбцы"""
        for row in range(self.columns_table.rowCount()):
            checkbox = self.columns_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def deselect_all_columns(self):
        """Снять выделение со всех столбцов"""
        for row in range(self.columns_table.rowCount()):
            checkbox = self.columns_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def add_join(self):
        """Добавление JOIN"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
        
        if len(self.tables) < 2:
            QMessageBox.warning(self, "Предупреждение", "Необходимо выбрать минимум 2 таблицы для JOIN")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить JOIN")
        layout = QVBoxLayout()
        
        # Тип JOIN
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип JOIN:"))
        join_type_combo = QComboBox()
        join_type_combo.addItems(["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"])
        type_layout.addWidget(join_type_combo)
        layout.addLayout(type_layout)
        
        # Таблица для JOIN
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Таблица:"))
        table_combo = QComboBox()
        table_items = [f"{name} AS {alias}" if alias else name 
                      for name, alias in self.tables.items()]
        table_combo.addItems(table_items)
        table_layout.addWidget(table_combo)
        layout.addLayout(table_layout)
        
        # Условие ON
        on_layout = QHBoxLayout()
        on_layout.addWidget(QLabel("Условие ON:"))
        on_edit = QLineEdit()
        on_edit.setPlaceholderText("Например: table1.id = table2.id")
        on_layout.addWidget(on_edit)
        layout.addLayout(on_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            join_type = join_type_combo.currentText()
            table = table_combo.currentText()
            condition = on_edit.text().strip()
            
            if not condition:
                QMessageBox.warning(dialog, "Предупреждение", "Необходимо указать условие ON")
                return
            
            join_text = f"{join_type} {table} ON {condition}"
            self.joins.append(join_text)
            self.joins_list.addItem(join_text)
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def remove_join(self):
        """Удаление выбранного JOIN"""
        current_item = self.joins_list.currentItem()
        if current_item:
            index = self.joins_list.row(current_item)
            self.joins.pop(index)
            self.joins_list.takeItem(index)

    def add_aggregate_function(self):
        """Добавление агрегатной функции"""
        dialog = AggregateFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.aggregate_functions.append(function_sql)
                self.aggregate_list.addItem(function_sql)
                # Обновляем доступные столбцы для ORDER BY
                self.update_available_order_columns()

    def remove_aggregate_function(self):
        """Удаление выбранной агрегатной функции"""
        current_item = self.aggregate_list.currentItem()
        if current_item:
            index = self.aggregate_list.row(current_item)
            self.aggregate_functions.pop(index)
            self.aggregate_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_aggregates(self):
        """Удаление всех агрегатных функций"""
        self.aggregate_functions.clear()
        self.aggregate_list.clear()
        self.update_available_order_columns()

    def add_date_function(self):
        """Добавление функции даты"""
        dialog = DateFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.date_functions.append(function_sql)
                self.date_functions_list.addItem(function_sql)
                self.update_available_order_columns()

    def remove_date_function(self):
        """Удаление выбранной функции даты"""
        current_item = self.date_functions_list.currentItem()
        if current_item:
            index = self.date_functions_list.row(current_item)
            self.date_functions.pop(index)
            self.date_functions_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_date_functions(self):
        """Удаление всех функций даты"""
        self.date_functions.clear()
        self.date_functions_list.clear()
        self.update_available_order_columns()

    def add_string_function(self):
        """Добавление строковой функции"""
        dialog = StringFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.string_functions.append(function_sql)
                self.string_functions_list.addItem(function_sql)
                self.update_available_order_columns()

    def remove_string_function(self):
        """Удаление выбранной строковой функции"""
        current_item = self.string_functions_list.currentItem()
        if current_item:
            index = self.string_functions_list.row(current_item)
            self.string_functions.pop(index)
            self.string_functions_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_string_functions(self):
        """У��аление всех строковых функций"""
        self.string_functions.clear()
        self.string_functions_list.clear()
        self.update_available_order_columns()

    def add_math_function(self):
        """Добавление математической функции"""
        dialog = MathFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.math_functions.append(function_sql)
                self.math_functions_list.addItem(function_sql)
                self.update_available_order_columns()

    def remove_math_function(self):
        """Удаление выбранной математической функции"""
        current_item = self.math_functions_list.currentItem()
        if current_item:
            index = self.math_functions_list.row(current_item)
            self.math_functions.pop(index)
            self.math_functions_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_math_functions(self):
        """Удаление всех математических функций"""
        self.math_functions.clear()
        self.math_functions_list.clear()
        self.update_available_order_columns()

    def add_special_function(self):
        """Добавление специальной функции"""
        dialog = SpecialFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.special_functions.append(function_sql)
                self.special_functions_list.addItem(function_sql)
                self.update_available_order_columns()

    def remove_special_function(self):
        """Удаление выбранной специальной функции"""
        current_item = self.special_functions_list.currentItem()
        if current_item:
            index = self.special_functions_list.row(current_item)
            self.special_functions.pop(index)
            self.special_functions_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_special_functions(self):
        """Удаление всех специальных функций"""
        self.special_functions.clear()
        self.special_functions_list.clear()
        self.update_available_order_columns()

    def add_window_function(self):
        """Добавление оконной функции"""
        dialog = WindowFunctionsDialog(self.tables, self.db_manager, self)
        if dialog.exec_():
            function_sql = dialog.get_function_sql()
            if function_sql:
                self.window_functions.append(function_sql)
                self.window_functions_list.addItem(function_sql)
                self.update_available_order_columns()

    def remove_window_function(self):
        """Удаление выбранной оконной функции"""
        current_item = self.window_functions_list.currentItem()
        if current_item:
            index = self.window_functions_list.row(current_item)
            self.window_functions.pop(index)
            self.window_functions_list.takeItem(index)
            self.update_available_order_columns()

    def remove_all_window_functions(self):
        """Удаление всех оконных функций"""
        self.window_functions.clear()
        self.window_functions_list.clear()
        self.update_available_order_columns()

    def update_available_order_columns(self):
        """Обновление списка доступных столбцов для ORDER BY с учетом псевдонимов функций"""
        current_text = self.order_by_combo.currentText()
        self.order_by_combo.clear()
        
        # Добавляем обычные столбцы
        for row in range(self.columns_table.rowCount()):
            checkbox = self.columns_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                table = self.columns_table.item(row, 1).text()
                column = self.columns_table.item(row, 2).text()
                alias_text = self.columns_table.item(row, 3).text()
                table_alias = self.tables.get(table)
                
                if alias_text:
                    self.order_by_combo.addItem(alias_text)
                elif table_alias:
                    self.order_by_combo.addItem(f"{table_alias}.{column}")
                else:
                    self.order_by_combo.addItem(f"{table}.{column}")
        
        # Добавляем агрегатные функции с псевдонимами
        for func in self.aggregate_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Добавляем функции даты с псевдонимами
        for func in self.date_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Добавляем строковые функции с псевдонимами
        for func in self.string_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Добавляем математические функции с псевдонимами
        for func in self.math_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Добавляем специальные функции с псевдонимами
        for func in self.special_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Добавляем оконные функции с псевдонимами
        for func in self.window_functions:
            alias = self.extract_alias_from_function(func)
            if alias:
                self.order_by_combo.addItem(alias)
        
        # Восстанавливаем предыдущий выбор, если возможно
        index = self.order_by_combo.findText(current_text)
        if index >= 0:
            self.order_by_combo.setCurrentIndex(index)

    def extract_alias_from_function(self, function_sql):
        """Извлечение псевдонима из SQL функции"""
        # Ищем паттерн "AS alias" в конце строки
        match = re.search(r'\s+AS\s+(\w+)\s*$', function_sql, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def add_group_by(self):
        """Добавление столбца в GROUP BY"""
        column = self.group_by_combo.currentText().strip()
        if column:
            # Проверяем, не добавлен ли уже этот столбец
            for i in range(self.group_by_list.count()):
                if self.group_by_list.item(i).text() == column:
                    QMessageBox.warning(self, "Предупреждение", "Этот столбец уже добавлен в GROUP BY")
                    return
            
            self.group_by_list.addItem(column)

    def remove_group_by(self):
        """Удаление выбранного столбца из GROUP BY"""
        current_item = self.group_by_list.currentItem()
        if current_item:
            self.group_by_list.takeItem(self.group_by_list.row(current_item))

    def remove_all_group_by(self):
        """Удаление всех столбцов из GROUP BY"""
        self.group_by_list.clear()

    def add_order_by(self):
        """Добавление столбца в ORDER BY"""
        column = self.order_by_combo.currentText().strip()
        direction = self.order_direction_combo.currentText()
        
        if column:
            order_text = f"{column} {direction}"
            self.order_by_list.addItem(order_text)

    def remove_order_by(self):
        """Удаление выбранного столбца из ORDER BY"""
        current_item = self.order_by_list.currentItem()
        if current_item:
            self.order_by_list.takeItem(self.order_by_list.row(current_item))

    def remove_all_order_by(self):
        """Удаление всех столбцов из ORDER BY"""
        self.order_by_list.clear()

    def generate_sql(self):
        """Генерация SQL запроса"""
        try:
            query = self.build_sql_query()
            self.sql_edit.setPlainText(query)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать SQL: {str(e)}")

    def build_sql_query(self):
        """Построение SQL запроса"""
        if not self.tables:
            raise ValueError("Необходимо выбрать хотя бы одну таблицу")
        
        # SELECT часть
        select_parts = []
        
        # Добавляем выбранные столбцы
        for row in range(self.columns_table.rowCount()):
            checkbox = self.columns_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                table = self.columns_table.item(row, 1).text()
                column = self.columns_table.item(row, 2).text()
                alias = self.columns_table.item(row, 3).text()
                table_alias = self.tables.get(table)
                
                if table_alias:
                    column_ref = f"{table_alias}.{column}"
                else:
                    column_ref = f"{table}.{column}"
                
                if alias:
                    column_ref += f" AS {alias}"
                
                select_parts.append(column_ref)
        
        # Добавляем агрегатные функции
        for func in self.aggregate_functions:
            select_parts.append(func)
        
        # Добавляем функции даты
        for func in self.date_functions:
            select_parts.append(func)
        
        # Добавляем строковые функции
        for func in self.string_functions:
            select_parts.append(func)
        
        # Добавляем математические функции
        for func in self.math_functions:
            select_parts.append(func)
        
        # Добавляем специальные функции
        for func in self.special_functions:
            select_parts.append(func)
        
        # Добавляем оконные функции
        for func in self.window_functions:
            select_parts.append(func)
        
        if not select_parts:
            select_parts.append("*")
        
        # DISTINCT
        distinct = "DISTINCT " if self.distinct_checkbox.isChecked() else ""
        
        query = f"SELECT {distinct}{', '.join(select_parts)}"
        
        # FROM часть
        first_table = list(self.tables.keys())[0]
        first_alias = self.tables[first_table]
        if first_alias:
            query += f"\nFROM {first_table} AS {first_alias}"
        else:
            query += f"\nFROM {first_table}"
        
        # JOIN часть
        for join in self.joins:
            query += f"\n{join}"
        
        # WHERE часть
        where_condition = self.where_edit.toPlainText().strip()
        if where_condition:
            query += f"\nWHERE {where_condition}"
        
        # GROUP BY часть
        group_by_items = []
        for i in range(self.group_by_list.count()):
            group_by_items.append(self.group_by_list.item(i).text())
        
        if group_by_items:
            query += f"\nGROUP BY {', '.join(group_by_items)}"
        
        # HAVING часть
        having_condition = self.having_edit.text().strip()
        if having_condition:
            query += f"\nHAVING {having_condition}"
        
        # ORDER BY часть
        order_by_items = []
        for i in range(self.order_by_list.count()):
            order_by_items.append(self.order_by_list.item(i).text())
        
        if order_by_items:
            query += f"\nORDER BY {', '.join(order_by_items)}"
        
        # LIMIT часть
        limit = self.limit_spinbox.value()
        if limit > 0:
            query += f"\nLIMIT {limit}"
        
        return query

    def execute_query(self):
        """Выполнение SQL запроса"""
        try:
            query = self.sql_edit.toPlainText().strip()
            if not query:
                query = self.build_sql_query()
                self.sql_edit.setPlainText(query)
            
            self.query_executed.emit(query)
            QMessageBox.information(self, "Успех", "Запрос отправлен на выполнение")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить запрос: {str(e)}")

    def clear_all(self):
        """Очистка всех полей"""
        # Очистка таблиц
        self.tables.clear()
        self.tables_list.clear()
        
        # Очистка JOIN
        self.joins.clear()
        self.joins_list.clear()
        
        # Очистка столбцов
        self.columns_table.setRowCount(0)
        
        # Очистка функций
        self.aggregate_functions.clear()
        self.aggregate_list.clear()
        self.date_functions.clear()
        self.date_functions_list.clear()
        self.string_functions.clear()
        self.string_functions_list.clear()
        self.math_functions.clear()
        self.math_functions_list.clear()
        self.special_functions.clear()
        self.special_functions_list.clear()
        self.window_functions.clear()
        self.window_functions_list.clear()
        
        # Очистка WHERE
        self.where_edit.clear()
        
        # Очистка GROUP BY и HAVING
        self.group_by_list.clear()
        self.having_edit.clear()
        
        # Очистка ORDER BY
        self.order_by_list.clear()
        
        # Сброс LIMIT
        self.limit_spinbox.setValue(0)
        
        # Сброс DISTINCT
        self.distinct_checkbox.setChecked(False)
        
        # Очистка SQL
        self.sql_edit.clear()
