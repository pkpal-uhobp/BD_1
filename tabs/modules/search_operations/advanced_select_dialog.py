from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea, QListWidget, QListWidgetItem, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification
import re


class SortColumnWidget(QWidget):
    """Виджет для отображения столбца с его направлением сортировки"""
    
    def __init__(self, column_name, parent=None):
        super().__init__(parent)
        self.column_name = column_name
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        # Название столбца
        self.column_label = QLabel(self.column_name)
        self.column_label.setObjectName("sortColumnLabel")
        self.column_label.setMinimumWidth(150)
        
        # Направление сортировки
        self.direction_combo = QComboBox()
        self.direction_combo.setObjectName("sortDirectionCombo")
        self.direction_combo.addItems(["ASC", "DESC"])
        self.direction_combo.setMinimumWidth(80)
        self.direction_combo.setCurrentIndex(0)  # Устанавливаем ASC по умолчанию
        # Делаем только для выбора, без ввода с клавиатуры
        self.direction_combo.setEditable(False)
        
        # Принудительно устанавливаем темную палитру для комбобокса сортировки
        palette = self.direction_combo.palette()
        palette.setColor(QPalette.Window, QColor(25, 25, 35))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 35))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(25, 25, 35))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(100, 255, 218))
        palette.setColor(QPalette.HighlightedText, QColor(10, 10, 15))
        self.direction_combo.setPalette(palette)
        
        # Кнопка удаления
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setObjectName("removeSortBtn")
        self.remove_btn.setMaximumWidth(30)
        self.remove_btn.setMaximumHeight(30)
        
        layout.addWidget(self.column_label)
        layout.addWidget(QLabel("→"))
        layout.addWidget(self.direction_combo)
        layout.addWidget(self.remove_btn)
        layout.addStretch()
        
        # Подключаем сигнал удаления
        self.remove_btn.clicked.connect(self.remove_self)
        
        # Принудительно обновляем отображение
        self.direction_combo.setCurrentText("ASC")
        
    def remove_self(self):
        """Удаляет этот виджет"""
        print(f"Кнопка удаления нажата для: {self.column_name}")  # Отладочная информация
        # Находим главный диалог через цепочку родителей
        parent = self.parent()
        while parent and not hasattr(parent, 'remove_sort_widget'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'remove_sort_widget'):
            print(f"Найден родитель с методом remove_sort_widget: {type(parent)}")
            parent.remove_sort_widget(self)
        else:
            print("Не найден родитель с методом remove_sort_widget")
            
    def get_sort_clause(self):
        """Возвращает SQL для сортировки этого столбца"""
        direction = self.direction_combo.currentText()
        return f'"{self.column_name}" {direction}'


class AdvancedSelectDialog(QDialog):
    # Сигнал для передачи результатов в главное окно
    results_to_main_table = Signal(list)
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Расширенный SELECT")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1000, 800)
        self.resize(900, 700)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Создаем скроллируемую область
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("mainScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Создаем контейнер для содержимого
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        
        # Создаем интерфейс
        self.setup_ui()
        self.apply_styles()
        
    def set_dark_palette(self):
        """Устанавливает тёмную цветовую палитру"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.ToolTipText, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)
        
    def setup_ui(self):
        """Создает пользовательский интерфейс"""
        
        # Заголовок
        header_label = QLabel("РАСШИРЕННЫЙ SELECT")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(header_label)
        
        # Создаем панель настроек запроса (без правой панели результатов)
        query_panel = self.create_query_panel()
        self.content_layout.addWidget(query_panel)
        
        # Устанавливаем содержимое в скролл-область
        self.scroll_area.setWidget(self.content_widget)
        
        # Добавляем скролл-область в основной layout
        self.layout().addWidget(self.scroll_area)
        
        # Кнопки (вне скролл-области)
        buttons_layout = QHBoxLayout()
        
        self.execute_button = QPushButton("Выполнить и отправить в главную таблицу")
        self.execute_button.setObjectName("executeButton")
        self.execute_button.clicked.connect(self.execute_and_send_query)
        
        self.preview_button = QPushButton("Предварительный просмотр SQL")
        self.preview_button.setObjectName("previewButton")
        self.preview_button.clicked.connect(self.preview_sql)
        
        self.clear_button = QPushButton("🗑 Очистить")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_all)
        
        self.close_button = QPushButton("Закрыть")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.execute_button)
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        self.layout().addLayout(buttons_layout)
        
        # Переменная для хранения результатов запроса
        self.last_query_results = []
        
        # Подключаем валидацию в реальном времени для WHERE и HAVING
        self.where_input.textChanged.connect(self.validate_where_condition)
        self.having_input.textChanged.connect(self.validate_having_condition)
        
        # Заполняем начальные данные
        self.populate_tables()
        
    def create_query_panel(self):
        """Создает левую панель с настройками запроса"""
        panel = QWidget()
        panel.setObjectName("queryPanel")
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Создаем вкладки для лучшей организации
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Вкладка "Основные настройки"
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        basic_tab.setLayout(basic_layout)
        
        # Группа выбора таблицы
        table_group = QGroupBox("Выбор таблицы")
        table_group.setObjectName("tableGroup")
        table_layout = QFormLayout()
        table_group.setLayout(table_layout)
        
        self.table_combo = QComboBox()
        self.table_combo.setObjectName("tableCombo")
        self.table_combo.currentTextChanged.connect(self.populate_columns)
        
        # Принудительно устанавливаем темную палитру для комбобокса
        palette = self.table_combo.palette()
        palette.setColor(QPalette.Window, QColor(25, 25, 35))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 35))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(25, 25, 35))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(100, 255, 218))
        palette.setColor(QPalette.HighlightedText, QColor(10, 10, 15))
        self.table_combo.setPalette(palette)
        
        table_layout.addRow("Таблица:", self.table_combo)
        
        basic_layout.addWidget(table_group)
        
        # Группа выбора столбцов
        columns_group = QGroupBox("Выбор столбцов")
        columns_group.setObjectName("columnsGroup")
        columns_layout = QVBoxLayout()
        columns_group.setLayout(columns_layout)
        
        # Список доступных столбцов
        self.available_columns = QListWidget()
        self.available_columns.setObjectName("availableColumns")
        self.available_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(QLabel("Доступные столбцы:"))
        columns_layout.addWidget(self.available_columns)
        
        # Кнопки для управления столбцами
        columns_buttons_layout = QHBoxLayout()
        
        self.add_column_btn = QPushButton("➡ Добавить")
        self.add_column_btn.setObjectName("addColumnBtn")
        self.add_column_btn.clicked.connect(self.add_selected_columns)
        
        self.add_all_btn = QPushButton("➡➡ Все")
        self.add_all_btn.setObjectName("addAllBtn")
        self.add_all_btn.clicked.connect(self.add_all_columns)
        
        columns_buttons_layout.addWidget(self.add_column_btn)
        columns_buttons_layout.addWidget(self.add_all_btn)
        columns_layout.addLayout(columns_buttons_layout)
        
        # Список выбранных столбцов
        self.selected_columns = QListWidget()
        self.selected_columns.setObjectName("selectedColumns")
        self.selected_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(QLabel("Выбранные столбцы:"))
        columns_layout.addWidget(self.selected_columns)
        
        # Кнопки для удаления столбцов
        remove_buttons_layout = QHBoxLayout()
        
        self.remove_column_btn = QPushButton("⬅ Удалить")
        self.remove_column_btn.setObjectName("removeColumnBtn")
        self.remove_column_btn.clicked.connect(self.remove_selected_columns)
        
        self.remove_all_btn = QPushButton("⬅⬅ Все")
        self.remove_all_btn.setObjectName("removeAllBtn")
        self.remove_all_btn.clicked.connect(self.remove_all_columns)
        
        remove_buttons_layout.addWidget(self.remove_column_btn)
        remove_buttons_layout.addWidget(self.remove_all_btn)
        columns_layout.addLayout(remove_buttons_layout)
        
        basic_layout.addWidget(columns_group)
        
        # Добавляем основную вкладку
        tab_widget.addTab(basic_tab, "Основные настройки")
        
        # Вкладка "Фильтрация и сортировка"
        filter_tab = QWidget()
        filter_layout = QVBoxLayout()
        filter_tab.setLayout(filter_layout)
        
        # Группа WHERE
        where_group = QGroupBox("WHERE (Условия фильтрации)")
        where_group.setObjectName("whereGroup")
        where_layout = QVBoxLayout()
        where_group.setLayout(where_layout)
        
        self.where_input = QLineEdit()
        self.where_input.setObjectName("whereInput")
        self.where_input.setPlaceholderText("Например: age > 18 AND name LIKE '%John%'")
        where_layout.addWidget(self.where_input)
        
        # Метка для отображения ошибок/успеха валидации WHERE
        self.where_error_label = QLabel()
        self.where_error_label.setObjectName("whereErrorLabel")
        self.where_error_label.setWordWrap(True)
        self.where_error_label.hide()
        where_layout.addWidget(self.where_error_label)
        
        filter_layout.addWidget(where_group)
        
        # Группа ORDER BY - новый интерфейс с индивидуальным направлением
        order_group = QGroupBox("ORDER BY (Сортировка)")
        order_group.setObjectName("orderGroup")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        # Доступные столбцы для сортировки
        self.available_order_columns = QListWidget()
        self.available_order_columns.setObjectName("availableOrderColumns")
        self.available_order_columns.setSelectionMode(QListWidget.MultiSelection)
        # Делаем список только для выбора, без ввода с клавиатуры
        self.available_order_columns.setEditTriggers(QListWidget.NoEditTriggers)
        order_layout.addWidget(QLabel("Доступные столбцы:"))
        order_layout.addWidget(self.available_order_columns)
        
        # Кнопки для добавления столбцов сортировки
        order_add_buttons_layout = QHBoxLayout()
        
        self.add_order_btn = QPushButton("➡ Добавить")
        self.add_order_btn.setObjectName("addOrderBtn")
        self.add_order_btn.clicked.connect(self.add_order_column)
        
        self.add_all_order_btn = QPushButton("➡➡ Все")
        self.add_all_order_btn.setObjectName("addAllOrderBtn")
        self.add_all_order_btn.clicked.connect(self.add_all_order_columns)
        
        order_add_buttons_layout.addWidget(self.add_order_btn)
        order_add_buttons_layout.addWidget(self.add_all_order_btn)
        order_layout.addLayout(order_add_buttons_layout)
        
        # Контейнер для виджетов сортировки
        order_layout.addWidget(QLabel("Столбцы для сортировки:"))
        self.sort_widgets_container = QWidget()
        self.sort_widgets_container.setObjectName("sortWidgetsContainer")
        self.sort_widgets_layout = QVBoxLayout()
        self.sort_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self.sort_widgets_container.setLayout(self.sort_widgets_layout)
        order_layout.addWidget(self.sort_widgets_container)
        
        filter_layout.addWidget(order_group)
        
        # Добавляем вкладку фильтрации
        tab_widget.addTab(filter_tab, "Фильтрация и сортировка")
        
        # Вкладка "Группировка и агрегаты"
        group_tab = QWidget()
        group_tab_layout = QVBoxLayout()
        group_tab.setLayout(group_tab_layout)
        
        # Группа GROUP BY - переделаем в стиле 1-й вкладки
        group_group = QGroupBox("GROUP BY (Группировка)")
        group_group.setObjectName("groupGroup")
        group_layout = QVBoxLayout()
        group_group.setLayout(group_layout)
        
        # Доступные столбцы для группировки
        self.available_group_columns = QListWidget()
        self.available_group_columns.setObjectName("availableGroupColumns")
        self.available_group_columns.setSelectionMode(QListWidget.MultiSelection)
        # Делаем список только для выбора, без ввода с клавиатуры
        self.available_group_columns.setEditTriggers(QListWidget.NoEditTriggers)
        group_layout.addWidget(QLabel("Доступные столбцы:"))
        group_layout.addWidget(self.available_group_columns)
        
        # Кнопки для добавления столбцов группировки
        group_add_buttons_layout = QHBoxLayout()
        
        self.add_group_btn = QPushButton("➡ Добавить")
        self.add_group_btn.setObjectName("addGroupBtn")
        self.add_group_btn.clicked.connect(self.add_group_column)
        
        self.add_all_group_btn = QPushButton("➡➡ Все")
        self.add_all_group_btn.setObjectName("addAllGroupBtn")
        self.add_all_group_btn.clicked.connect(self.add_all_group_columns)
        
        group_add_buttons_layout.addWidget(self.add_group_btn)
        group_add_buttons_layout.addWidget(self.add_all_group_btn)
        group_layout.addLayout(group_add_buttons_layout)
        
        # Выбранные столбцы для группировки
        self.group_columns = QListWidget()
        self.group_columns.setObjectName("groupColumns")
        self.group_columns.setSelectionMode(QListWidget.MultiSelection)
        group_layout.addWidget(QLabel("Столбцы для группировки:"))
        group_layout.addWidget(self.group_columns)
        
        # Кнопки для удаления столбцов группировки
        group_remove_buttons_layout = QHBoxLayout()
        
        self.remove_group_btn = QPushButton("⬅ Удалить")
        self.remove_group_btn.setObjectName("removeGroupBtn")
        self.remove_group_btn.clicked.connect(self.remove_group_column)
        
        self.remove_all_group_btn = QPushButton("⬅⬅ Все")
        self.remove_all_group_btn.setObjectName("removeAllGroupBtn")
        self.remove_all_group_btn.clicked.connect(self.remove_all_group_columns)
        
        group_remove_buttons_layout.addWidget(self.remove_group_btn)
        group_remove_buttons_layout.addWidget(self.remove_all_group_btn)
        group_layout.addLayout(group_remove_buttons_layout)
        
        group_tab_layout.addWidget(group_group)
        
        # Группа агрегатных функций - переделаем в стиле 1-й вкладки
        agg_group = QGroupBox("Агрегатные функции")
        agg_group.setObjectName("aggGroup")
        agg_layout = QVBoxLayout()
        agg_group.setLayout(agg_layout)
        
        # Кнопки для добавления агрегатных функций
        agg_add_buttons_layout = QHBoxLayout()
        
        self.add_agg_btn = QPushButton("➕ Добавить функцию")
        self.add_agg_btn.setObjectName("addAggBtn")
        self.add_agg_btn.clicked.connect(self.add_aggregate_function)
        
        agg_add_buttons_layout.addWidget(self.add_agg_btn)
        agg_add_buttons_layout.addStretch()
        agg_layout.addLayout(agg_add_buttons_layout)
        
        # Выбранные агрегатные функции
        self.agg_functions = QListWidget()
        self.agg_functions.setObjectName("aggFunctions")
        agg_layout.addWidget(QLabel("Агрегатные функции:"))
        agg_layout.addWidget(self.agg_functions)
        
        # Кнопки для удаления агрегатных функций
        agg_remove_buttons_layout = QHBoxLayout()
        
        self.remove_agg_btn = QPushButton("⬅ Удалить")
        self.remove_agg_btn.setObjectName("removeAggBtn")
        self.remove_agg_btn.clicked.connect(self.remove_aggregate_function)
        
        self.remove_all_agg_btn = QPushButton("⬅⬅ Все")
        self.remove_all_agg_btn.setObjectName("removeAllAggBtn")
        self.remove_all_agg_btn.clicked.connect(self.remove_all_aggregate_functions)
        
        agg_remove_buttons_layout.addWidget(self.remove_agg_btn)
        agg_remove_buttons_layout.addWidget(self.remove_all_agg_btn)
        agg_layout.addLayout(agg_remove_buttons_layout)
        
        group_tab_layout.addWidget(agg_group)
        
        # Группа HAVING
        having_group = QGroupBox("HAVING (Условия для групп)")
        having_group.setObjectName("havingGroup")
        having_layout = QVBoxLayout()
        having_group.setLayout(having_layout)
        
        self.having_input = QLineEdit()
        self.having_input.setObjectName("havingInput")
        self.having_input.setPlaceholderText("Например: COUNT(*) > 5")
        having_layout.addWidget(self.having_input)
        
        # Метка для отображения ошибок/успеха валидации HAVING
        self.having_error_label = QLabel()
        self.having_error_label.setObjectName("havingErrorLabel")
        self.having_error_label.setWordWrap(True)
        self.having_error_label.hide()
        having_layout.addWidget(self.having_error_label)
        
        group_tab_layout.addWidget(having_group)
        
        # Добавляем вкладку группировки
        tab_widget.addTab(group_tab, "Группировка и агрегаты")
        
        # Добавляем вкладки в основной layout
        layout.addWidget(tab_widget)
        
        return panel
        
        
    def populate_tables(self):
        """Заполняет список таблиц"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            tables = self.db_instance.get_tables()
            self.table_combo.clear()
            self.table_combo.addItems(tables)
            
            # Заполняем столбцы для первой таблицы
            if tables:
                self.populate_columns(tables[0])
                
        except Exception as e:
            self.show_error(f"Ошибка при получении списка таблиц: {e}")
            
    def populate_columns(self, table_name):
        """Заполняет список столбцов для выбранной таблицы"""
        try:
            if not table_name or not self.db_instance or not self.db_instance.is_connected():
                return
                
            columns = self.db_instance.get_table_columns(table_name)
            
            # Очищаем списки
            self.available_columns.clear()
            self.selected_columns.clear()
            self.group_columns.clear()
            self.agg_functions.clear()
            
            # Очищаем новые списки
            self.available_order_columns.clear()
            self.available_group_columns.clear()
            
            # Очищаем виджеты сортировки
            self.clear_all_sort_widgets()
            
            # Заполняем доступные столбцы
            self.available_columns.addItems(columns)
            self.available_group_columns.addItems(columns)
            
            # Для сортировки используем выбранные столбцы (которые могут иметь алиасы)
            # Пока что используем базовые столбцы, но обновим их при изменении выбранных столбцов
            self.available_order_columns.addItems(columns)
            
        except Exception as e:
            self.show_error(f"Ошибка при получении столбцов: {e}")
            
    def add_selected_columns(self):
        """Добавляет выбранные столбцы в список выбранных"""
        selected_items = self.available_columns.selectedItems()
        for item in selected_items:
            if self.selected_columns.findItems(item.text(), Qt.MatchExactly):
                continue
            self.selected_columns.addItem(item.text())
        
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
            
    def add_all_columns(self):
        """Добавляет все столбцы в список выбранных"""
        self.selected_columns.clear()
        for i in range(self.available_columns.count()):
            item = self.available_columns.item(i)
            self.selected_columns.addItem(item.text())
        
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
            
    def remove_selected_columns(self):
        """Удаляет выбранные столбцы из списка выбранных"""
        selected_items = self.selected_columns.selectedItems()
        for item in selected_items:
            self.selected_columns.takeItem(self.selected_columns.row(item))
        
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
            
    def remove_all_columns(self):
        """Удаляет все столбцы из списка выбранных"""
        self.selected_columns.clear()
        
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
        
    def update_available_order_columns(self):
        """Обновляет доступные столбцы для сортировки на основе выбранных столбцов и агрегатных функций"""
        self.available_order_columns.clear()
        
        # Добавляем выбранные столбцы (которые могут иметь алиасы)
        for i in range(self.selected_columns.count()):
            column_text = self.selected_columns.item(i).text()
            self.available_order_columns.addItem(column_text)
        
        # Добавляем агрегатные функции с их алиасами
        for i in range(self.agg_functions.count()):
            agg_text = self.agg_functions.item(i).text()
            # Извлекаем алиас из агрегатной функции (формат: "FUNCTION(column) AS alias")
            if " AS " in agg_text:
                # Извлекаем алиас из строки типа "MAX(reader_id) AS mx"
                alias = agg_text.split(" AS ")[-1].strip('"')
                self.available_order_columns.addItem(alias)
        
    def add_group_column(self):
        """Добавляет столбец для группировки"""
        selected_items = self.available_group_columns.selectedItems()
        for item in selected_items:
            if self.group_columns.findItems(item.text(), Qt.MatchExactly):
                continue
            self.group_columns.addItem(item.text())
            
    def add_all_group_columns(self):
        """Добавляет все столбцы для группировки"""
        self.group_columns.clear()
        for i in range(self.available_group_columns.count()):
            item = self.available_group_columns.item(i)
            self.group_columns.addItem(item.text())
            
    def remove_group_column(self):
        """Удаляет столбец из группировки"""
        selected_items = self.group_columns.selectedItems()
        for item in selected_items:
            self.group_columns.takeItem(self.group_columns.row(item))
            
    def remove_all_group_columns(self):
        """Удаляет все столбцы из группировки"""
        self.group_columns.clear()
            
    def add_aggregate_function(self):
        """Добавляет агрегатную функцию"""
        # Создаем диалог для выбора агрегатной функции
        dialog = AggregateFunctionDialog(self.selected_columns, self)
        if dialog.exec() == QDialog.Accepted:
            agg_func = dialog.get_aggregate_function()
            if agg_func:
                self.agg_functions.addItem(agg_func)
                # Обновляем доступные столбцы для сортировки
                self.update_available_order_columns()
                
    def remove_aggregate_function(self):
        """Удаляет агрегатную функцию"""
        selected_items = self.agg_functions.selectedItems()
        for item in selected_items:
            self.agg_functions.takeItem(self.agg_functions.row(item))
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
            
    def remove_all_aggregate_functions(self):
        """Удаляет все агрегатные функции"""
        self.agg_functions.clear()
        # Обновляем доступные столбцы для сортировки
        self.update_available_order_columns()
            
    def add_order_column(self):
        """Добавляет столбец для сортировки"""
        selected_items = self.available_order_columns.selectedItems()
        for item in selected_items:
            column_name = item.text()
            # Проверяем, не добавлен ли уже этот столбец
            if not self.is_sort_column_added(column_name):
                self.add_sort_widget(column_name)
                
    def add_all_order_columns(self):
        """Добавляет все столбцы для сортировки"""
        self.clear_all_sort_widgets()
        for i in range(self.available_order_columns.count()):
            item = self.available_order_columns.item(i)
            self.add_sort_widget(item.text())
            
    def add_sort_widget(self, column_name):
        """Добавляет виджет сортировки для столбца"""
        sort_widget = SortColumnWidget(column_name, self.sort_widgets_container)
        sort_widget.setParent(self.sort_widgets_container)
        self.sort_widgets_layout.addWidget(sort_widget)
        
        # Принудительно обновляем отображение
        sort_widget.direction_combo.setCurrentIndex(0)
        sort_widget.direction_combo.setCurrentText("ASC")
        sort_widget.direction_combo.update()
        
        # Подключаем сигнал удаления напрямую
        sort_widget.remove_btn.clicked.connect(lambda: self.remove_sort_widget(sort_widget))
        
        # Принудительно применяем стили к новому виджету
        sort_widget.setStyleSheet("""
            SortColumnWidget {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                margin: 2px;
                padding: 5px;
            }
            
            #sortColumnLabel {
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #sortDirectionCombo {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-width: 60px;
            }
            
            #sortDirectionCombo:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            #sortDirectionCombo::drop-down {
                border: none;
                width: 15px;
            }
            
            #sortDirectionCombo::down-arrow {
                image: none;
                border: 2px solid #64ffda;
                width: 4px;
                height: 4px;
                background: #64ffda;
                border-radius: 2px;
            }
            
            #sortDirectionCombo QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #44475a;
                border-radius: 4px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 12px;
            }
            
            #sortDirectionCombo QAbstractItemView::item {
                padding: 6px;
                border-bottom: 1px solid #44475a40;
            }
            
            #sortDirectionCombo QAbstractItemView::item:hover {
                background-color: rgba(100, 255, 218, 0.2);
            }
            
            #sortDirectionCombo QAbstractItemView::item:selected {
                background-color: #64ffda;
                color: #0a0a0f;
            }
            
            #removeSortBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: 1px solid #ff6b6b;
                border-radius: 4px;
                color: #ffffff;
                font-size: 10px;
                font-weight: bold;
            }
            
            #removeSortBtn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
                border: 2px solid #ff6b6b;
            }
        """)
        
    def is_sort_column_added(self, column_name):
        """Проверяет, добавлен ли уже столбец для сортировки"""
        for i in range(self.sort_widgets_layout.count()):
            widget = self.sort_widgets_layout.itemAt(i).widget()
            if isinstance(widget, SortColumnWidget) and widget.column_name == column_name:
                return True
        return False
        
    def remove_sort_widget(self, widget):
        """Удаляет виджет сортировки"""
        print(f"Удаляем виджет сортировки: {widget.column_name}")  # Отладочная информация
        # Удаляем виджет из layout
        self.sort_widgets_layout.removeWidget(widget)
        # Удаляем виджет
        widget.deleteLater()
            
    def clear_all_sort_widgets(self):
        """Удаляет все виджеты сортировки"""
        while self.sort_widgets_layout.count():
            child = self.sort_widgets_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            
    def execute_and_send_query(self):
        """Выполняет запрос и сразу отправляет результаты в главную таблицу"""
        try:
            # Проверяем подключение к базе данных
            if not self.db_instance or not self.db_instance.is_connected():
                self.show_error("Нет подключения к базе данных")
                return
                
            # Строим SQL запрос
            sql_query = self.build_sql_query()
            
            if not sql_query:
                self.show_error("Не удалось построить запрос. Убедитесь, что выбрана таблица и столбцы.")
                return
                
            # Выполняем запрос
            results = self.db_instance.execute_custom_query(sql_query)
            
            if not results:
                self.show_error("Запрос не вернул результатов")
                return
                
            # Отправляем результаты в главную таблицу
            self.results_to_main_table.emit(results)
            
            # Показываем уведомление об успехе
            self.show_info(f"Запрос выполнен успешно! Найдено {len(results)} записей. Результаты отправлены в главную таблицу.")
            
            # Закрываем диалог
            self.accept()
            
        except Exception as e:
            error_msg = f"Ошибка при выполнении запроса: {e}"
            self.show_error(error_msg)
            
    def build_sql_query(self):
        """Строит SQL запрос на основе настроек"""
        try:
            table_name = self.table_combo.currentText()
            if not table_name:
                return None
                
            # SELECT часть
            select_parts = []
            
            # Добавляем выбранные столбцы
            for i in range(self.selected_columns.count()):
                column = self.selected_columns.item(i).text()
                select_parts.append(f'"{column}"')
                
            # Добавляем агрегатные функции
            for i in range(self.agg_functions.count()):
                agg_func = self.agg_functions.item(i).text()
                select_parts.append(agg_func)
                
            if not select_parts:
                select_parts = ["*"]
                
            select_clause = "SELECT " + ", ".join(select_parts)
            
            # FROM часть
            from_clause = f'FROM "{table_name}"'
            
            # WHERE часть
            where_clause = ""
            where_condition = self.where_input.text().strip()
            if where_condition:
                where_clause = f"WHERE {where_condition}"
                
            # GROUP BY часть
            group_clause = ""
            group_columns = []
            for i in range(self.group_columns.count()):
                group_columns.append(f'"{self.group_columns.item(i).text()}"')
            if group_columns:
                group_clause = f"GROUP BY {', '.join(group_columns)}"
                
            # HAVING часть
            having_clause = ""
            having_condition = self.having_input.text().strip()
            if having_condition:
                having_clause = f"HAVING {having_condition}"
                
            # ORDER BY часть - новый интерфейс с индивидуальным направлением
            order_clause = ""
            order_columns = []
            for i in range(self.sort_widgets_layout.count()):
                widget = self.sort_widgets_layout.itemAt(i).widget()
                if isinstance(widget, SortColumnWidget):
                    order_columns.append(widget.get_sort_clause())
            if order_columns:
                order_clause = f"ORDER BY {', '.join(order_columns)}"
                
            # Собираем полный запрос
            query_parts = [select_clause, from_clause]
            if where_clause:
                query_parts.append(where_clause)
            if group_clause:
                query_parts.append(group_clause)
            if having_clause:
                query_parts.append(having_clause)
            if order_clause:
                query_parts.append(order_clause)
                
            return " ".join(query_parts)
            
        except Exception as e:
            self.show_error(f"Ошибка при построении запроса: {e}")
            return None
            
        
    def preview_sql(self):
        """Показывает предварительный просмотр SQL запроса"""
        try:
            sql_query = self.build_sql_query()
            if not sql_query:
                self.show_error("Не удалось построить запрос. Убедитесь, что выбрана таблица и столбцы.")
                return
                
            # Создаем диалог для показа SQL
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
            from PySide6.QtCore import Qt
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Предварительный просмотр SQL")
            dialog.setModal(True)
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            dialog.setLayout(layout)
            
            # Текстовое поле для SQL
            sql_text = QTextEdit()
            sql_text.setPlainText(sql_query)
            sql_text.setReadOnly(True)
            sql_text.setFont(QFont("Consolas", 12))
            layout.addWidget(sql_text)
            
            # Кнопки
            buttons_layout = QHBoxLayout()
            
            copy_button = QPushButton(" Копировать")
            copy_button.clicked.connect(lambda: self.copy_to_clipboard(sql_query))
            
            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.accept)
            
            buttons_layout.addWidget(copy_button)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_button)
            layout.addLayout(buttons_layout)
            
            # Применяем стили
            dialog.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #0a0a0f, 
                                              stop: 1 #1a1a2e);
                    border: 2px solid #44475a;
                    border-radius: 10px;
                }
                QTextEdit {
                    background: rgba(15, 15, 25, 0.8);
                    border: 2px solid #44475a;
                    border-radius: 6px;
                    padding: 10px;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    color: #f8f8f2;
                    font-size: 12px;
                }
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #44475a, 
                                              stop: 1 #2a2a3a);
                    border: 2px solid #6272a4;
                    border-radius: 6px;
                    color: #f8f8f2;
                    font-size: 12px;
                    font-weight: bold;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    padding: 8px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #6272a4, 
                                              stop: 1 #44475a);
                    border: 2px solid #64ffda;
                    color: #64ffda;
                }
            """)
            
            dialog.exec()
            
        except Exception as e:
            self.show_error(f"Ошибка при создании предварительного просмотра: {e}")
            
    def copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена"""
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.show_info("SQL запрос скопирован в буфер обмена")
        except Exception as e:
            self.show_error(f"Ошибка при копировании: {e}")
            
    def show_info(self, message):
        """Показывает информационное сообщение"""
        QMessageBox.information(self, "Информация", message)
        
        
    def clear_all(self):
        """Очищает все настройки"""
        self.selected_columns.clear()
        self.group_columns.clear()
        self.agg_functions.clear()
        self.where_input.clear()
        self.having_input.clear()
        
        # Очищаем ошибки валидации
        self.clear_where_error()
        self.clear_having_error()
        
        # Очищаем новые списки
        self.available_order_columns.clear()
        self.available_group_columns.clear()
        
        # Очищаем виджеты сортировки
        self.clear_all_sort_widgets()
        
        # Очищаем результаты
        self.last_query_results = []
        
    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        QMessageBox.warning(self, "Ошибка", message)
        
    def validate_where_condition(self, text):
        """Валидирует SQL условие WHERE в реальном времени"""
        text = text.strip()
        
        if not text:
            self.clear_where_error()
            return
            
        # Проверяем базовую структуру SQL
        is_valid, error_message, success_message = self.validate_sql_condition(text)
        
        if not is_valid:
            self.set_where_error(error_message)
        else:
            if success_message:
                self.set_where_success(success_message)
            else:
                self.clear_where_error()
                
    def validate_sql_condition(self, condition):
        """Валидирует SQL условие и возвращает (is_valid, error_message, success_message)"""
        import re
        
        # Удаляем лишние пробелы
        condition = re.sub(r'\s+', ' ', condition.strip())
        
        if not condition:
            return True, "", ""
            
        # Проверяем на опасные SQL конструкции
        dangerous_patterns = [
            r'\b(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|TRUNCATE)\b',
            r'\b(EXEC|EXECUTE|sp_|xp_)\b',
            r'--',  # SQL комментарии
            r'/\*.*?\*/',  # Блочные комментарии
            r';\s*$',  # Точка с запятой в конце
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, condition, re.IGNORECASE):
                return False, "✕ Запрещенные SQL конструкции", ""
        
        # Проверяем на базовые SQL операторы
        allowed_operators = ['=', '!=', '<>', '<', '>', '<=', '>=', 'LIKE', 'ILIKE', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL']
        logical_operators = ['AND', 'OR', 'NOT']
        
        # Простая проверка на корректность скобок
        if condition.count('(') != condition.count(')'):
            return False, "✕ Несбалансированные скобки", ""
            
        # Проверяем на пустые условия
        if condition in ['AND', 'OR', 'NOT']:
            return False, "✕ Неполное условие", ""
            
        # Проверяем на корректность строковых литералов
        if condition.count("'") % 2 != 0:
            return False, "✕ Незакрытые кавычки", ""
            
        # Проверяем на корректность LIKE с экранированием
        if 'LIKE' in condition.upper() or 'ILIKE' in condition.upper():
            if not re.search(r"LIKE\s+['\"].*['\"]", condition, re.IGNORECASE):
                return False, "✕ LIKE должен содержать строковый литерал", ""
        
        # Если все проверки пройдены
        return True, "", "✓ Валидное SQL условие"
        
    def set_where_error(self, message):
        """Устанавливает ошибку для поля WHERE"""
        self.where_error_label.setText(message)
        self.where_error_label.setProperty("class", "error-label")
        self.where_error_label.setStyleSheet(self.styleSheet())
        self.where_error_label.show()
        
        # Подсветка поля ввода
        self.where_input.setProperty("class", "error")
        self.where_input.setStyleSheet(self.styleSheet())
        
    def set_where_success(self, message):
        """Устанавливает успех для поля WHERE"""
        self.where_error_label.setText(message)
        self.where_error_label.setProperty("class", "success-label")
        self.where_error_label.setStyleSheet(self.styleSheet())
        self.where_error_label.show()
        
        # Подсветка поля ввода
        self.where_input.setProperty("class", "success")
        self.where_input.setStyleSheet(self.styleSheet())
        
    def clear_where_error(self):
        """Очищает ошибку для поля WHERE"""
        self.where_error_label.hide()
        self.where_error_label.setText("")
        self.where_error_label.setProperty("class", "error-label")
        self.where_error_label.setStyleSheet(self.styleSheet())
        
        # Убираем подсветку поля ввода
        self.where_input.setProperty("class", "")
        self.where_input.setStyleSheet(self.styleSheet())
        
    def validate_having_condition(self, text):
        """Валидирует SQL условие HAVING в реальном времени"""
        text = text.strip()
        
        if not text:
            self.clear_having_error()
            return
            
        # Проверяем базовую структуру SQL
        is_valid, error_message, success_message = self.validate_sql_condition(text)
        
        if not is_valid:
            self.set_having_error(error_message)
        else:
            if success_message:
                self.set_having_success(success_message)
            else:
                self.clear_having_error()
                
    def set_having_error(self, message):
        """Устанавливает ошибку для поля HAVING"""
        self.having_error_label.setText(message)
        self.having_error_label.setProperty("class", "error-label")
        self.having_error_label.setStyleSheet(self.styleSheet())
        self.having_error_label.show()
        
        # Подсветка поля ввода
        self.having_input.setProperty("class", "error")
        self.having_input.setStyleSheet(self.styleSheet())
        
    def set_having_success(self, message):
        """Устанавливает успех для поля HAVING"""
        self.having_error_label.setText(message)
        self.having_error_label.setProperty("class", "success-label")
        self.having_error_label.setStyleSheet(self.styleSheet())
        self.having_error_label.show()
        
        # Подсветка поля ввода
        self.having_input.setProperty("class", "success")
        self.having_input.setStyleSheet(self.styleSheet())
        
    def clear_having_error(self):
        """Очищает ошибку для поля HAVING"""
        self.having_error_label.hide()
        self.having_error_label.setText("")
        self.having_error_label.setProperty("class", "error-label")
        self.having_error_label.setStyleSheet(self.styleSheet())
        
        # Убираем подсветку поля ввода
        self.having_input.setProperty("class", "")
        self.having_input.setStyleSheet(self.styleSheet())
        
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            /* Основной диалог */
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 2px solid #44475a;
                border-radius: 10px;
            }
            
            /* Заголовок */
            #headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 15px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
                border: 1px solid #64ffda;
            }
            
            
            /* Вкладки */
            #tabWidget {
                background: transparent;
            }
            
            QTabWidget::pane {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.6);
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 10px 15px;
                margin-right: 2px;
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QTabBar::tab:selected {
                background: rgba(100, 255, 218, 0.2);
                border-color: #64ffda;
                color: #64ffda;
            }
            
            QTabBar::tab:hover {
                background: rgba(100, 255, 218, 0.1);
                border-color: #6272a4;
            }
            
            /* Панель */
            #queryPanel {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 8px;
                padding: 10px;
            }
            
            /* Группы */
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin: 10px 0;
                padding: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background: rgba(10, 10, 15, 0.9);
            }
            
            /* Метки */
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            /* Выпадающие списки */
            QComboBox {
                background: rgba(25, 25, 35, 0.9);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox#tableCombo {
                background: rgba(25, 25, 35, 0.9);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox#tableCombo:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QComboBox#tableCombo::drop-down {
                border: none;
                background: rgba(25, 25, 35, 0.9);
            }
            
            QComboBox#tableCombo::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64ffda;
                margin-right: 5px;
            }
            
            QComboBox#tableCombo QAbstractItemView {
                background: rgba(25, 25, 35, 0.95);
                border: 2px solid #64ffda;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QComboBox#sortDirectionCombo {
                background: rgba(25, 25, 35, 0.9);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox#sortDirectionCombo:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QComboBox#sortDirectionCombo QAbstractItemView {
                background: rgba(25, 25, 35, 0.95);
                border: 2px solid #64ffda;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QComboBox:editable {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #64ffda;
            }
            
            QComboBox:editable:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QComboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            /* Поля ввода */
            QLineEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QLineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QLineEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #64ffda;
                width: 6px;
                height: 6px;
                background: #64ffda;
                border-radius: 3px;
            }
            
            QComboBox QAbstractItemView {
                background: rgba(25, 25, 35, 0.95);
                border: 2px solid #44475a;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid #44475a40;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: rgba(100, 255, 218, 0.2);
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #64ffda;
                color: #0a0a0f;
            }
            
            
            /* Списки */
            QListWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QListWidget:focus {
                border: 2px solid #64ffda;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #44475a40;
            }
            
            QListWidget::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
            }
            
            QListWidget::item:hover {
                background-color: rgba(100, 255, 218, 0.2);
            }
            
            /* Кнопки */
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #6272a4;
                border-radius: 6px;
                color: #f8f8f2;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 12px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a3a, 
                                          stop: 1 #1a1a2e);
                padding: 7px 11px;
            }
            
            /* Кнопки сортировки и группировки */
            #addOrderBtn, #addAllOrderBtn,
            #addGroupBtn, #removeGroupBtn, #addAllGroupBtn, #removeAllGroupBtn,
            #addAggBtn, #removeAggBtn, #removeAllAggBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                border-radius: 6px;
                color: #64ffda;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 6px 10px;
                min-width: 60px;
            }
            
            #addOrderBtn:hover, #addAllOrderBtn:hover,
            #addGroupBtn:hover, #removeGroupBtn:hover, #addAllGroupBtn:hover, #removeAllGroupBtn:hover,
            #addAggBtn:hover, #removeAggBtn:hover, #removeAllAggBtn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #64ffda, 
                                          stop: 1 #50e3c2);
                color: #0a0a0f;
            }
            
            /* Контейнер для виджетов сортировки */
            #sortWidgetsContainer {
                background: rgba(15, 15, 25, 0.6);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 10px;
                min-height: 100px;
            }
            
            /* Виджет сортировки */
            SortColumnWidget {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                margin: 2px;
                padding: 5px;
            }
            
            #sortColumnLabel {
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #sortDirectionCombo {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-width: 60px;
            }
            
            #sortDirectionCombo:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            #sortDirectionCombo::drop-down {
                border: none;
                width: 15px;
            }
            
            #sortDirectionCombo::down-arrow {
                image: none;
                border: 2px solid #64ffda;
                width: 4px;
                height: 4px;
                background: #64ffda;
                border-radius: 2px;
            }
            
            #sortDirectionCombo QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #44475a;
                border-radius: 4px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 12px;
            }
            
            #sortDirectionCombo QAbstractItemView::item {
                padding: 6px;
                border-bottom: 1px solid #44475a40;
            }
            
            #sortDirectionCombo QAbstractItemView::item:hover {
                background-color: rgba(100, 255, 218, 0.2);
            }
            
            #sortDirectionCombo QAbstractItemView::item:selected {
                background-color: #64ffda;
                color: #0a0a0f;
            }
            
            #sortDirectionCombo::drop-down {
                border: none;
                width: 15px;
            }
            
            #sortDirectionCombo::down-arrow {
                image: none;
                border: 2px solid #64ffda;
                width: 4px;
                height: 4px;
                background: #64ffda;
                border-radius: 2px;
            }
            
            #removeSortBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: 1px solid #ff6b6b;
                border-radius: 4px;
                color: #ffffff;
                font-size: 10px;
                font-weight: bold;
            }
            
            #removeSortBtn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
                border: 2px solid #ff6b6b;
            }
            
            /* Специальные кнопки */
            #executeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 120px;
            }
            
            #executeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }
            
            #clearButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 120px;
            }
            
            #clearButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
                border: 2px solid #ff6b6b;
            }
            
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: none;
                border-radius: 6px;
                color: #f8f8f2;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 120px;
            }
            
            #closeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #6272a4;
            }
            
            #previewButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ffd700, 
                                          stop: 1 #ffb347);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-width: 120px;
            }
            
            #previewButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ffed4e, 
                                          stop: 1 #ffa726);
                border: 2px solid #ffd700;
            }
            
            
            
            /* Скроллбары */
            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #64ffda;
                border-radius: 6px;
                min-height: 25px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #50e3c2;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* Горизонтальные скроллбары */
            QScrollBar:horizontal {
                border: none;
                background: #1a1a2e;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background: #64ffda;
                border-radius: 6px;
                min-width: 25px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #50e3c2;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            /* Скролл-область */
            #mainScrollArea {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.6);
            }
            
            #mainScrollArea QWidget {
                background: transparent;
            }
            
            /* Контент-виджет */
            #contentWidget {
                background: transparent;
            }
            
            /* Стили для валидации WHERE */
            QLineEdit.error, QComboBox.error, QTextEdit.error, QSpinBox.error, QDoubleSpinBox.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }
            
            QLineEdit.success, QComboBox.success, QTextEdit.success, QSpinBox.success, QDoubleSpinBox.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }
            
            .error-label {
                color: #ff5555;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #ff5555;
            }
            
            .success-label {
                color: #50fa7b;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #50fa7b;
            }
        """)


class AggregateFunctionDialog(QDialog):
    """Диалог для выбора агрегатной функции"""
    
    def __init__(self, columns_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить агрегатную функцию")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Выбор функции
        layout.addWidget(QLabel("Функция:"))
        self.function_combo = QComboBox()
        self.function_combo.addItems([
            "COUNT(*)", "COUNT(column)", "SUM(column)", "AVG(column)", 
            "MIN(column)", "MAX(column)", "DISTINCT column"
        ])
        layout.addWidget(self.function_combo)
        
        # Выбор столбца
        layout.addWidget(QLabel("Столбец:"))
        self.column_combo = QComboBox()
        self.column_combo.setEditable(False)  # Только выбор, без ввода с клавиатуры
        self.column_combo.setInsertPolicy(QComboBox.NoInsert)
        for i in range(columns_list.count()):
            column_text = columns_list.item(i).text()
            # Добавляем алиас если он есть (формат: "column_name AS alias")
            if " AS " in column_text:
                display_text = column_text
            else:
                display_text = column_text
            self.column_combo.addItem(display_text)
        layout.addWidget(self.column_combo)
        
        # Устанавливаем первый элемент как выбранный по умолчанию
        if self.column_combo.count() > 0:
            self.column_combo.setCurrentIndex(0)
            self.column_combo.setCurrentText(self.column_combo.itemText(0))
        
        # Подключаем обработчик выбора столбца
        self.column_combo.currentTextChanged.connect(self.on_column_selected)
        self.column_combo.currentIndexChanged.connect(self.on_column_index_changed)
        
        # Алиас
        layout.addWidget(QLabel("Алиас (необязательно):"))
        self.alias_input = QLineEdit()
        self.alias_input.setPlaceholderText("Например: total_count")
        layout.addWidget(self.alias_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Подключаем обработчик изменения функции
        self.function_combo.currentTextChanged.connect(self.on_function_changed)
        
        # Принудительно обновляем отображение столбца
        self.update_column_display()
        
        self.apply_styles()
        
    def set_dark_palette(self):
        """Устанавливает тёмную цветовую палитру"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.ToolTipText, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)
        
    def on_function_changed(self, function):
        """Обработчик изменения функции"""
        if function == "COUNT(*)":
            self.column_combo.setEnabled(False)
            self.column_combo.setCurrentText("")  # Очищаем поле для COUNT(*)
        else:
            self.column_combo.setEnabled(True)
            # Если поле пустое, устанавливаем первый доступный столбец
            if not self.column_combo.currentText() or self.column_combo.currentText().strip() == "":
                self.update_column_display()
            
    def on_column_selected(self, column):
        """Обработчик выбора столбца"""
        # Обновляем текст в поле, чтобы показать выбранный столбец
        self.column_combo.setCurrentText(column)
        
    def on_column_index_changed(self, index):
        """Обработчик изменения индекса столбца"""
        if index >= 0:
            column_text = self.column_combo.itemText(index)
            self.column_combo.setCurrentText(column_text)
            
    def update_column_display(self):
        """Принудительно обновляет отображение выбранного столбца"""
        if self.column_combo.count() > 0:
            current_text = self.column_combo.currentText()
            if not current_text or current_text.strip() == "":
                # Если поле пустое, устанавливаем первый элемент
                first_item = self.column_combo.itemText(0)
                self.column_combo.setCurrentText(first_item)
                self.column_combo.setCurrentIndex(0)
            
    def get_aggregate_function(self):
        """Возвращает сформированную агрегатную функцию"""
        function = self.function_combo.currentText()
        alias = self.alias_input.text().strip()
        
        if function == "COUNT(*)":
            result = "COUNT(*)"
        else:
            column = self.column_combo.currentText()
            if column and column.strip():
                result = function.replace("column", f'"{column}"')
            else:
                result = function  # Оставляем как есть, если столбец не выбран
                
        if alias:
            result += f' AS "{alias}"'
            
        return result
        
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 2px solid #44475a;
                border-radius: 10px;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #64ffda;
                width: 6px;
                height: 6px;
                background: #64ffda;
                border-radius: 3px;
            }
            
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #44475a;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid #44475a40;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: rgba(100, 255, 218, 0.2);
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #64ffda;
                color: #0a0a0f;
            }
            
            QLineEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QLineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QLineEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #6272a4;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 12px 16px;
                min-width: 100px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
        """)
