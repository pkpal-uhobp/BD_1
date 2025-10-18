from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea, QSpinBox, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification
import re


class StringFunctionsDialog(QDialog):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("🔤 Строковые функции")
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        self.setMaximumSize(1400, 1000)
        self.resize(1200, 800)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Переменные для хранения результатов
        self.current_results = []
        self.current_function_name = ""
        self.current_table_name = ""
        self.current_column_name = ""
        self.current_function_params = ""
        
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
        header_label = QLabel("🔤 СТРОКОВЫЕ ФУНКЦИИ БАЗЫ ДАННЫХ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(header_label)
        
        # Создаем сплиттер для разделения на панели
        splitter = QSplitter(Qt.Horizontal)
        self.layout().addWidget(splitter)
        
        # Левая панель - настройки
        left_panel = self.create_settings_panel()
        splitter.addWidget(left_panel)
        
        # Правая панель - результаты
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции сплиттера
        splitter.setSizes([400, 600])
        
        # Кнопки управления
        self.create_control_buttons()
        
    def create_settings_panel(self):
        """Создает панель настроек"""
        panel = QWidget()
        panel.setObjectName("settingsPanel")
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок панели
        panel_header = QLabel("⚙️ НАСТРОЙКИ ФУНКЦИЙ")
        panel_header.setObjectName("panelHeader")
        panel_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(panel_header)
        
        # Группа выбора таблицы и столбца
        table_group = QGroupBox("📋 Выбор данных")
        table_group.setObjectName("groupBox")
        table_layout = QFormLayout()
        table_group.setLayout(table_layout)
        
        # Выбор таблицы
        self.table_combo = QComboBox()
        self.table_combo.setObjectName("comboBox")
        self.table_combo.setMinimumHeight(35)
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        # Принудительно устанавливаем темную палитру
        self.table_combo.setStyleSheet("""
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2 !important;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                border: 1px solid #44475a !important;
            }
            QComboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
            QComboBox * {
                color: #f8f8f2 !important;
                background: rgba(15, 15, 25, 0.95) !important;
            }
        """)
        table_layout.addRow("Таблица:", self.table_combo)
        
        # Выбор столбца
        self.column_combo = QComboBox()
        self.column_combo.setObjectName("comboBox")
        self.column_combo.setMinimumHeight(35)
        # Принудительно устанавливаем темную палитру
        self.column_combo.setStyleSheet("""
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                border: 1px solid #44475a !important;
            }
            QComboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
        """)
        table_layout.addRow("Столбец:", self.column_combo)
        
        layout.addWidget(table_group)
        
        # Группа выбора функции
        function_group = QGroupBox("🔧 Строковые функции")
        function_group.setObjectName("groupBox")
        function_layout = QVBoxLayout()
        function_group.setLayout(function_layout)
        
        # Выбор функции
        self.function_combo = QComboBox()
        self.function_combo.setObjectName("comboBox")
        self.function_combo.setMinimumHeight(35)
        self.function_combo.addItems([
            "UPPER - Преобразование в верхний регистр",
            "LOWER - Преобразование в нижний регистр", 
            "SUBSTRING - Извлечение подстроки",
            "TRIM - Удаление пробелов",
            "LPAD - Дополнение слева",
            "RPAD - Дополнение справа",
            "CONCAT - Объединение строк"
        ])
        self.function_combo.currentTextChanged.connect(self.on_function_changed)
        # Принудительно устанавливаем темную палитру
        self.function_combo.setStyleSheet("""
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                border: 1px solid #44475a !important;
            }
            QComboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
        """)
        function_layout.addWidget(QLabel("Функция:"))
        function_layout.addWidget(self.function_combo)
        
        # Параметры функции
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        function_layout.addWidget(self.params_widget)
        
        layout.addWidget(function_group)
        
        # Группа предварительного просмотра
        preview_group = QGroupBox("👁️ Предварительный просмотр")
        preview_group.setObjectName("groupBox")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)
        
        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("textEdit")
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("SQL-запрос будет отображен здесь...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Заполняем таблицы
        self.load_tables()
        
        return panel
        
    def create_results_panel(self):
        """Создает панель результатов"""
        panel = QWidget()
        panel.setObjectName("resultsPanel")
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок панели
        panel_header = QLabel("📊 РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ")
        panel_header.setObjectName("panelHeader")
        panel_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(panel_header)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setObjectName("resultsTable")
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setWordWrap(True)
        layout.addWidget(self.results_table)
        
        # Информация о результатах
        self.results_info = QLabel("Выберите функцию и нажмите 'Выполнить' для просмотра результатов")
        self.results_info.setObjectName("infoLabel")
        self.results_info.setAlignment(Qt.AlignCenter)
        self.results_info.setWordWrap(True)
        layout.addWidget(self.results_info)
        
        return panel
        
    def create_control_buttons(self):
        """Создает кнопки управления"""
        button_layout = QHBoxLayout()
        
        # Кнопка выполнения
        self.execute_button = QPushButton("🚀 Выполнить")
        self.execute_button.setObjectName("executeButton")
        self.execute_button.setMinimumHeight(45)
        self.execute_button.clicked.connect(self.execute_function)
        button_layout.addWidget(self.execute_button)
        
        # Кнопка применения изменений
        self.apply_button = QPushButton("✅ Применить изменения")
        self.apply_button.setObjectName("applyButton")
        self.apply_button.setMinimumHeight(45)
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setEnabled(False)  # Включается только при наличии результатов
        button_layout.addWidget(self.apply_button)
        
        
        # Кнопка очистки
        self.clear_button = QPushButton("🗑️ Очистить")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setMinimumHeight(45)
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)
        
        # Кнопка закрытия
        self.close_button = QPushButton("❌ Закрыть")
        self.close_button.setObjectName("closeButton")
        self.close_button.setMinimumHeight(45)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        self.layout().addLayout(button_layout)
        
    def load_tables(self):
        """Загружает список таблиц"""
        if not self.db_instance or not self.db_instance.is_connected():
            return
            
        try:
            # Получаем список таблиц
            tables = self.db_instance.get_tables()
            self.table_combo.clear()
            self.table_combo.addItems(tables)
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Не удалось загрузить список таблиц: {str(e)}",
                timeout=3
            )
            
    def on_table_changed(self, table_name):
        """Обработчик изменения таблицы"""
        if not table_name or not self.db_instance:
            return
            
        try:
            # Получаем столбцы выбранной таблицы
            columns = self.db_instance.get_table_columns(table_name)
            self.column_combo.clear()
            
            # Добавляем все столбцы (пользователь сам выберет подходящий)
            self.column_combo.addItems(columns)
            
            # Обновляем предварительный просмотр
            self.update_preview()
            
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Не удалось загрузить столбцы таблицы: {str(e)}",
                timeout=3
            )
            
    def on_function_changed(self, function_text):
        """Обработчик изменения функции"""
        # Очищаем параметры
        self.clear_params()
        
        # Создаем параметры для выбранной функции
        function_name = function_text.split(' - ')[0]
        
        if function_name == "SUBSTRING":
            self.create_substring_params()
        elif function_name == "TRIM":
            self.create_trim_params()
        elif function_name in ["LPAD", "RPAD"]:
            self.create_pad_params()
        elif function_name == "CONCAT":
            self.create_concat_params()
            
        # Обновляем предварительный просмотр
        self.update_preview()
        
    def clear_params(self):
        """Очищает параметры функции"""
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def create_substring_params(self):
        """Создает параметры для SUBSTRING"""
        # Начальная позиция
        start_label = QLabel("Начальная позиция:")
        start_label.setObjectName("paramLabel")
        self.start_spin = QSpinBox()
        self.start_spin.setObjectName("spinBox")
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(1000)
        self.start_spin.setValue(1)
        self.start_spin.valueChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(start_label)
        self.params_layout.addWidget(self.start_spin)
        
        # Длина подстроки
        length_label = QLabel("Длина (необязательно):")
        length_label.setObjectName("paramLabel")
        self.length_spin = QSpinBox()
        self.length_spin.setObjectName("spinBox")
        self.length_spin.setMinimum(0)
        self.length_spin.setMaximum(1000)
        self.length_spin.setValue(10)
        self.length_spin.setSpecialValueText("Не ограничено")
        self.length_spin.valueChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(length_label)
        self.params_layout.addWidget(self.length_spin)
        
    def create_trim_params(self):
        """Создает параметры для TRIM"""
        # Тип TRIM
        trim_type_label = QLabel("Тип TRIM:")
        trim_type_label.setObjectName("paramLabel")
        self.trim_type_combo = QComboBox()
        self.trim_type_combo.setObjectName("comboBox")
        self.trim_type_combo.addItems(["BOTH", "LEADING", "TRAILING"])
        self.trim_type_combo.currentTextChanged.connect(self.update_preview)
        # Принудительно устанавливаем темную палитру
        self.trim_type_combo.setStyleSheet("""
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                border: 1px solid #44475a !important;
            }
            QComboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
        """)
        
        self.params_layout.addWidget(trim_type_label)
        self.params_layout.addWidget(self.trim_type_combo)
        
        # Символы для удаления
        chars_label = QLabel("Символы для удаления (необязательно):")
        chars_label.setObjectName("paramLabel")
        self.trim_chars_input = QLineEdit()
        self.trim_chars_input.setObjectName("lineEdit")
        self.trim_chars_input.setPlaceholderText("По умолчанию: пробелы")
        self.trim_chars_input.textChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(chars_label)
        self.params_layout.addWidget(self.trim_chars_input)
        
    def create_pad_params(self):
        """Создает параметры для LPAD/RPAD"""
        # Длина
        length_label = QLabel("Целевая длина:")
        length_label.setObjectName("paramLabel")
        self.pad_length_spin = QSpinBox()
        self.pad_length_spin.setObjectName("spinBox")
        self.pad_length_spin.setMinimum(1)
        self.pad_length_spin.setMaximum(1000)
        self.pad_length_spin.setValue(20)
        self.pad_length_spin.valueChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(length_label)
        self.params_layout.addWidget(self.pad_length_spin)
        
        # Символ дополнения
        pad_char_label = QLabel("Символ дополнения:")
        pad_char_label.setObjectName("paramLabel")
        self.pad_char_input = QLineEdit()
        self.pad_char_input.setObjectName("lineEdit")
        self.pad_char_input.setText(" ")
        self.pad_char_input.setMaxLength(1)
        self.pad_char_input.textChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(pad_char_label)
        self.params_layout.addWidget(self.pad_char_input)
        
    def create_concat_params(self):
        """Создает параметры для CONCAT"""
        # Строка для объединения
        concat_label = QLabel("Строка для объединения:")
        concat_label.setObjectName("paramLabel")
        self.concat_input = QLineEdit()
        self.concat_input.setObjectName("lineEdit")
        self.concat_input.setPlaceholderText("Введите строку для объединения...")
        self.concat_input.textChanged.connect(self.update_preview)
        
        self.params_layout.addWidget(concat_label)
        self.params_layout.addWidget(self.concat_input)
        
    def update_preview(self):
        """Обновляет предварительный просмотр SQL-запроса"""
        table_name = self.table_combo.currentText()
        column_name = self.column_combo.currentText()
        function_text = self.function_combo.currentText()
        
        if not table_name or not column_name or not function_text:
            self.preview_text.clear()
            return
            
        function_name = function_text.split(' - ')[0]
        sql_query = self.generate_sql_preview(table_name, column_name, function_name)
        self.preview_text.setPlainText(sql_query)
        
    def generate_sql_preview(self, table_name, column_name, function_name):
        """Генерирует предварительный просмотр SQL-запроса"""
        if not table_name or not column_name:
            return ""
            
        col = f"{table_name}.{column_name}"
        
        if function_name == "UPPER":
            return f"SELECT {col}, UPPER({col}) AS upper_result FROM {table_name};"
        elif function_name == "LOWER":
            return f"SELECT {col}, LOWER({col}) AS lower_result FROM {table_name};"
        elif function_name == "SUBSTRING":
            start = getattr(self, 'start_spin', None)
            length = getattr(self, 'length_spin', None)
            if start and length:
                if length.value() == 0:
                    return f"SELECT {col}, SUBSTRING({col} FROM {start.value()}) AS substring_result FROM {table_name};"
                else:
                    return f"SELECT {col}, SUBSTRING({col} FROM {start.value()} FOR {length.value()}) AS substring_result FROM {table_name};"
        elif function_name == "TRIM":
            trim_type = getattr(self, 'trim_type_combo', None)
            chars = getattr(self, 'trim_chars_input', None)
            if trim_type and chars:
                if chars.text().strip():
                    return f"SELECT {col}, TRIM({trim_type.currentText()} '{chars.text()}' FROM {col}) AS trim_result FROM {table_name};"
                else:
                    return f"SELECT {col}, TRIM({trim_type.currentText()} FROM {col}) AS trim_result FROM {table_name};"
        elif function_name in ["LPAD", "RPAD"]:
            length = getattr(self, 'pad_length_spin', None)
            char = getattr(self, 'pad_char_input', None)
            if length and char:
                return f"SELECT {col}, {function_name}({col}, {length.value()}, '{char.text()}') AS {function_name.lower()}_result FROM {table_name};"
        elif function_name == "CONCAT":
            concat_str = getattr(self, 'concat_input', None)
            if concat_str:
                return f"SELECT {col}, CONCAT({col}, '{concat_str.text()}') AS concat_result FROM {table_name};"
                
        return f"SELECT {col}, {function_name}({col}) AS {function_name.lower()}_result FROM {table_name};"
        
    def execute_function(self):
        """Выполняет выбранную строковую функцию"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="❌ Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
            
        table_name = self.table_combo.currentText()
        column_name = self.column_combo.currentText()
        function_text = self.function_combo.currentText()
        
        if not table_name or not column_name or not function_text:
            notification.notify(
                title="❌ Ошибка",
                message="Выберите таблицу, столбец и функцию!",
                timeout=3
            )
            return
            
        try:
            function_name = function_text.split(' - ')[0]
            results = []
            function_params = ""
            
            if function_name == "UPPER":
                results = self.db_instance.string_functions_demo(table_name, column_name, "UPPER")
            elif function_name == "LOWER":
                results = self.db_instance.string_functions_demo(table_name, column_name, "LOWER")
            elif function_name == "SUBSTRING":
                start = getattr(self, 'start_spin', None)
                length = getattr(self, 'length_spin', None)
                if start and length:
                    length_val = length.value() if length.value() > 0 else None
                    results = self.db_instance.substring_function(table_name, column_name, start.value(), length_val)
                    function_params = f"start={start.value()}, length={length_val}"
            elif function_name == "TRIM":
                trim_type = getattr(self, 'trim_type_combo', None)
                chars = getattr(self, 'trim_chars_input', None)
                if trim_type and chars:
                    chars_val = chars.text().strip() if chars.text().strip() else None
                    results = self.db_instance.trim_functions(table_name, column_name, trim_type.currentText(), chars_val)
                    function_params = f"trim_type={trim_type.currentText()}, chars={chars_val}"
            elif function_name in ["LPAD", "RPAD"]:
                length = getattr(self, 'pad_length_spin', None)
                char = getattr(self, 'pad_char_input', None)
                if length and char:
                    pad_type = "LPAD" if function_name == "LPAD" else "RPAD"
                    results = self.db_instance.pad_functions(table_name, column_name, length.value(), char.text(), pad_type)
                    function_params = f"length={length.value()}, char='{char.text()}', pad_type={pad_type}"
            elif function_name == "CONCAT":
                concat_str = getattr(self, 'concat_input', None)
                if concat_str:
                    results = self.db_instance.string_functions_demo(table_name, column_name, "CONCAT", concat_string=concat_str.text())
                    function_params = f"concat_string='{concat_str.text()}'"
                    
            # Сохраняем текущие результаты для возможного сохранения
            self.current_results = results
            self.current_function_name = function_name
            self.current_table_name = table_name
            self.current_column_name = column_name
            self.current_function_params = function_params
                    
            if results:
                self.display_results(results)
                self.apply_button.setEnabled(True)   # Включаем кнопку применения
                notification.notify(
                    title="✅ Успех",
                    message=f"Функция {function_name} выполнена успешно. Найдено {len(results)} записей.",
                    timeout=3
                )
            else:
                self.results_table.clear()
                self.results_table.setRowCount(0)
                self.results_table.setColumnCount(1)
                self.results_table.setHorizontalHeaderLabels(["Нет данных"])
                self.results_info.setText("Результаты не найдены")
                self.apply_button.setEnabled(False)  # Отключаем кнопку
                
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка выполнения функции: {str(e)}",
                timeout=5
            )
            self.results_info.setText(f"Ошибка: {str(e)}")
            
    def display_results(self, results):
        """Отображает результаты в таблице"""
        if not results:
            return
            
        # Получаем ключи из первого результата
        sample_result = results[0]
        columns = list(sample_result.keys())
        
        # Настраиваем таблицу
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Заполняем данными
        for row_idx, result in enumerate(results):
            for col_idx, column in enumerate(columns):
                value = result.get(column, "")
                if value is None:
                    value = ""
                elif isinstance(value, (list, tuple)):
                    value = ", ".join(map(str, value))
                else:
                    value = str(value)
                    
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_idx, col_idx, item)
                
        # Настраиваем размеры столбцов
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        # Обновляем информацию
        self.results_info.setText(f"Найдено {len(results)} записей")
        

    def apply_changes(self):
        """Применяет изменения к исходной таблице"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="❌ Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
            
        # Показываем диалог подтверждения
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "⚠️ Подтверждение изменений",
            f"Вы уверены, что хотите применить функцию {self.current_function_name} "
            f"к столбцу {self.current_column_name} в таблице {self.current_table_name}?\n\n"
            f"Это изменит данные в исходной таблице!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Получаем параметры функции
            params = self._get_function_params()
            
            # Применяем изменения
            success = self.db_instance.update_string_values_in_table(
                table_name=self.current_table_name,
                column_name=self.current_column_name,
                function_name=self.current_function_name,
                **params
            )
            
            if success:
                notification.notify(
                    title="✅ Успех",
                    message=f"Функция {self.current_function_name} успешно применена к таблице {self.current_table_name}!",
                    timeout=3
                )
                # Обновляем отображение результатов
                self.execute_function()
            else:
                notification.notify(
                    title="❌ Ошибка",
                    message="Не удалось применить изменения к таблице!",
                    timeout=3
                )
                
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка применения изменений: {str(e)}",
                timeout=5
            )

    def clear_results(self):
        """Очищает результаты"""
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.results_info.setText("Результаты очищены")
        self.current_results = []
        self.apply_button.setEnabled(False)

    def _get_function_params(self):
        """Получает параметры функции из UI"""
        params = {}
        
        if self.current_function_name == "SUBSTRING":
            start = getattr(self, 'start_spin', None)
            length = getattr(self, 'length_spin', None)
            if start and length:
                params['start'] = start.value()
                params['length'] = length.value() if length.value() > 0 else None
        elif self.current_function_name == "TRIM":
            trim_type = getattr(self, 'trim_type_combo', None)
            chars = getattr(self, 'trim_chars_input', None)
            if trim_type and chars:
                params['trim_type'] = trim_type.currentText()
                params['chars'] = chars.text().strip() if chars.text().strip() else None
        elif self.current_function_name in ["LPAD", "RPAD"]:
            length = getattr(self, 'pad_length_spin', None)
            char = getattr(self, 'pad_char_input', None)
            if length and char:
                params['length'] = length.value()
                params['pad_string'] = char.text()
        elif self.current_function_name == "CONCAT":
            concat_str = getattr(self, 'concat_input', None)
            if concat_str:
                params['concat_string'] = concat_str.text()
        
        return params



    def apply_styles(self):
        """Применяет стили к диалогу"""
        self.setStyleSheet("""
            /* Основной диалог */
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
            }
            
            /* Заголовки */
            #headerLabel, #panelHeader {
                font-size: 18px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
                border: 1px solid #64ffda;
            }
            
            /* Панели */
            #settingsPanel, #resultsPanel {
                background: rgba(15, 15, 25, 0.6);
                border: 1px solid #44475a;
                border-radius: 10px;
                padding: 15px;
            }
            
            /* Группы */
            #groupBox {
                background: rgba(20, 20, 30, 0.8);
                border: 1px solid #44475a;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                font-weight: bold;
                color: #f8f8f2;
            }
            
            #groupBox::title {
                color: #64ffda;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            
            /* Комбобоксы */
            #comboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #comboBox:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }
            
            #comboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            /* Стилизация выпадающего списка комбобокса */
            #comboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                border: 1px solid #44475a !important;
                border-radius: 6px !important;
                color: #f8f8f2 !important;
                selection-background-color: #64ffda !important;
                selection-color: #0a0a0f !important;
            }
            
            #comboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
                border: none !important;
            }
            
            #comboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            
            #comboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
            
            /* Дополнительные стили для принудительного применения темной темы */
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                border: 1px solid #44475a !important;
            }
            
            QComboBox QAbstractItemView::item {
                background: rgba(15, 15, 25, 0.95) !important;
                color: #f8f8f2 !important;
                padding: 8px 12px !important;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background: rgba(30, 30, 40, 0.9) !important;
                color: #64ffda !important;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background: #64ffda !important;
                color: #0a0a0f !important;
            }
            
            /* Принудительные стили для всех элементов комбобокса */
            QComboBox * {
                color: #f8f8f2 !important;
                background: rgba(15, 15, 25, 0.95) !important;
            }
            
            QComboBox QAbstractItemView * {
                color: #f8f8f2 !important;
                background: rgba(15, 15, 25, 0.95) !important;
            }
            
            /* Стили для текста в комбобоксе */
            QComboBox::drop-down {
                background: rgba(15, 15, 25, 0.8);
                border: none;
            }
            
            QComboBox::down-arrow {
                background: rgba(15, 15, 25, 0.8);
                border: none;
            }
            
            /* Поля ввода */
            #lineEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #lineEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }
            
            #lineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            /* Спинбоксы */
            #spinBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #spinBox:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }
            
            #spinBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            /* Текстовое поле */
            #textEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #textEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            /* Таблица результатов */
            #resultsTable {
                background: rgba(25, 25, 35, 0.8);
                border: 1px solid #44475a;
                border-radius: 8px;
                gridline-color: #44475a;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 12px;
            }
            
            #resultsTable::item {
                padding: 8px;
                border-bottom: 1px solid #44475a40;
                color: #f8f8f2;
            }
            
            #resultsTable::item:selected {
                background-color: #64ffda40;
                color: #0a0a0f;
            }
            
            #resultsTable::item:alternate {
                background-color: rgba(40, 40, 50, 0.4);
            }
            
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                color: #f8f8f2;
                padding: 8px;
                border: 1px solid #6272a4;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 11px;
            }
            
            QHeaderView::section:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #64ffda, 
                                          stop: 1 #50e3c2);
                color: #0a0a0f;
            }
            
            /* Кнопки */
            #executeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 8px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #executeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }
            
            #executeButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
            }
            
            #clearButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ee5a52);
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #clearButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #e53935);
                border: 2px solid #ff6b6b;
            }
            
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: none;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #closeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #7c7c9c, 
                                          stop: 1 #5a5a7a);
                border: 2px solid #6272a4;
            }
            
            #saveButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4caf50, 
                                          stop: 1 #45a049);
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #saveButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #45a049, 
                                          stop: 1 #3d8b40);
                border: 2px solid #4caf50;
            }
            
            #saveButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3d8b40, 
                                          stop: 1 #2e7d32);
            }
            
            
            #applyButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4caf50, 
                                          stop: 1 #45a049);
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            #applyButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #45a049, 
                                          stop: 1 #3d8b40);
                border: 2px solid #4caf50;
            }
            
            #applyButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3d8b40, 
                                          stop: 1 #2e7d32);
            }
            
            #applyButton:disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #666666, 
                                          stop: 1 #555555);
                color: #999999;
                border: none;
            }
            
            
            /* Метки параметров */
            #paramLabel {
                color: #f8f8f2 !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px 0;
            }
            
            /* Все метки должны быть белыми */
            QLabel {
                color: #f8f8f2 !important;
                background: transparent !important;
            }
            
            /* Специальные стили для меток в группах */
            QGroupBox QLabel {
                color: #f8f8f2 !important;
                background: transparent !important;
            }
            
            /* Информационная метка */
            #infoLabel {
                color: #8892b0;
                font-size: 12px;
                font-style: italic;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
                background: rgba(15, 15, 25, 0.6);
                border-radius: 6px;
                border: 1px solid #44475a;
            }
            
            /* Сплиттер */
            QSplitter::handle {
                background: #44475a;
                width: 3px;
                height: 3px;
            }
            
            QSplitter::handle:hover {
                background: #64ffda;
            }
        """)
