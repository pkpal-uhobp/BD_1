from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QGroupBox, QListWidget,
    QListWidgetItem, QTabWidget, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor


class WindowFunctionDialog(QDialog):
    """Диалог для работы с оконными функциями RANK, LAG, LEAD"""
    
    def __init__(self, db_instance, table_name, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.table_name = table_name
        self.setWindowTitle("Оконные функции (RANK, LAG, LEAD)")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # ��сновной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("ОКОННЫЕ ФУНКЦИИ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Создаем вкладки для разных оконных функций
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tabWidget")
        
        # Вкладка RANK
        self.rank_tab = self.create_rank_tab()
        self.tab_widget.addTab(self.rank_tab, "RANK")
        
        # Вкладка LAG
        self.lag_tab = self.create_lag_tab()
        self.tab_widget.addTab(self.lag_tab, "LAG")
        
        # Вкладка LEAD
        self.lead_tab = self.create_lead_tab()
        self.tab_widget.addTab(self.lead_tab, "LEAD")
        
        main_layout.addWidget(self.tab_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Применить")
        self.apply_button.setObjectName("applyButton")
        self.apply_button.clicked.connect(self.apply_window_function)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Применяем стили
        self.apply_styles()
        
        # Загружаем столбцы таблицы
        self.load_table_columns()
        
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
        
    def load_table_columns(self):
        """Загружает столбцы таблицы"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            columns = self.db_instance.get_table_columns(self.table_name)
            
            # RANK - заполняем списки столбцов
            self.rank_available_partition_columns.addItems(columns)
            self.rank_available_order_columns.addItems(columns)
            
            # LAG - заполняем комбобоксы
            self.lag_column_combo.addItems(columns)
            self.lag_available_partition_columns.addItems(columns)
            self.lag_available_order_columns.addItems(columns)
            
            # LEAD - заполняем комбобоксы
            self.lead_column_combo.addItems(columns)
            self.lead_available_partition_columns.addItems(columns)
            self.lead_available_order_columns.addItems(columns)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить столбцы: {e}")
            
    def create_rank_tab(self):
        """Создает вкладку для функции RANK"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        tab.setLayout(layout)
        
        # Описание
        info_label = QLabel(
            "Функция RANK() присваивает ранг каждой строке в разделе результирующего набора.\n"
            "Строки с одинаковыми значениями получают одинаковый ранг."
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Группа PARTITION BY
        partition_group = QGroupBox("PARTITION BY (Разбиение)")
        partition_group.setObjectName("partitionGroup")
        partition_layout = QVBoxLayout()
        partition_group.setLayout(partition_layout)
        
        partition_layout.addWidget(QLabel("Доступные столбцы:"))
        self.rank_available_partition_columns = QListWidget()
        self.rank_available_partition_columns.setObjectName("availableColumns")
        self.rank_available_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.rank_available_partition_columns)
        
        partition_buttons_layout = QHBoxLayout()
        add_partition_btn = QPushButton(">> Добавить")
        add_partition_btn.setObjectName("addBtn")
        add_partition_btn.clicked.connect(lambda: self.add_partition_columns('rank'))
        partition_buttons_layout.addWidget(add_partition_btn)
        partition_layout.addLayout(partition_buttons_layout)
        
        partition_layout.addWidget(QLabel("Столбцы для разбиения:"))
        self.rank_selected_partition_columns = QListWidget()
        self.rank_selected_partition_columns.setObjectName("selectedColumns")
        self.rank_selected_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.rank_selected_partition_columns)
        
        remove_partition_layout = QHBoxLayout()
        remove_partition_btn = QPushButton("<< Удалить")
        remove_partition_btn.setObjectName("removeBtn")
        remove_partition_btn.clicked.connect(lambda: self.remove_partition_columns('rank'))
        remove_partition_layout.addWidget(remove_partition_btn)
        partition_layout.addLayout(remove_partition_layout)
        
        layout.addWidget(partition_group)
        
        # Группа ORDER BY
        order_group = QGroupBox("ORDER BY (Сортировка)")
        order_group.setObjectName("orderGroup")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        order_layout.addWidget(QLabel("Доступные столбцы:"))
        self.rank_available_order_columns = QListWidget()
        self.rank_available_order_columns.setObjectName("availableColumns")
        self.rank_available_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.rank_available_order_columns)
        
        order_buttons_layout = QHBoxLayout()
        add_order_btn = QPushButton(">> Добавить")
        add_order_btn.setObjectName("addBtn")
        add_order_btn.clicked.connect(lambda: self.add_order_columns('rank'))
        order_buttons_layout.addWidget(add_order_btn)
        order_layout.addLayout(order_buttons_layout)
        
        order_layout.addWidget(QLabel("Столбцы для сортировки:"))
        self.rank_selected_order_columns = QListWidget()
        self.rank_selected_order_columns.setObjectName("selectedColumns")
        self.rank_selected_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.rank_selected_order_columns)
        
        remove_order_layout = QHBoxLayout()
        remove_order_btn = QPushButton("<< Удалить")
        remove_order_btn.setObjectName("removeBtn")
        remove_order_btn.clicked.connect(lambda: self.remove_order_columns('rank'))
        
        # Направление сортировки
        order_direction_layout = QHBoxLayout()
        order_direction_layout.addWidget(QLabel("Направление:"))
        self.rank_order_direction = QComboBox()
        self.rank_order_direction.setObjectName("directionCombo")
        self.rank_order_direction.addItems(["ASC", "DESC"])
        order_direction_layout.addWidget(self.rank_order_direction)
        order_direction_layout.addStretch()
        
        remove_order_layout.addWidget(remove_order_btn)
        order_layout.addLayout(remove_order_layout)
        order_layout.addLayout(order_direction_layout)
        
        layout.addWidget(order_group)
        
        # Алиас для результата
        alias_layout = QFormLayout()
        self.rank_alias_input = QLineEdit()
        self.rank_alias_input.setObjectName("aliasInput")
        self.rank_alias_input.setPlaceholderText("Например: row_rank")
        alias_layout.addRow("Алиас (название столбца):", self.rank_alias_input)
        layout.addLayout(alias_layout)
        
        return tab
        
    def create_lag_tab(self):
        """Создает вкладку для функции LAG"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        tab.setLayout(layout)
        
        # Описание
        info_label = QLabel(
            "Функция LAG() позволяет получить доступ к значению из предыдущей строки.\n"
            "Полезна для сравнения текущего значения с предыдущим."
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Выбор столбца
        column_layout = QFormLayout()
        self.lag_column_combo = QComboBox()
        self.lag_column_combo.setObjectName("columnCombo")
        column_layout.addRow("Столбец:", self.lag_column_combo)
        layout.addLayout(column_layout)
        
        # Смещение
        offset_layout = QFormLayout()
        self.lag_offset_spin = QSpinBox()
        self.lag_offset_spin.setObjectName("offsetSpin")
        self.lag_offset_spin.setMinimum(1)
        self.lag_offset_spin.setMaximum(100)
        self.lag_offset_spin.setValue(1)
        offset_layout.addRow("Смещение (offset):", self.lag_offset_spin)
        layout.addLayout(offset_layout)
        
        # Значение по умолчанию
        default_layout = QFormLayout()
        self.lag_default_input = QLineEdit()
        self.lag_default_input.setObjectName("defaultInput")
        self.lag_default_input.setPlaceholderText("NULL (если оставить пустым)")
        default_layout.addRow("Значение по умолчанию:", self.lag_default_input)
        layout.addLayout(default_layout)
        
        # Группа PARTITION BY
        partition_group = QGroupBox("PARTITION BY (Разбиение)")
        partition_group.setObjectName("partitionGroup")
        partition_layout = QVBoxLayout()
        partition_group.setLayout(partition_layout)
        
        partition_layout.addWidget(QLabel("Доступные столбцы:"))
        self.lag_available_partition_columns = QListWidget()
        self.lag_available_partition_columns.setObjectName("availableColumns")
        self.lag_available_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.lag_available_partition_columns)
        
        partition_buttons_layout = QHBoxLayout()
        add_partition_btn = QPushButton(">> Добавить")
        add_partition_btn.setObjectName("addBtn")
        add_partition_btn.clicked.connect(lambda: self.add_partition_columns('lag'))
        partition_buttons_layout.addWidget(add_partition_btn)
        partition_layout.addLayout(partition_buttons_layout)
        
        partition_layout.addWidget(QLabel("Столбцы для разбиения:"))
        self.lag_selected_partition_columns = QListWidget()
        self.lag_selected_partition_columns.setObjectName("selectedColumns")
        self.lag_selected_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.lag_selected_partition_columns)
        
        remove_partition_layout = QHBoxLayout()
        remove_partition_btn = QPushButton("<< Удалить")
        remove_partition_btn.setObjectName("removeBtn")
        remove_partition_btn.clicked.connect(lambda: self.remove_partition_columns('lag'))
        remove_partition_layout.addWidget(remove_partition_btn)
        partition_layout.addLayout(remove_partition_layout)
        
        layout.addWidget(partition_group)
        
        # Группа ORDER BY
        order_group = QGroupBox("ORDER BY (Сортировка)")
        order_group.setObjectName("orderGroup")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        order_layout.addWidget(QLabel("Доступные столбцы:"))
        self.lag_available_order_columns = QListWidget()
        self.lag_available_order_columns.setObjectName("availableColumns")
        self.lag_available_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.lag_available_order_columns)
        
        order_buttons_layout = QHBoxLayout()
        add_order_btn = QPushButton(">> Добавить")
        add_order_btn.setObjectName("addBtn")
        add_order_btn.clicked.connect(lambda: self.add_order_columns('lag'))
        order_buttons_layout.addWidget(add_order_btn)
        order_layout.addLayout(order_buttons_layout)
        
        order_layout.addWidget(QLabel("Столбцы для сортировки:"))
        self.lag_selected_order_columns = QListWidget()
        self.lag_selected_order_columns.setObjectName("selectedColumns")
        self.lag_selected_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.lag_selected_order_columns)
        
        remove_order_layout = QHBoxLayout()
        remove_order_btn = QPushButton("<< Удалить")
        remove_order_btn.setObjectName("removeBtn")
        remove_order_btn.clicked.connect(lambda: self.remove_order_columns('lag'))
        
        # Направление сортировки
        order_direction_layout = QHBoxLayout()
        order_direction_layout.addWidget(QLabel("Направление:"))
        self.lag_order_direction = QComboBox()
        self.lag_order_direction.setObjectName("directionCombo")
        self.lag_order_direction.addItems(["ASC", "DESC"])
        order_direction_layout.addWidget(self.lag_order_direction)
        order_direction_layout.addStretch()
        
        remove_order_layout.addWidget(remove_order_btn)
        order_layout.addLayout(remove_order_layout)
        order_layout.addLayout(order_direction_layout)
        
        layout.addWidget(order_group)
        
        # Алиас для результата
        alias_layout = QFormLayout()
        self.lag_alias_input = QLineEdit()
        self.lag_alias_input.setObjectName("aliasInput")
        self.lag_alias_input.setPlaceholderText("Например: prev_value")
        alias_layout.addRow("Алиас (название столбца):", self.lag_alias_input)
        layout.addLayout(alias_layout)
        
        return tab
        
    def create_lead_tab(self):
        """Создает вкладку для функции LEAD"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        tab.setLayout(layout)
        
        # Описание
        info_label = QLabel(
            "Функция LEAD() позволяет получить доступ к значению из следующей строки.\n"
            "Полезна для сравнения текущего значения с последующим."
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Выбор столбца
        column_layout = QFormLayout()
        self.lead_column_combo = QComboBox()
        self.lead_column_combo.setObjectName("columnCombo")
        column_layout.addRow("Столбец:", self.lead_column_combo)
        layout.addLayout(column_layout)
        
        # Смещение
        offset_layout = QFormLayout()
        self.lead_offset_spin = QSpinBox()
        self.lead_offset_spin.setObjectName("offsetSpin")
        self.lead_offset_spin.setMinimum(1)
        self.lead_offset_spin.setMaximum(100)
        self.lead_offset_spin.setValue(1)
        offset_layout.addRow("Смещение (offset):", self.lead_offset_spin)
        layout.addLayout(offset_layout)
        
        # Значение по умолчанию
        default_layout = QFormLayout()
        self.lead_default_input = QLineEdit()
        self.lead_default_input.setObjectName("defaultInput")
        self.lead_default_input.setPlaceholderText("NULL (если оставить пустым)")
        default_layout.addRow("Значение по умолчанию:", self.lead_default_input)
        layout.addLayout(default_layout)
        
        # Группа PARTITION BY
        partition_group = QGroupBox("PARTITION BY (Разбиение)")
        partition_group.setObjectName("partitionGroup")
        partition_layout = QVBoxLayout()
        partition_group.setLayout(partition_layout)
        
        partition_layout.addWidget(QLabel("Доступные столбцы:"))
        self.lead_available_partition_columns = QListWidget()
        self.lead_available_partition_columns.setObjectName("availableColumns")
        self.lead_available_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.lead_available_partition_columns)
        
        partition_buttons_layout = QHBoxLayout()
        add_partition_btn = QPushButton(">> Добавить")
        add_partition_btn.setObjectName("addBtn")
        add_partition_btn.clicked.connect(lambda: self.add_partition_columns('lead'))
        partition_buttons_layout.addWidget(add_partition_btn)
        partition_layout.addLayout(partition_buttons_layout)
        
        partition_layout.addWidget(QLabel("Сто��бцы для разбиения:"))
        self.lead_selected_partition_columns = QListWidget()
        self.lead_selected_partition_columns.setObjectName("selectedColumns")
        self.lead_selected_partition_columns.setSelectionMode(QListWidget.MultiSelection)
        partition_layout.addWidget(self.lead_selected_partition_columns)
        
        remove_partition_layout = QHBoxLayout()
        remove_partition_btn = QPushButton("<< Удалить")
        remove_partition_btn.setObjectName("removeBtn")
        remove_partition_btn.clicked.connect(lambda: self.remove_partition_columns('lead'))
        remove_partition_layout.addWidget(remove_partition_btn)
        partition_layout.addLayout(remove_partition_layout)
        
        layout.addWidget(partition_group)
        
        # Группа ORDER BY
        order_group = QGroupBox("ORDER BY (Сортировка)")
        order_group.setObjectName("orderGroup")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        order_layout.addWidget(QLabel("Доступные столбцы:"))
        self.lead_available_order_columns = QListWidget()
        self.lead_available_order_columns.setObjectName("availableColumns")
        self.lead_available_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.lead_available_order_columns)
        
        order_buttons_layout = QHBoxLayout()
        add_order_btn = QPushButton(">> Добавить")
        add_order_btn.setObjectName("addBtn")
        add_order_btn.clicked.connect(lambda: self.add_order_columns('lead'))
        order_buttons_layout.addWidget(add_order_btn)
        order_layout.addLayout(order_buttons_layout)
        
        order_layout.addWidget(QLabel("Столбцы для сортировки:"))
        self.lead_selected_order_columns = QListWidget()
        self.lead_selected_order_columns.setObjectName("selectedColumns")
        self.lead_selected_order_columns.setSelectionMode(QListWidget.MultiSelection)
        order_layout.addWidget(self.lead_selected_order_columns)
        
        remove_order_layout = QHBoxLayout()
        remove_order_btn = QPushButton("<< Удалить")
        remove_order_btn.setObjectName("removeBtn")
        remove_order_btn.clicked.connect(lambda: self.remove_order_columns('lead'))
        
        # Направление сортировки
        order_direction_layout = QHBoxLayout()
        order_direction_layout.addWidget(QLabel("Направление:"))
        self.lead_order_direction = QComboBox()
        self.lead_order_direction.setObjectName("directionCombo")
        self.lead_order_direction.addItems(["ASC", "DESC"])
        order_direction_layout.addWidget(self.lead_order_direction)
        order_direction_layout.addStretch()
        
        remove_order_layout.addWidget(remove_order_btn)
        order_layout.addLayout(remove_order_layout)
        order_layout.addLayout(order_direction_layout)
        
        layout.addWidget(order_group)
        
        # Алиас для результата
        alias_layout = QFormLayout()
        self.lead_alias_input = QLineEdit()
        self.lead_alias_input.setObjectName("aliasInput")
        self.lead_alias_input.setPlaceholderText("Например: next_value")
        alias_layout.addRow("Алиас (название столбца):", self.lead_alias_input)
        layout.addLayout(alias_layout)
        
        return tab
        
    def add_partition_columns(self, function_type):
        """Добавляет столбцы для PARTITION BY"""
        if function_type == 'rank':
            available = self.rank_available_partition_columns
            selected = self.rank_selected_partition_columns
        elif function_type == 'lag':
            available = self.lag_available_partition_columns
            selected = self.lag_selected_partition_columns
        else:  # lead
            available = self.lead_available_partition_columns
            selected = self.lead_selected_partition_columns
            
        selected_items = available.selectedItems()
        for item in selected_items:
            if not selected.findItems(item.text(), Qt.MatchExactly):
                selected.addItem(item.text())
                
    def remove_partition_columns(self, function_type):
        """Удаляет столбцы из PARTITION BY"""
        if function_type == 'rank':
            selected = self.rank_selected_partition_columns
        elif function_type == 'lag':
            selected = self.lag_selected_partition_columns
        else:  # lead
            selected = self.lead_selected_partition_columns
            
        selected_items = selected.selectedItems()
        for item in selected_items:
            selected.takeItem(selected.row(item))
            
    def add_order_columns(self, function_type):
        """Добавляет столбцы для ORDER BY"""
        if function_type == 'rank':
            available = self.rank_available_order_columns
            selected = self.rank_selected_order_columns
        elif function_type == 'lag':
            available = self.lag_available_order_columns
            selected = self.lag_selected_order_columns
        else:  # lead
            available = self.lead_available_order_columns
            selected = self.lead_selected_order_columns
            
        selected_items = available.selectedItems()
        for item in selected_items:
            if not selected.findItems(item.text(), Qt.MatchExactly):
                selected.addItem(item.text())
                
    def remove_order_columns(self, function_type):
        """Удаляет столбцы из ORDER BY"""
        if function_type == 'rank':
            selected = self.rank_selected_order_columns
        elif function_type == 'lag':
            selected = self.lag_selected_order_columns
        else:  # lead
            selected = self.lead_selected_order_columns
            
        selected_items = selected.selectedItems()
        for item in selected_items:
            selected.takeItem(selected.row(item))
            
    def build_window_function_sql(self):
        """Строит SQL для оконной функции"""
        current_tab_index = self.tab_widget.currentIndex()
        
        if current_tab_index == 0:  # RANK
            return self.build_rank_sql()
        elif current_tab_index == 1:  # LAG
            return self.build_lag_sql()
        else:  # LEAD
            return self.build_lead_sql()
            
    def build_rank_sql(self):
        """Строит SQL для RANK()"""
        # PARTITION BY
        partition_columns = []
        for i in range(self.rank_selected_partition_columns.count()):
            partition_columns.append(f'"{self.rank_selected_partition_columns.item(i).text()}"')
            
        # ORDER BY
        order_columns = []
        for i in range(self.rank_selected_order_columns.count()):
            order_columns.append(f'"{self.rank_selected_order_columns.item(i).text()}"')
            
        if not order_columns:
            raise ValueError("Необходимо выбрать хотя бы один столбец для ORDER BY")
            
        direction = self.rank_order_direction.currentText()
        alias = self.rank_alias_input.text().strip() or "rank_value"
        
        sql = "RANK() OVER ("
        if partition_columns:
            sql += f"PARTITION BY {', '.join(partition_columns)} "
        sql += f"ORDER BY {', '.join(order_columns)} {direction}"
        sql += f') AS "{alias}"'
        
        return sql
        
    def build_lag_sql(self):
        """Строит SQL для LAG()"""
        column = self.lag_column_combo.currentText()
        if not column:
            raise ValueError("Необходимо выбрать столбец")
            
        offset = self.lag_offset_spin.value()
        default_value = self.lag_default_input.text().strip()
        
        # PARTITION BY
        partition_columns = []
        for i in range(self.lag_selected_partition_columns.count()):
            partition_columns.append(f'"{self.lag_selected_partition_columns.item(i).text()}"')
            
        # ORDER BY
        order_columns = []
        for i in range(self.lag_selected_order_columns.count()):
            order_columns.append(f'"{self.lag_selected_order_columns.item(i).text()}"')
            
        if not order_columns:
            raise ValueError("Необходимо выбрать хотя бы один столбец для ORDER BY")
            
        direction = self.lag_order_direction.currentText()
        alias = self.lag_alias_input.text().strip() or "lag_value"
        
        # Формируем LAG()
        if default_value:
            sql = f'LAG("{column}", {offset}, {default_value}) OVER ('
        else:
            sql = f'LAG("{column}", {offset}) OVER ('
            
        if partition_columns:
            sql += f"PARTITION BY {', '.join(partition_columns)} "
        sql += f"ORDER BY {', '.join(order_columns)} {direction}"
        sql += f') AS "{alias}"'
        
        return sql
        
    def build_lead_sql(self):
        """Строит SQL для LEAD()"""
        column = self.lead_column_combo.currentText()
        if not column:
            raise ValueError("Необходимо выбрать столбец")
            
        offset = self.lead_offset_spin.value()
        default_value = self.lead_default_input.text().strip()
        
        # PARTITION BY
        partition_columns = []
        for i in range(self.lead_selected_partition_columns.count()):
            partition_columns.append(f'"{self.lead_selected_partition_columns.item(i).text()}"')
            
        # ORDER BY
        order_columns = []
        for i in range(self.lead_selected_order_columns.count()):
            order_columns.append(f'"{self.lead_selected_order_columns.item(i).text()}"')
            
        if not order_columns:
            raise ValueError("Необходимо выбрать хотя бы один столбец для ORDER BY")
            
        direction = self.lead_order_direction.currentText()
        alias = self.lead_alias_input.text().strip() or "lead_value"
        
        # Формируем LEAD()
        if default_value:
            sql = f'LEAD("{column}", {offset}, {default_value}) OVER ('
        else:
            sql = f'LEAD("{column}", {offset}) OVER ('
            
        if partition_columns:
            sql += f"PARTITION BY {', '.join(partition_columns)} "
        sql += f"ORDER BY {', '.join(order_columns)} {direction}"
        sql += f') AS "{alias}"'
        
        return sql
        
    def apply_window_function(self):
        """Применяет оконную функцию"""
        try:
            sql = self.build_window_function_sql()
            self.window_function_sql = sql
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать оконную функцию: {e}")
            
    def get_window_function_sql(self):
        """Возвращает SQL оконной функции"""
        return getattr(self, 'window_function_sql', None)
        
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
            
            #headerLabel {
                font-size: 18px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
            }
            
            #infoLabel {
                color: #8892b0;
                font-size: 12px;
                font-weight: normal;
                font-style: italic;
                background: rgba(136, 146, 176, 0.1);
                border-radius: 6px;
                padding: 10px;
                border-left: 3px solid #64ffda;
            }
            
            QTabWidget::pane {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.6);
            }
            
            QTabBar::tab {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 10px 20px;
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
            
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
                padding-top: 25px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 5px;
                padding: 0 8px;
                background: rgba(10, 10, 15, 0.9);
            }
            
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QListWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 100px;
                max-height: 150px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #44475a40;
            }
            
            QListWidget::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
            }
            
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #ffffff;
                min-height: 25px;
            }
            
            QComboBox:focus {
                border: 2px solid #64ffda;
            }
            
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #44475a;
                color: #ffffff;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }
            
            QLineEdit, QSpinBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #64ffda;
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
                padding: 8px 16px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            
            #applyButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                color: #0a0a0f;
                padding: 10px 20px;
            }
            
            #applyButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
            }
        """)
