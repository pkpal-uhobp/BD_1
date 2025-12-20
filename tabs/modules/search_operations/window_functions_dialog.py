from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFormLayout, QWidget, QGroupBox, QListWidget, 
    QListWidgetItem, QSpinBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor
from plyer import notification

class WindowFunctionDialog(QDialog):
    """Диалог для работы с оконными функциями"""
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Оконные функции")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Переменные для хранения результатов
        self.window_function_expression = ""
        
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
        header_label = QLabel("ОКОННЫЕ ФУНКЦИИ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(header_label)
        
        # Создаем скроллируемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        
        # Контейнер для содержимого
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        # Группа выбора таблицы
        table_group = QGroupBox("Выбор таблицы")
        table_group.setObjectName("groupBox")
        table_layout = QFormLayout()
        table_group.setLayout(table_layout)
        
        self.table_combo = QComboBox()
        self.table_combo.setObjectName("comboBox")
        self.table_combo.setMinimumHeight(35)
        self.table_combo.currentTextChanged.connect(self.load_table_columns)
        table_layout.addRow("Таблица:", self.table_combo)
        
        content_layout.addWidget(table_group)
        
        # Группа выбора оконной функции
        function_group = QGroupBox("Оконная функция")
        function_group.setObjectName("groupBox")
        function_layout = QVBoxLayout()
        function_group.setLayout(function_layout)
        
        # Тип функции
        type_layout = QFormLayout()
        self.function_type_combo = QComboBox()
        self.function_type_combo.setObjectName("comboBox")
        self.function_type_combo.setMinimumHeight(35)
        self.function_type_combo.addItems([
            "ROW_NUMBER - Порядковый номер строки",
            "RANK - Ранг с пропусками",
            "DENSE_RANK - Ранг без пропусков",
            "NTILE - Разбиение на группы",
            "LAG - Значение из предыдущей строки",
            "LEAD - Значение из следующей строки",
            "FIRST_VALUE - Первое значение в окне",
            "LAST_VALUE - Последнее значение в окне",
            "NTH_VALUE - N-ое значение в окне"
        ])
        self.function_type_combo.currentTextChanged.connect(self.on_function_type_changed)
        type_layout.addRow("Функция:", self.function_type_combo)
        function_layout.addLayout(type_layout)
        
        # Контейнер для параметров функции
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        function_layout.addWidget(self.params_widget)
        
        content_layout.addWidget(function_group)
        
        # Группа PARTITION BY
        partition_group = QGroupBox("PARTITION BY (Разбиение на окна)")
        partition_group.setObjectName("groupBox")
        partition_layout = QVBoxLayout()
        partition_group.setLayout(partition_layout)
        
        partition_info = QLabel("Столбцы для разбиения данных на группы")
        partition_info.setWordWrap(True)
        partition_layout.addWidget(partition_info)
        
        # Доступные столбцы для PARTITION BY
        self.available_partition_columns = QListWidget()
        self.available_partition_columns.setObjectName("listWidget")
        self.available_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(QLabel("Доступные столбцы:"))
        partition_layout.addWidget(self.available_partition_columns)
        
        # Кнопки управления
        partition_buttons = QHBoxLayout()
        add_partition_btn = QPushButton(">> Добавить")
        add_partition_btn.setObjectName("addButton")
        add_partition_btn.clicked.connect(self.add_partition_columns)
        partition_buttons.addWidget(add_partition_btn)
        partition_layout.addLayout(partition_buttons)
        
        # Выбранные столбцы PARTITION BY
        self.partition_columns = QListWidget()
        self.partition_columns.setObjectName("listWidget")
        partition_layout.addWidget(QLabel("Столбцы разбиения:"))
        partition_layout.addWidget(self.partition_columns)
        
        # Кнопки удаления
        remove_partition_buttons = QHBoxLayout()
        remove_partition_btn = QPushButton("<< Удалить")
        remove_partition_btn.setObjectName("removeButton")
        remove_partition_btn.clicked.connect(self.remove_partition_columns)
        remove_partition_buttons.addWidget(remove_partition_btn)
        partition_layout.addLayout(remove_partition_buttons)
        
        content_layout.addWidget(partition_group)
        
        # Группа ORDER BY
        order_group = QGroupBox("ORDER BY (Сортировка в окне)")
        order_group.setObjectName("groupBox")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        order_info = QLabel("Столбцы для сортировки строк внутри окна")
        order_info.setWordWrap(True)
        order_layout.addWidget(order_info)
        
        # Доступные столбцы для ORDER BY
        self.available_order_columns = QListWidget()
        self.available_order_columns.setObjectName("listWidget")
        self.available_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(QLabel("Доступные столбцы:"))
        order_layout.addWidget(self.available_order_columns)
        
        # Кнопки управления
        order_buttons = QHBoxLayout()
        add_order_btn = QPushButton(">> Добавить")
        add_order_btn.setObjectName("addButton")
        add_order_btn.clicked.connect(self.add_order_columns)
        order_buttons.addWidget(add_order_btn)
        order_layout.addLayout(order_buttons)
        
        # Выбранные столбцы ORDER BY
        self.order_columns = QListWidget()
        self.order_columns.setObjectName("listWidget")
        order_layout.addWidget(QLabel("Столбцы сортировки:"))
        order_layout.addWidget(self.order_columns)
        
        # Кнопки удаления
        remove_order_buttons = QHBoxLayout()
        remove_order_btn = QPushButton("<< Удалить")
        remove_order_btn.setObjectName("removeButton")
        remove_order_btn.clicked.connect(self.remove_order_columns)
        remove_order_buttons.addWidget(remove_order_btn)
        order_layout.addLayout(remove_order_buttons)
        
        content_layout.addWidget(order_group)
        
        # Устанавливаем содержимое в скролл-область
        scroll_area.setWidget(content_widget)
        self.layout().addWidget(scroll_area)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setObjectName("okButton")
        self.ok_button.clicked.connect(self.accept_dialog)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        self.layout().addLayout(buttons_layout)
        
        # Загружаем начальные данные
        self.load_tables()
        
    def load_tables(self):
        """Загружает список таблиц"""
        if not self.db_instance or not self.db_instance.is_connected():
            return
        
        try:
            tables = self.db_instance.get_tables()
            self.table_combo.clear()
            self.table_combo.addItems(tables)
        except Exception as e:
            notification.notify(
                title="Ошибка",
                message=f"Не удалось загрузить таблицы: {str(e)}",
                timeout=3
            )
    
    def load_table_columns(self, table_name):
        """Загружает столбцы выбранной таблицы"""
        if not table_name:
            return
        
        try:
            columns = self.db_instance.get_table_columns(table_name)
            
            # Очищаем списки
            self.available_partition_columns.clear()
            self.partition_columns.clear()
            self.available_order_columns.clear()
            self.order_columns.clear()
            
            # Заполняем доступные столбцы
            self.available_partition_columns.addItems(columns)
            self.available_order_columns.addItems(columns)
            
        except Exception as e:
            notification.notify(
                title="Ошибка",
                message=f"Не удалось загрузить столбцы: {str(e)}",
                timeout=3
            )
    
    def on_function_type_changed(self, function_text):
        """Обработчик изменения типа функции"""
        # Очищаем параметры
        self.clear_params()
        
        # Создаем параметры для выбранной функции
        function_name = function_text.split(' - ')[0]
        
        if function_name == "NTILE":
            self.create_ntile_params()
        elif function_name in ["LAG", "LEAD"]:
            self.create_lag_lead_params()
        elif function_name == "NTH_VALUE":
            self.create_nth_value_params()
    
    def clear_params(self):
        """Очищает параметры функции"""
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def create_ntile_params(self):
        """Создает параметры для NTILE"""
        label = QLabel("Количество групп:")
        label.setObjectName("paramLabel")
        
        self.ntile_spin = QSpinBox()
        self.ntile_spin.setObjectName("spinBox")
        self.ntile_spin.setMinimum(1)
        self.ntile_spin.setMaximum(1000)
        self.ntile_spin.setValue(4)
        
        self.params_layout.addWidget(label)
        self.params_layout.addWidget(self.ntile_spin)
    
    def create_lag_lead_params(self):
        """Создает параметры для LAG/LEAD"""
        # Столбец
        column_label = QLabel("Столбец:")
        column_label.setObjectName("paramLabel")
        
        self.lag_lead_column = QComboBox()
        self.lag_lead_column.setObjectName("comboBox")
        # Заполним столбцами при выборе таблицы
        if self.table_combo.currentText():
            columns = self.db_instance.get_table_columns(self.table_combo.currentText())
            self.lag_lead_column.addItems(columns)
        
        self.params_layout.addWidget(column_label)
        self.params_layout.addWidget(self.lag_lead_column)
        
        # Смещение
        offset_label = QLabel("Смещение (строк):")
        offset_label.setObjectName("paramLabel")
        
        self.offset_spin = QSpinBox()
        self.offset_spin.setObjectName("spinBox")
        self.offset_spin.setMinimum(1)
        self.offset_spin.setMaximum(1000)
        self.offset_spin.setValue(1)
        
        self.params_layout.addWidget(offset_label)
        self.params_layout.addWidget(self.offset_spin)
    
    def create_nth_value_params(self):
        """Создает параметры для NTH_VALUE"""
        # Столбец
        column_label = QLabel("Столбец:")
        column_label.setObjectName("paramLabel")
        
        self.nth_column = QComboBox()
        self.nth_column.setObjectName("comboBox")
        # Заполним столбцами при выборе таблицы
        if self.table_combo.currentText():
            columns = self.db_instance.get_table_columns(self.table_combo.currentText())
            self.nth_column.addItems(columns)
        
        self.params_layout.addWidget(column_label)
        self.params_layout.addWidget(self.nth_column)
        
        # Позиция
        position_label = QLabel("Позиция (N):")
        position_label.setObjectName("paramLabel")
        
        self.position_spin = QSpinBox()
        self.position_spin.setObjectName("spinBox")
        self.position_spin.setMinimum(1)
        self.position_spin.setMaximum(1000)
        self.position_spin.setValue(1)
        
        self.params_layout.addWidget(position_label)
        self.params_layout.addWidget(self.position_spin)
    
    def add_partition_columns(self):
        """Добавляет столбцы в PARTITION BY"""
        selected = self.available_partition_columns.selectedItems()
        for item in selected:
            if not self.partition_columns.findItems(item.text(), Qt.MatchExactly):
                self.partition_columns.addItem(item.text())
    
    def remove_partition_columns(self):
        """Удаляет столбцы из PARTITION BY"""
        selected = self.partition_columns.selectedItems()
        for item in selected:
            self.partition_columns.takeItem(self.partition_columns.row(item))
    
    def add_order_columns(self):
        """Добавляет столбцы в ORDER BY"""
        selected = self.available_order_columns.selectedItems()
        for item in selected:
            if not self.order_columns.findItems(item.text(), Qt.MatchExactly):
                self.order_columns.addItem(item.text())
    
    def remove_order_columns(self):
        """Удаляет столбцы из ORDER BY"""
        selected = self.order_columns.selectedItems()
        for item in selected:
            self.order_columns.takeItem(self.order_columns.row(item))
    
    def accept_dialog(self):
        """Принимает диалог и формирует выражение оконной функции"""
        function_text = self.function_type_combo.currentText()
        function_name = function_text.split(' - ')[0]
        
        # Формируем выражение функции
        if function_name in ["ROW_NUMBER", "RANK", "DENSE_RANK"]:
            func_expr = f"{function_name}()"
        elif function_name == "NTILE":
            n = getattr(self, 'ntile_spin', None)
            if n:
                func_expr = f"NTILE({n.value()})"
            else:
                func_expr = "NTILE(4)"
        elif function_name in ["LAG", "LEAD"]:
            col = getattr(self, 'lag_lead_column', None)
            offset = getattr(self, 'offset_spin', None)
            if col and offset:
                func_expr = f'{function_name}("{col.currentText()}", {offset.value()})'
            else:
                notification.notify(
                    title="Ошибка",
                    message="Укажите столбец для LAG/LEAD",
                    timeout=3
                )
                return
        elif function_name in ["FIRST_VALUE", "LAST_VALUE"]:
            # Для FIRST_VALUE и LAST_VALUE нужен столбец
            # Используем первый доступный столбец
            if self.available_partition_columns.count() > 0:
                col = self.available_partition_columns.item(0).text()
                func_expr = f'{function_name}("{col}")'
            else:
                notification.notify(
                    title="Ошибка",
                    message="Нет доступных столбцов",
                    timeout=3
                )
                return
        elif function_name == "NTH_VALUE":
            col = getattr(self, 'nth_column', None)
            pos = getattr(self, 'position_spin', None)
            if col and pos:
                func_expr = f'NTH_VALUE("{col.currentText()}", {pos.value()})'
            else:
                notification.notify(
                    title="Ошибка",
                    message="Укажите столбец и позицию для NTH_VALUE",
                    timeout=3
                )
                return
        else:
            func_expr = f"{function_name}()"
        
        # Формируем OVER clause
        over_parts = []
        
        # PARTITION BY
        partition_cols = []
        for i in range(self.partition_columns.count()):
            partition_cols.append(f'"{self.partition_columns.item(i).text()}"')
        
        if partition_cols:
            over_parts.append(f"PARTITION BY {', '.join(partition_cols)}")
        
        # ORDER BY
        order_cols = []
        for i in range(self.order_columns.count()):
            order_cols.append(f'"{self.order_columns.item(i).text()}"')
        
        if order_cols:
            over_parts.append(f"ORDER BY {', '.join(order_cols)}")
        
        # Полное выражение
        if over_parts:
            over_clause = " ".join(over_parts)
            self.window_function_expression = f"{func_expr} OVER ({over_clause})"
        else:
            self.window_function_expression = f"{func_expr} OVER ()"
        
        self.accept()
    
    def get_window_function_expression(self):
        """Возвращает сформированное выражение оконной функции"""
        return self.window_function_expression
    
    def apply_styles(self):
        """Применяет стили к диалогу"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
            }
            
            #headerLabel {
                font-size: 24px;
                font-weight: bold;
                color: #64ffda;
                padding: 15px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QGroupBox {
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                font-size: 14px;
                font-weight: bold;
                color: #f8f8f2;
                background: rgba(15, 15, 25, 0.5);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #64ffda;
                background: rgba(15, 15, 25, 0.8);
                border-radius: 4px;
            }
            
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QComboBox:hover {
                border: 2px solid #64ffda;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                border: 1px solid #44475a;
            }
            
            QListWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px;
                color: #f8f8f2;
            }
            
            QListWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background: #64ffda;
                color: #0a0a0f;
            }
            
            QListWidget::item:hover {
                background: rgba(100, 255, 218, 0.3);
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
                padding: 8px 16px;
                min-width: 100px;
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
                                          stop: 1 #1a1a2a);
            }
            
            #okButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00d4aa);
                color: #0a0a0f;
                border: none;
            }
            
            #okButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
            }
            
            QSpinBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
            }
            
            QSpinBox:hover {
                border: 2px solid #64ffda;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QLabel {
                color: #f8f8f2;
            }
            
            #paramLabel {
                font-weight: bold;
                color: #64ffda;
                font-size: 12px;
            }
        """)
