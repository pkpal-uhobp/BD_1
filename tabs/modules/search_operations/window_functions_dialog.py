from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QGroupBox, QTabWidget, QWidget,
    QSpinBox, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QFormLayout, QCheckBox, QSplitter, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor


class WindowFunctionDialog(QDialog):
    """Диалог для работы с оконными функциями (RANK, LAG, LEAD)"""
    
    def __init__(self, db_instance, table_name, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.table_name = table_name
        self.columns = []
        self.current_results = []
        
        self.setWindowTitle("Оконные функции")
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        
        self.set_dark_palette()
        self.load_table_columns()
        self.init_ui()
        
    def set_dark_palette(self):
        """Устанавливает темную цветовую палитру"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 24))
        palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.Base, QColor(25, 25, 35))
        palette.setColor(QPalette.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.Button, QColor(40, 40, 50))
        palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(palette)
        
    def load_table_columns(self):
        """Загружает столбцы выбранной таблицы"""
        try:
            if self.db_instance and hasattr(self.db_instance, 'get_table_columns'):
                self.columns = self.db_instance.get_table_columns(self.table_name)
            elif self.db_instance and hasattr(self.db_instance, 'connection'):
                cursor = self.db_instance.connection.cursor()
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table_name}'")
                self.columns = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.columns = []
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить столбцы: {e}")
            
    def init_ui(self):
        """Инициализирует пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        header = QLabel("ОКОННЫЕ ФУНКЦИИ")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Создаем сплиттер для разделения настроек и результатов
        splitter = QSplitter(Qt.Vertical)
        
        # Верхняя часть - вкладки с функциями
        tab_widget = QTabWidget()
        
        # Вкладка RANK
        self.rank_tab = self.create_rank_tab()
        tab_widget.addTab(self.rank_tab, "RANK")
        
        # Вкладка LAG
        self.lag_tab = self.create_lag_tab()
        tab_widget.addTab(self.lag_tab, "LAG")
        
        # Вкладка LEAD
        self.lead_tab = self.create_lead_tab()
        tab_widget.addTab(self.lead_tab, "LEAD")
        
        splitter.addWidget(tab_widget)
        
        # Нижняя часть - результаты
        results_widget = self.create_results_panel()
        splitter.addWidget(results_widget)
        
        splitter.setSizes([350, 350])
        layout.addWidget(splitter)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("Выполнить")
        self.execute_btn.setStyleSheet("background-color: #64ffda; color: #000; padding: 10px; font-weight: bold;")
        self.execute_btn.clicked.connect(self.execute_window_function)
        
        self.copy_sql_btn = QPushButton("Копировать SQL")
        self.copy_sql_btn.clicked.connect(self.copy_sql_to_clipboard)
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.copy_sql_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def create_rank_tab(self):
        """Создает вкладку для функции RANK"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Описание
        desc = QLabel("Функция RANK() присваивает ранг каждой строке в разделе набора результатов.")
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background-color: rgba(64, 255, 218, 0.1); border-radius: 5px;")
        layout.addWidget(desc)
        
        # ORDER BY
        order_group = QGroupBox("ORDER BY (обязательно)")
        order_layout = QVBoxLayout()
        
        order_label = QLabel("Столбец для сортировки:")
        self.rank_order_combo = QComboBox()
        self.rank_order_combo.addItems(self.columns)
        self.rank_order_combo.currentTextChanged.connect(self.update_rank_preview)
        
        direction_label = QLabel("Направление сортировки:")
        self.rank_direction_combo = QComboBox()
        self.rank_direction_combo.addItems(["ASC", "DESC"])
        self.rank_direction_combo.currentTextChanged.connect(self.update_rank_preview)
        
        order_layout.addWidget(order_label)
        order_layout.addWidget(self.rank_order_combo)
        order_layout.addWidget(direction_label)
        order_layout.addWidget(self.rank_direction_combo)
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # PARTITION BY
        partition_group = QGroupBox("PARTITION BY (необязательно)")
        partition_layout = QVBoxLayout()
        
        self.rank_use_partition = QCheckBox("Использовать разбиение")
        self.rank_use_partition.stateChanged.connect(self.update_rank_preview)
        
        partition_label = QLabel("Столбец для разбиения:")
        self.rank_partition_combo = QComboBox()
        self.rank_partition_combo.addItems(self.columns)
        self.rank_partition_combo.currentTextChanged.connect(self.update_rank_preview)
        self.rank_partition_combo.setEnabled(False)
        
        self.rank_use_partition.stateChanged.connect(
            lambda state: self.rank_partition_combo.setEnabled(state == Qt.Checked)
        )
        
        partition_layout.addWidget(self.rank_use_partition)
        partition_layout.addWidget(partition_label)
        partition_layout.addWidget(self.rank_partition_combo)
        partition_group.setLayout(partition_layout)
        layout.addWidget(partition_group)
        
        # Предпросмотр SQL
        preview_group = QGroupBox("Предпросмотр SQL")
        preview_layout = QVBoxLayout()
        self.rank_preview = QTextEdit()
        self.rank_preview.setReadOnly(True)
        self.rank_preview.setMaximumHeight(100)
        preview_layout.addWidget(self.rank_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        # Инициализация предпросмотра
        self.update_rank_preview()
        
        return widget
        
    def create_lag_tab(self):
        """Создает вкладку для функции LAG"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Описание
        desc = QLabel("Функция LAG() предоставляет доступ к строке с заданным физическим смещением, которая ПРЕДШЕСТВУЕТ текущей строке.")
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background-color: rgba(64, 255, 218, 0.1); border-radius: 5px;")
        layout.addWidget(desc)
        
        # Параметры
        params_group = QGroupBox("Параметры функции")
        params_layout = QFormLayout()
        
        # Столбец
        self.lag_column_combo = QComboBox()
        self.lag_column_combo.addItems(self.columns)
        self.lag_column_combo.currentTextChanged.connect(self.update_lag_preview)
        params_layout.addRow("Столбец:", self.lag_column_combo)
        
        # Смещение
        self.lag_offset_spin = QSpinBox()
        self.lag_offset_spin.setMinimum(1)
        self.lag_offset_spin.setMaximum(100)
        self.lag_offset_spin.setValue(1)
        self.lag_offset_spin.valueChanged.connect(self.update_lag_preview)
        params_layout.addRow("Смещение:", self.lag_offset_spin)
        
        # Значение по умолчанию
        self.lag_default_input = QLineEdit()
        self.lag_default_input.setPlaceholderText("NULL (если не указано)")
        self.lag_default_input.textChanged.connect(self.update_lag_preview)
        params_layout.addRow("Значение по умолчанию:", self.lag_default_input)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # ORDER BY
        order_group = QGroupBox("ORDER BY (обязательно)")
        order_layout = QVBoxLayout()
        
        self.lag_order_combo = QComboBox()
        self.lag_order_combo.addItems(self.columns)
        self.lag_order_combo.currentTextChanged.connect(self.update_lag_preview)
        
        self.lag_direction_combo = QComboBox()
        self.lag_direction_combo.addItems(["ASC", "DESC"])
        self.lag_direction_combo.currentTextChanged.connect(self.update_lag_preview)
        
        order_layout.addWidget(QLabel("Столбец для сортировки:"))
        order_layout.addWidget(self.lag_order_combo)
        order_layout.addWidget(QLabel("Направление:"))
        order_layout.addWidget(self.lag_direction_combo)
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # PARTITION BY
        partition_group = QGroupBox("PARTITION BY (необязательно)")
        partition_layout = QVBoxLayout()
        
        self.lag_use_partition = QCheckBox("Использовать разбиение")
        self.lag_use_partition.stateChanged.connect(self.update_lag_preview)
        
        self.lag_partition_combo = QComboBox()
        self.lag_partition_combo.addItems(self.columns)
        self.lag_partition_combo.currentTextChanged.connect(self.update_lag_preview)
        self.lag_partition_combo.setEnabled(False)
        
        self.lag_use_partition.stateChanged.connect(
            lambda state: self.lag_partition_combo.setEnabled(state == Qt.Checked)
        )
        
        partition_layout.addWidget(self.lag_use_partition)
        partition_layout.addWidget(QLabel("Столбец для разбиения:"))
        partition_layout.addWidget(self.lag_partition_combo)
        partition_group.setLayout(partition_layout)
        layout.addWidget(partition_group)
        
        # Предпросмотр SQL
        preview_group = QGroupBox("Предпросмотр SQL")
        preview_layout = QVBoxLayout()
        self.lag_preview = QTextEdit()
        self.lag_preview.setReadOnly(True)
        self.lag_preview.setMaximumHeight(100)
        preview_layout.addWidget(self.lag_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        # Инициализация предпросмотра
        self.update_lag_preview()
        
        return widget
        
    def create_lead_tab(self):
        """Создает вкладку для функции LEAD"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Описание
        desc = QLabel("Функция LEAD() предоставляет доступ к строке с заданным физическим смещением, которая СЛЕДУЕТ ЗА текущей строкой.")
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background-color: rgba(64, 255, 218, 0.1); border-radius: 5px;")
        layout.addWidget(desc)
        
        # Параметры
        params_group = QGroupBox("Параметры функции")
        params_layout = QFormLayout()
        
        # Столбец
        self.lead_column_combo = QComboBox()
        self.lead_column_combo.addItems(self.columns)
        self.lead_column_combo.currentTextChanged.connect(self.update_lead_preview)
        params_layout.addRow("Столбец:", self.lead_column_combo)
        
        # Смещение
        self.lead_offset_spin = QSpinBox()
        self.lead_offset_spin.setMinimum(1)
        self.lead_offset_spin.setMaximum(100)
        self.lead_offset_spin.setValue(1)
        self.lead_offset_spin.valueChanged.connect(self.update_lead_preview)
        params_layout.addRow("Смещение:", self.lead_offset_spin)
        
        # Значение по умолчанию
        self.lead_default_input = QLineEdit()
        self.lead_default_input.setPlaceholderText("NULL (если не указано)")
        self.lead_default_input.textChanged.connect(self.update_lead_preview)
        params_layout.addRow("Значение по умолчанию:", self.lead_default_input)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # ORDER BY
        order_group = QGroupBox("ORDER BY (обязательно)")
        order_layout = QVBoxLayout()
        
        self.lead_order_combo = QComboBox()
        self.lead_order_combo.addItems(self.columns)
        self.lead_order_combo.currentTextChanged.connect(self.update_lead_preview)
        
        self.lead_direction_combo = QComboBox()
        self.lead_direction_combo.addItems(["ASC", "DESC"])
        self.lead_direction_combo.currentTextChanged.connect(self.update_lead_preview)
        
        order_layout.addWidget(QLabel("Столбец для сортировки:"))
        order_layout.addWidget(self.lead_order_combo)
        order_layout.addWidget(QLabel("Направление:"))
        order_layout.addWidget(self.lead_direction_combo)
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # PARTITION BY
        partition_group = QGroupBox("PARTITION BY (необязательно)")
        partition_layout = QVBoxLayout()
        
        self.lead_use_partition = QCheckBox("Использовать разбиение")
        self.lead_use_partition.stateChanged.connect(self.update_lead_preview)
        
        self.lead_partition_combo = QComboBox()
        self.lead_partition_combo.addItems(self.columns)
        self.lead_partition_combo.currentTextChanged.connect(self.update_lead_preview)
        self.lead_partition_combo.setEnabled(False)
        
        self.lead_use_partition.stateChanged.connect(
            lambda state: self.lead_partition_combo.setEnabled(state == Qt.Checked)
        )
        
        partition_layout.addWidget(self.lead_use_partition)
        partition_layout.addWidget(QLabel("Столбец для разбиения:"))
        partition_layout.addWidget(self.lead_partition_combo)
        partition_group.setLayout(partition_layout)
        layout.addWidget(partition_group)
        
        # Предпросмотр SQL
        preview_group = QGroupBox("Предпросмотр SQL")
        preview_layout = QVBoxLayout()
        self.lead_preview = QTextEdit()
        self.lead_preview.setReadOnly(True)
        self.lead_preview.setMaximumHeight(100)
        preview_layout.addWidget(self.lead_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        # Инициализация предпросмотра
        self.update_lead_preview()
        
        return widget
        
    def create_results_panel(self):
        """Создает панель результатов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        results_label = QLabel("Результаты выполнения:")
        results_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.results_table)
        
        self.results_info = QLabel("Выполните запрос для отображения результатов")
        self.results_info.setAlignment(Qt.AlignCenter)
        self.results_info.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.results_info)
        
        return widget
        
    def update_rank_preview(self):
        """Обновляет предпросмотр SQL для RANK"""
        sql = self.build_rank_sql()
        self.rank_preview.setPlainText(sql)
        
    def update_lag_preview(self):
        """Обновляет предпросмотр SQL для LAG"""
        sql = self.build_lag_sql()
        self.lag_preview.setPlainText(sql)
        
    def update_lead_preview(self):
        """Обновляет предпросмотр SQL для LEAD"""
        sql = self.build_lead_sql()
        self.lead_preview.setPlainText(sql)
        
    def build_rank_sql(self):
        """Строит SQL запрос для RANK"""
        order_col = self.rank_order_combo.currentText()
        direction = self.rank_direction_combo.currentText()
        
        partition_clause = ""
        if self.rank_use_partition.isChecked():
            partition_col = self.rank_partition_combo.currentText()
            partition_clause = f" PARTITION BY {partition_col}"
            
        sql = f"""SELECT *,
       RANK() OVER ({partition_clause} ORDER BY {order_col} {direction}) AS rank
FROM {self.table_name}"""
        
        return sql
        
    def build_lag_sql(self):
        """Строит SQL запрос для LAG"""
        column = self.lag_column_combo.currentText()
        offset = self.lag_offset_spin.value()
        default = self.lag_default_input.text().strip()
        order_col = self.lag_order_combo.currentText()
        direction = self.lag_direction_combo.currentText()
        
        default_value = f", '{default}'" if default else ""
        
        partition_clause = ""
        if self.lag_use_partition.isChecked():
            partition_col = self.lag_partition_combo.currentText()
            partition_clause = f" PARTITION BY {partition_col}"
            
        sql = f"""SELECT *,
       LAG({column}, {offset}{default_value}) OVER ({partition_clause} ORDER BY {order_col} {direction}) AS lag_value
FROM {self.table_name}"""
        
        return sql
        
    def build_lead_sql(self):
        """Строит SQL запрос для LEAD"""
        column = self.lead_column_combo.currentText()
        offset = self.lead_offset_spin.value()
        default = self.lead_default_input.text().strip()
        order_col = self.lead_order_combo.currentText()
        direction = self.lead_direction_combo.currentText()
        
        default_value = f", '{default}'" if default else ""
        
        partition_clause = ""
        if self.lead_use_partition.isChecked():
            partition_col = self.lead_partition_combo.currentText()
            partition_clause = f" PARTITION BY {partition_col}"
            
        sql = f"""SELECT *,
       LEAD({column}, {offset}{default_value}) OVER ({partition_clause} ORDER BY {order_col} {direction}) AS lead_value
FROM {self.table_name}"""
        
        return sql
        
    def get_window_function_sql(self):
        """Возвращает SQL для текущей выбранной функции"""
        current_tab_index = self.findChild(QTabWidget).currentIndex()
        
        if current_tab_index == 0:  # RANK
            return self.build_rank_sql()
        elif current_tab_index == 1:  # LAG
            return self.build_lag_sql()
        elif current_tab_index == 2:  # LEAD
            return self.build_lead_sql()
            
        return ""
        
    def execute_window_function(self):
        """Выполняет оконную функцию и отображает результаты"""
        sql = self.get_window_function_sql()
        
        if not sql:
            QMessageBox.warning(self, "Ошибка", "Не удалось сформировать SQL запрос")
            return
            
        try:
            cursor = self.db_instance.connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            self.display_results(results, columns)
            
            self.results_info.setText(f"Найдено записей: {len(results)}")
            self.results_info.setStyleSheet("color: #64ffda; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка выполнения", f"Ошибка при выполнении запроса:\n{str(e)}")
            self.results_info.setText(f"Ошибка: {str(e)}")
            self.results_info.setStyleSheet("color: #ff5555;")
            
    def display_results(self, results, columns):
        """Отображает результаты в таблице"""
        self.results_table.clear()
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, row_data in enumerate(results):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value is not None else "NULL")
                item.setTextAlignment(Qt.AlignCenter)
                self.results_table.setItem(row_idx, col_idx, item)
                
        self.results_table.resizeColumnsToContents()
        self.results_table.setSortingEnabled(True)
        
    def copy_sql_to_clipboard(self):
        """Копирует SQL запрос в буфер обмена"""
        from PySide6.QtWidgets import QApplication
        
        sql = self.get_window_function_sql()
        if sql:
            clipboard = QApplication.clipboard()
            clipboard.setText(sql)
            QMessageBox.information(self, "Успех", "SQL запрос скопирован в буфер обмена")
