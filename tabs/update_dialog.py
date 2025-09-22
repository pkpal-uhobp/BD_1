from decimal import Decimal, InvalidOperation
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit, QTextEdit)
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String, Text
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor, QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt
import re
from datetime import datetime


class EditRecordDialog(QDialog):
    """Модальное окно для редактирования записей в выбранной таблице."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        self.setWindowTitle("Редактирование данных")
        self.setModal(True)
        self.resize(750, 850)  # Увеличим размер для отображения ошибок

        # Устанавливаем тёмную палитру
        self.set_dark_palette()

        # Словари для хранения виджетов и меток ошибок
        self.search_widgets = {}
        self.update_widgets = {}
        self.search_error_labels = {}  # Метки ошибок для поиска
        self.update_error_labels = {}  # Метки ошибок для обновления

        # ID найденной записи
        self.found_record_id = None

        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.init_ui()
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

    def apply_styles(self):
        """Применяет CSS стили"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
                border-radius: 12px;
            }

            QLabel {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px 0;
            }

            .field-label {
                color: #64ffda;
            }

            .error-label {
                color: #ff5555;
                font-size: 11px;
                font-weight: normal;
                font-style: italic;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                padding: 3px 8px;
                margin: 2px 0px;
                border-left: 3px solid #ff5555;
            }

            .success-label {
                color: #50fa7b;
                font-size: 11px;
                font-weight: normal;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                padding: 3px 8px;
                margin: 2px 0px;
                border-left: 3px solid #50fa7b;
            }

            QComboBox {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 20px;
            }

            QComboBox:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QComboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64ffda;
                width: 0px;
                height: 0px;
            }

            QComboBox QAbstractItemView {
                background: rgba(25, 25, 35, 0.95);
                border: 2px solid #64ffda;
                border-radius: 8px;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                outline: none;
            }

            QLineEdit, QDateEdit, QTextEdit {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }

            QTextEdit {
                min-height: 80px;
            }

            QLineEdit:hover, QDateEdit:hover, QTextEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit::placeholder, QDateEdit::placeholder, QTextEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }

            .error-widget {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }

            .success-widget {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }

            QCheckBox {
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
                spacing: 8px;
                font-size: 14px;
            }

            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #44475a;
                border-radius: 4px;
                background: rgba(25, 25, 35, 0.8);
            }

            QCheckBox::indicator:hover {
                border: 2px solid #6272a4;
            }

            QCheckBox::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
            }

            QCheckBox::indicator:checked:hover {
                background: #50e3c2;
                border: 2px solid #50e3c2;
            }

            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 10px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-height: 40px;
            }

            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
            }

            QPushButton:disabled {
                background: #44475a;
                color: #6272a4;
                border: 1px solid #6272a4;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #64ffda;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #50e3c2;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            #tableContainer, #searchContainer, #updateContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }

            #fieldRow {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("✏️ РЕДАКТИРОВАНИЕ ДАННЫХ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title_label)

        # Контейнер для выбора таблицы
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_layout = QVBoxLayout(table_container)

        table_label = QLabel("📊 Выберите таблицу:")
        table_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.table_combo = QComboBox()
        self.table_combo.setMinimumHeight(35)

        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц.",
                timeout=3
            )
            self.reject()
            return

        self.table_combo.addItems(table_names)
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_combo)
        layout.addWidget(table_container)

        # Область условий поиска
        search_label = QLabel("🔍 Условия поиска записи:")
        search_label.setFont(QFont("Consolas", 12, QFont.Bold))
        layout.addWidget(search_label)

        self.search_container = QWidget()
        self.search_container.setObjectName("searchContainer")
        self.search_layout = QVBoxLayout(self.search_container)

        scroll_area_search = QScrollArea()
        scroll_area_search.setWidgetResizable(True)
        scroll_area_search.setWidget(self.search_container)
        scroll_area_search.setMaximumHeight(250)  # Увеличим для ошибок
        layout.addWidget(scroll_area_search)

        # Область новых значений
        update_label = QLabel("🔄 Новые значения:")
        update_label.setFont(QFont("Consolas", 12, QFont.Bold))
        layout.addWidget(update_label)

        self.update_container = QWidget()
        self.update_container.setObjectName("updateContainer")
        self.update_layout = QVBoxLayout(self.update_container)

        scroll_area_update = QScrollArea()
        scroll_area_update.setWidgetResizable(True)
        scroll_area_update.setWidget(self.update_container)
        scroll_area_update.setMinimumHeight(350)  # Увеличим для ошибок
        layout.addWidget(scroll_area_update)

        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_search = QPushButton("🔎 НАЙТИ ЗАПИСЬ")
        self.btn_update = QPushButton("💾 СОХРАНИТЬ ИЗМЕНЕНИЯ")
        self.btn_update.setEnabled(False)
        self.btn_clear = QPushButton("🗑️ ОЧИСТИТЬ ПОЛЯ")

        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setCursor(Qt.PointingHandCursor)

        buttons_layout.addWidget(self.btn_search)
        buttons_layout.addWidget(self.btn_update)
        buttons_layout.addWidget(self.btn_clear)

        layout.addLayout(buttons_layout)

        # Подключаем обработчики
        self.btn_search.clicked.connect(self.on_search_clicked)
        self.btn_update.clicked.connect(self.on_update_clicked)
        self.btn_clear.clicked.connect(self.on_clear_clicked)

    def create_field_row(self, label_text, widget, required=False, is_search=True):
        """Создает строку с меткой, виджетом ввода и меткой ошибки."""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)
        row_layout.setSpacing(5)

        # Верхняя строка: метка и виджет
        input_row = QWidget()
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)

        label_text_with_req = f"{label_text}{' *' if required else ''}"
        label = QLabel(label_text_with_req)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setProperty("class", "field-label")
        label.setStyleSheet("color: #64ffda;")

        input_layout.addWidget(label)
        input_layout.addWidget(widget, 1)

        # Метка для отображения ошибки (изначально скрыта)
        error_label = QLabel()
        error_label.setProperty("class", "error-label")
        error_label.setWordWrap(True)
        error_label.setVisible(False)
        error_label.setMaximumHeight(40)  # Ограничиваем высоту

        row_layout.addWidget(input_row)
        row_layout.addWidget(error_label)

        # Сохраняем ссылку на метку ошибки
        if is_search:
            self.search_error_labels[label_text] = error_label
        else:
            self.update_error_labels[label_text] = error_label

        return row_widget

    def show_field_error(self, field_name, message, is_search=True):
        """Показывает сообщение об ошибке под указанным полем."""
        error_labels = self.search_error_labels if is_search else self.update_error_labels

        if field_name in error_labels:
            error_label = error_labels[field_name]
            if message:
                error_label.setText(message)
                error_label.setVisible(True)
                error_label.setProperty("class", "error-label")
                error_label.setStyleSheet(self.styleSheet())
            else:
                error_label.setVisible(False)

    def show_field_success(self, field_name, message, is_search=True):
        """Показывает сообщение об успехе под указанным полем."""
        error_labels = self.search_error_labels if is_search else self.update_error_labels

        if field_name in error_labels:
            error_label = error_labels[field_name]
            if message:
                error_label.setText(message)
                error_label.setVisible(True)
                error_label.setProperty("class", "success-label")
                error_label.setStyleSheet(self.styleSheet())
            else:
                error_label.setVisible(False)

    def clear_fields(self):
        """Полностью очищает все поля ввода и ошибки."""
        # Очистка условий поиска
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.search_widgets.clear()
        self.search_error_labels.clear()

        # Очистка полей для новых значений
        while self.update_layout.count():
            item = self.update_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.update_widgets.clear()
        self.update_error_labels.clear()

    def on_clear_clicked(self):
        """Очищает все поля ввода и сообщения об ошибках."""
        for widget in self.search_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate(2000, 1, 1))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QTextEdit):
                widget.clear()

        for widget in self.update_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QTextEdit):
                widget.clear()

        # Очищаем все сообщения об ошибках
        for field_name in list(self.search_error_labels.keys()):
            self.show_field_error(field_name, "", True)

        for field_name in list(self.update_error_labels.keys()):
            self.show_field_error(field_name, "", False)

        self.btn_update.setEnabled(False)
        notification.notify(
            title="Очистка",
            message="Все поля очищены.",
            timeout=2
        )

    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля для условий поиска и новых значений."""
        self.clear_fields()

        if table_name not in self.db_instance.tables:
            notification.notify(
                title="Ошибка",
                message=f"Метаданные для таблицы '{table_name}' не загружены.",
                timeout=3
            )
            return

        table = self.db_instance.tables[table_name]

        # Поля для условий поиска
        for column in table.columns:
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = self.create_search_widget(column)

            field_row = self.create_field_row(f"{display_name}:", widget, is_search=True)
            self.search_layout.addWidget(field_row)
            self.search_widgets[column.name] = widget

        # Поля для новых значений (пропускаем автоинкрементные PK)
        for column in table.columns:
            if column.primary_key and column.autoincrement:
                continue

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = self.create_update_widget(column)
            required = not column.nullable

            field_row = self.create_field_row(f"{display_name}:", widget, required, is_search=False)
            self.update_layout.addWidget(field_row)
            self.update_widgets[column.name] = widget

        # Добавляем растягивающие элементы
        self.search_layout.addStretch()
        self.update_layout.addStretch()

    def create_search_widget(self, column):
        """Создает виджет для условия поиска на основе типа столбца."""
        if isinstance(column.type, SQLEnum):
            widget = QComboBox()
            widget.addItem("")  # пустой вариант — не фильтровать
            widget.addItems(column.type.enums)
        elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
            widget = QLineEdit()
            widget.setPlaceholderText("Введите через двоеточие или оставьте пустым")
        elif isinstance(column.type, Boolean):
            widget = QComboBox()
            widget.addItem("")
            widget.addItem("Да", True)
            widget.addItem("Нет", False)
        elif isinstance(column.type, Date):
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setSpecialValueText("Не задано")
            widget.setDate(QDate(2000, 1, 1))
            widget.setMinimumDate(QDate(1900, 1, 1))
            widget.setMaximumDate(QDate(2100, 12, 31))
        elif isinstance(column.type, Integer):
            widget = QLineEdit()
            widget.setPlaceholderText("Целое число или оставьте пустым")
            validator = QIntValidator()
            validator.setBottom(-2147483648)
            validator.setTop(2147483647)
            widget.setValidator(validator)
        elif isinstance(column.type, Numeric):
            widget = QLineEdit()
            widget.setPlaceholderText("Число с плавающей точкой или оставьте пустым")
            validator = QDoubleValidator()
            validator.setBottom(-999999999999.99)
            validator.setTop(999999999999.99)
            validator.setDecimals(10)
            validator.setNotation(QDoubleValidator.StandardNotation)
            widget.setValidator(validator)
        elif isinstance(column.type, Text):
            widget = QTextEdit()
            widget.setPlaceholderText("Текст или оставьте пустым")
        elif isinstance(column.type, String):
            widget = QLineEdit()
            widget.setPlaceholderText("Текст или оставьте пустым")
            max_length = getattr(column.type, 'length', 255)
            if max_length:
                widget.setMaxLength(max_length)
        else:
            widget = QLineEdit()
            widget.setPlaceholderText("Значение или оставьте пустым")

        # Подключаем валидацию при изменении
        if isinstance(widget, (QLineEdit, QTextEdit)):
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda: self.validate_field(widget, column, True))
            else:
                widget.textChanged.connect(lambda: self.validate_field(widget, column, True))
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(lambda: self.validate_field(widget, column, True))
        elif isinstance(widget, QDateEdit):
            widget.dateChanged.connect(lambda: self.validate_field(widget, column, True))

        return widget

    def create_update_widget(self, column):
        """Создает виджет для ввода нового значения на основе типа столбца."""
        if isinstance(column.type, SQLEnum):
            widget = QComboBox()
            widget.addItem("")
            widget.addItems(column.type.enums)
            widget.setEditable(False)
        elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
            widget = QLineEdit()
            widget.setPlaceholderText("Введите значения через двоеточие: знач1:знач2")
        elif isinstance(column.type, Boolean):
            widget = QCheckBox("Да")
        elif isinstance(column.type, Date):
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            widget.setMinimumDate(QDate(1900, 1, 1))
            widget.setMaximumDate(QDate(2100, 12, 31))
        elif isinstance(column.type, Integer):
            widget = QLineEdit()
            widget.setPlaceholderText("Целое число")
            validator = QIntValidator()
            validator.setBottom(-2147483648)
            validator.setTop(2147483647)
            widget.setValidator(validator)
        elif isinstance(column.type, Numeric):
            widget = QLineEdit()
            widget.setPlaceholderText("Число с плавающей точкой")
            validator = QDoubleValidator()
            validator.setBottom(-999999999999.99)
            validator.setTop(999999999999.99)
            validator.setDecimals(10)
            validator.setNotation(QDoubleValidator.StandardNotation)
            widget.setValidator(validator)
        elif isinstance(column.type, Text):
            widget = QTextEdit()
            widget.setPlaceholderText("Текст")
        elif isinstance(column.type, String):
            widget = QLineEdit()
            max_length = getattr(column.type, 'length', 255)
            if max_length:
                widget.setMaxLength(max_length)
        else:
            widget = QLineEdit()
            widget.setPlaceholderText("Новое значение")

        # Подключаем валидацию при изменении
        if isinstance(widget, (QLineEdit, QTextEdit)):
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda: self.validate_field(widget, column, False))
            else:
                widget.textChanged.connect(lambda: self.validate_field(widget, column, False))
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(lambda: self.validate_field(widget, column, False))
        elif isinstance(widget, QDateEdit):
            widget.dateChanged.connect(lambda: self.validate_field(widget, column, False))
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(lambda: self.validate_field(widget, column, False))

        return widget

    def validate_field(self, widget, column, is_search=True):
        """Валидирует отдельное поле и показывает ошибку под ним."""
        try:
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            is_valid = True
            error_message = ""
            success_message = ""

            if isinstance(widget, QLineEdit):
                text = widget.text().strip()

                # Проверка обязательных полей (только для обновления)
                if not is_search and not column.nullable and not text:
                    is_valid = False
                    error_message = "⚠️ Обязательное поле"

                elif text:  # Если поле не пустое
                    if isinstance(column.type, Integer):
                        if not text.lstrip('-').isdigit():
                            is_valid = False
                            error_message = "❌ Должно быть целым числом"
                        else:
                            value = int(text)
                            if value < -2147483648 or value > 2147483647:
                                is_valid = False
                                error_message = "❌ Вне диапазона INTEGER (-2,147,483,648 до 2,147,483,647)"
                            else:
                                success_message = "✅ Корректное целое число"

                    elif isinstance(column.type, Numeric):
                        try:
                            value = Decimal(text)
                            if hasattr(column.type, 'precision') and column.type.precision:
                                max_value = 10 ** column.type.precision - 1
                                if abs(value) > max_value:
                                    is_valid = False
                                    error_message = f"❌ Максимум {column.type.precision} цифр"
                                else:
                                    success_message = "✅ Корректное число"
                        except InvalidOperation:
                            is_valid = False
                            error_message = "❌ Некорректное число"

                    elif isinstance(column.type, String):
                        max_length = getattr(column.type, 'length', None)
                        if max_length and len(text) > max_length:
                            is_valid = False
                            error_message = f"❌ Максимум {max_length} символов (сейчас: {len(text)})"
                        else:
                            success_message = f"✅ Корректная строка ({len(text)}/{max_length if max_length else '∞'} символов)"

                        # Специфические проверки
                        if column.name.lower() in ['email', 'mail']:
                            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
                                is_valid = False
                                error_message = "❌ Некорректный email адрес"
                            else:
                                success_message = "✅ Корректный email"

                        elif column.name.lower() in ['phone', 'telephone', 'tel']:
                            if not re.match(r'^[\+]?[0-9\s\-\(\)]{10,15}$', text):
                                is_valid = False
                                error_message = "❌ Некорректный номер телефона"
                            else:
                                success_message = "✅ Корректный номер телефона"

            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                if not is_search and not column.nullable and not text:
                    is_valid = False
                    error_message = "⚠️ Обязательное поле"
                elif text:
                    success_message = f"✅ Текст ({len(text)} символов)"

            elif isinstance(widget, QComboBox):
                text = widget.currentText()
                if not is_search and not column.nullable and not text:
                    is_valid = False
                    error_message = "⚠️ Обязательное поле"
                elif text and isinstance(column.type, SQLEnum) and text not in column.type.enums:
                    is_valid = False
                    error_message = f"❌ Допустимые значения: {', '.join(column.type.enums)}"
                elif text:
                    success_message = "✅ Выбрано корректное значение"

            elif isinstance(widget, QDateEdit):
                if not is_search and not column.nullable and not widget.date().isValid():
                    is_valid = False
                    error_message = "⚠️ Обязательное поле"
                elif widget.date().isValid():
                    success_message = f"✅ Корректная дата: {widget.date().toString('dd.MM.yyyy')}"

            elif isinstance(widget, QCheckBox):
                success_message = "✅ Значение установлено" if widget.isChecked() else "☑️ Значение не установлено"
                is_valid = True  # CheckBox всегда валиден

            # Применяем стиль и показываем сообщение
            if is_search:
                # Для поиска ошибки не критичны, просто информационные сообщения
                if error_message:
                    widget.setProperty("class", "error-widget")
                    self.show_field_error(f"{display_name}:", error_message, True)
                elif success_message and text:  # Показываем успех только если есть текст
                    widget.setProperty("class", "success-widget")
                    self.show_field_success(f"{display_name}:", success_message, True)
                else:
                    widget.setProperty("class", "")
                    self.show_field_error(f"{display_name}:", "", True)
            else:
                # Для обновления строгая валидация
                if not is_valid:
                    widget.setProperty("class", "error-widget")
                    self.show_field_error(f"{display_name}:", error_message, False)
                else:
                    if success_message and (not isinstance(widget, (QLineEdit, QTextEdit)) or
                                            (isinstance(widget, (QLineEdit, QTextEdit)) and self.get_widget_text(
                                                widget).strip())):
                        widget.setProperty("class", "success-widget")
                        self.show_field_success(f"{display_name}:", success_message, False)
                    else:
                        widget.setProperty("class", "")
                        self.show_field_error(f"{display_name}:", "", False)

            # Обновляем стиль
            widget.setStyleSheet(self.styleSheet())

            return is_valid

        except Exception as e:
            print(f"Ошибка валидации поля: {e}")
            return False

    def get_widget_text(self, widget):
        """Возвращает текст из виджета в зависимости от его типа."""
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        return ""

    def validate_all_update_fields(self):
        """Проверяет валидность всех полей обновления."""
        all_valid = True
        errors = []

        for col_name, widget in self.update_widgets.items():
            column = self.db_instance.tables[self.table_combo.currentText()].c[col_name]
            display_name = self.COLUMN_HEADERS_MAP.get(col_name, col_name)

            # Проверяем обязательные поля
            if not column.nullable:
                if isinstance(widget, (QLineEdit, QTextEdit)) and not self.get_widget_text(widget).strip():
                    all_valid = False
                    errors.append(f"Поле '{display_name}' обязательно для заполнения")
                    self.show_field_error(f"{display_name}:", "⚠️ Обязательное поле", False)
                elif isinstance(widget, QComboBox) and not widget.currentText():
                    all_valid = False
                    errors.append(f"Поле '{display_name}' обязательно для заполнения")
                    self.show_field_error(f"{display_name}:", "⚠️ Обязательное поле", False)
                elif isinstance(widget, QDateEdit) and not widget.date().isValid():
                    all_valid = False
                    errors.append(f"Поле '{display_name}' обязательно для заполнения")
                    self.show_field_error(f"{display_name}:", "⚠️ Обязательное поле", False)

        return all_valid, errors

    # Остальные методы (on_search_clicked, build_search_condition, populate_update_fields,
    # on_update_clicked, build_update_values) остаются без изменений из предыдущего кода

    def on_search_clicked(self):
        """Обрабатывает нажатие кнопки 'Найти запись' с валидацией."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        # Валидация условий поиска
        validation_errors = self.validate_search_condition(table_name)
        if validation_errors:
            error_msg = "Ошибки валидации:\n• " + "\n• ".join(validation_errors)
            QMessageBox.warning(self, "Ошибки валидации", error_msg)
            return

        condition = self.build_search_condition(table_name)
        if not condition:
            notification.notify(title="Ошибка", message="Укажите хотя бы одно условие для поиска!", timeout=3)
            return

        try:
            # Сначала проверяем количество записей
            count = self.db_instance.count_records_filtered(table_name, condition)

            if count == 0:
                notification.notify(
                    title="Не найдено",
                    message="Запись, удовлетворяющая условиям, не найдена.",
                    timeout=3
                )
                self.btn_update.setEnabled(False)
                self.found_record_id = None
                return

            if count > 1:
                notification.notify(
                    title="⚠️ Несколько записей",
                    message=f"Найдено {count} записей. Уточните условия поиска!",
                    timeout=5
                )
                QMessageBox.warning(
                    self,
                    "Уточните поиск",
                    f"Найдено {count} записей. Пожалуйста, добавьте больше условий, чтобы найти уникальную запись."
                )
                self.btn_update.setEnabled(False)
                self.found_record_id = None
                return

            # Если ровно одна запись — делаем SELECT *
            where_clause = " AND ".join([f'"{col}" = :{col}' for col in condition.keys()])
            select_query = f'SELECT * FROM "{table_name}" WHERE {where_clause} LIMIT 1'
            result = self.db_instance.execute_query(select_query, condition, fetch="dict")

            if not result:
                notification.notify(
                    title="Ошибка",
                    message="Запись не найдена, несмотря на подсчёт. Повторите поиск.",
                    timeout=3
                )
                self.btn_update.setEnabled(False)
                self.found_record_id = None
                return

            record = result[0]

            # Определяем ID записи через первичный ключ таблицы
            table = self.db_instance.tables[table_name]
            pk_columns = [col.name for col in table.primary_key.columns]

            if pk_columns:
                self.found_record_id = record.get(pk_columns[0])
            else:
                self.found_record_id = next(iter(record.values()), None)

            # Заполняем поля формы данными из записи
            self.populate_update_fields(record, table_name)

            # Разблокируем кнопку сохранения
            self.btn_update.setEnabled(True)

            notification.notify(
                title="✅ Найдено",
                message="Запись найдена. Введите новые значения и нажмите 'Сохранить'.",
                timeout=3
            )

        except Exception as e:
            notification.notify(
                title="❌ Ошибка поиска",
                message=f"Не удалось найти запись: {str(e)}",
                timeout=5
            )

    def validate_search_condition(self, table_name):
        """Валидация условий поиска перед выполнением запроса."""
        table = self.db_instance.tables[table_name]
        errors = []

        for col_name, widget in self.search_widgets.items():
            column = getattr(table.c, col_name)
            display_name = self.COLUMN_HEADERS_MAP.get(col_name, col_name)

            try:
                if isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if text:  # Только если поле не пустое
                        if isinstance(column.type, Integer):
                            if not text.lstrip('-').isdigit():
                                errors.append(f"Поле '{display_name}' должно быть целым числом")
                            else:
                                value = int(text)
                                if value < -2147483648 or value > 2147483647:
                                    errors.append(
                                        f"Поле '{display_name}' должно быть в диапазоне от -2,147,483,648 до 2,147,483,647")

                        elif isinstance(column.type, Numeric):
                            try:
                                value = Decimal(text)
                                if hasattr(column.type, 'precision') and column.type.precision:
                                    max_value = 10 ** column.type.precision - 1
                                    if abs(value) > max_value:
                                        errors.append(f"Поле '{display_name}' не должно превышать {max_value}")
                            except InvalidOperation:
                                errors.append(f"Поле '{display_name}' должно быть числом")

                        elif isinstance(column.type, String):
                            max_length = getattr(column.type, 'length', None)
                            if max_length and len(text) > max_length:
                                errors.append(f"Поле '{display_name}' не должно превышать {max_length} символов")

                elif isinstance(widget, QDateEdit):
                    if widget.date().isValid() and widget.date().year() != 2000:
                        date_val = widget.date()
                        if date_val < QDate(1900, 1, 1) or date_val > QDate(2100, 12, 31):
                            errors.append(f"Дата в поле '{display_name}' должна быть между 1900-01-01 и 2100-12-31")

            except Exception as e:
                errors.append(f"Ошибка валидации поля '{display_name}': {str(e)}")

        return errors

    def build_search_condition(self, table_name):
        """Формирует словарь условий поиска из виджетов."""
        condition = {}
        table = self.db_instance.tables[table_name]

        for col_name, widget in self.search_widgets.items():
            column = getattr(table.c, col_name)

            if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                value = widget.currentText()
                if value:
                    condition[col_name] = value

            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                if text:
                    items = [item.strip() for item in text.split(":") if item.strip()]
                    condition[col_name] = items

            elif isinstance(widget, QComboBox) and isinstance(column.type, Boolean):
                index = widget.currentIndex()
                if index > 0:
                    condition[col_name] = widget.currentData()

            elif isinstance(widget, QDateEdit):
                if widget.date().isValid() and widget.date().year() != 2000:
                    condition[col_name] = widget.date().toString("yyyy-MM-dd")

            elif isinstance(widget, (QLineEdit, QTextEdit)):
                text = self.get_widget_text(widget).strip()
                if text:
                    if isinstance(column.type, Integer):
                        if not text.lstrip('-').isdigit():
                            return None
                        condition[col_name] = int(text)
                    elif isinstance(column.type, Numeric):
                        try:
                            condition[col_name] = float(text)
                        except ValueError:
                            return None
                    else:
                        condition[col_name] = text

        return condition

    def populate_update_fields(self, record, table_name):
        """Автозаполняет поля для редактирования на основе найденной записи."""
        table = self.db_instance.tables[table_name]

        for col_name, widget in self.update_widgets.items():
            if col_name not in record:
                continue

            value = record[col_name]
            column = getattr(table.c, col_name)

            try:
                if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                    index = widget.findText(str(value))
                    widget.setCurrentIndex(index if index >= 0 else 0)

                elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                    if isinstance(value, list):
                        widget.setText(':'.join(map(str, value)))
                    elif isinstance(value, str):
                        cleaned = value.strip('[]').replace("'", "").replace('"', "")
                        parts = [v.strip() for v in cleaned.split(':') if v.strip()]
                        widget.setText(':'.join(parts))
                    else:
                        widget.setText('')

                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(value))

                elif isinstance(widget, QDateEdit):
                    if isinstance(value, (str, datetime)):
                        if isinstance(value, datetime):
                            qdate = QDate(value.year, value.month, value.day)
                        else:
                            qdate = QDate.fromString(value, "yyyy-MM-dd")
                        if qdate.isValid():
                            widget.setDate(qdate)

                elif isinstance(widget, QLineEdit):
                    if value is None:
                        widget.setText('')
                    elif isinstance(value, Decimal):
                        widget.setText(str(value))
                    elif isinstance(value, (int, float)):
                        widget.setText(str(value))
                    else:
                        widget.setText(str(value))

                elif isinstance(widget, QTextEdit):
                    if value is None:
                        widget.clear()
                    else:
                        widget.setPlainText(str(value))

                # Валидируем поле после заполнения
                self.validate_field(widget, column, False)

            except Exception as e:
                print(f"Ошибка при заполнении поля {col_name}: {e}")

    def on_update_clicked(self):
        """Обрабатывает нажатие кнопки 'Сохранить изменения' с валидацией."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        # Валидация всех полей обновления
        all_valid, errors = self.validate_all_update_fields()
        if not all_valid:
            error_msg = "Обнаружены ошибки в полях:\n• " + "\n• ".join(errors)
            QMessageBox.warning(self, "Ошибки валидации", error_msg)
            return

        # Дополнительная валидация значений
        validation_errors = self.validate_update_values(table_name)
        if validation_errors:
            error_msg = "Ошибки валидации значений:\n• " + "\n• ".join(validation_errors)
            QMessageBox.warning(self, "Ошибки валидации", error_msg)
            return

        new_values = self.build_update_values(table_name)
        if new_values is None:
            return
        if not new_values:
            notification.notify(title="Ошибка", message="Нет данных для обновления!", timeout=3)
            return

        condition = self.build_search_condition(table_name)
        if not condition:
            notification.notify(title="Ошибка", message="Укажите условия для поиска записи!", timeout=3)
            return

        # Подтверждение действия
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите обновить запись в таблице '{table_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Выполняем обновление
        success = self.db_instance.update_data(table_name, condition, new_values)
        if success:
            notification.notify(
                title="✅ Успех",
                message=f"Запись успешно обновлена в таблице '{table_name}'.",
                timeout=5
            )
            self.accept()
        else:
            notification.notify(
                title="❌ Ошибка",
                message="Не удалось обновить запись. Проверьте логи.",
                timeout=5
            )

    def validate_update_values(self, table_name):
        """Валидация новых значений перед обновлением."""
        table = self.db_instance.tables[table_name]
        errors = []

        for col_name, widget in self.update_widgets.items():
            column = getattr(table.c, col_name)
            display_name = self.COLUMN_HEADERS_MAP.get(col_name, col_name)

            try:
                if isinstance(widget, (QLineEdit, QTextEdit)):
                    text = self.get_widget_text(widget).strip()

                    if text:  # Если поле не пустое
                        if isinstance(column.type, Integer):
                            if not text.lstrip('-').isdigit():
                                errors.append(f"Поле '{display_name}' должно быть целым числом")
                            else:
                                value = int(text)
                                if value < -2147483648 or value > 2147483647:
                                    errors.append(
                                        f"Поле '{display_name}' должно быть в диапазоне от -2,147,483,648 до 2,147,483,647")

                        elif isinstance(column.type, Numeric):
                            try:
                                value = Decimal(text)
                                if hasattr(column.type, 'precision') and column.type.precision:
                                    max_value = 10 ** column.type.precision - 1
                                    if abs(value) > max_value:
                                        errors.append(f"Поле '{display_name}' не должно превышать {max_value}")
                            except InvalidOperation:
                                errors.append(f"Поле '{display_name}' должно быть числом")

                elif isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                    value = widget.currentText()
                    if value and value not in column.type.enums:
                        errors.append(
                            f"Поле '{display_name}' должно содержать одно из значений: {', '.join(column.type.enums)}")

            except Exception as e:
                errors.append(f"Ошибка валидации поля '{display_name}': {str(e)}")

        return errors

    def build_update_values(self, table_name):
        """Формирует словарь новых значений из виджетов."""
        new_values = {}
        table = self.db_instance.tables[table_name]

        for col_name, widget in self.update_widgets.items():
            column = getattr(table.c, col_name)
            display_name = self.COLUMN_HEADERS_MAP.get(col_name, col_name)

            try:
                if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                    value = widget.currentText()
                    if not value and not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return None
                    new_values[col_name] = value if value else None

                elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                    text = widget.text().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.",
                                                timeout=3)
                            return None
                        new_values[col_name] = []
                    else:
                        new_values[col_name] = [x.strip() for x in text.split(":") if x.strip()]

                elif isinstance(widget, QCheckBox):
                    new_values[col_name] = widget.isChecked()

                elif isinstance(widget, QDateEdit):
                    qdate = widget.date()
                    if qdate.isValid():
                        new_values[col_name] = qdate.toString("yyyy-MM-dd")
                    elif not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return None
                    else:
                        new_values[col_name] = None

                elif isinstance(widget, (QLineEdit, QTextEdit)):
                    text = self.get_widget_text(widget).strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.",
                                                timeout=3)
                            return None
                        new_values[col_name] = None
                    else:
                        if isinstance(column.type, Integer):
                            if not text.lstrip('-').isdigit():
                                notification.notify(
                                    title="Ошибка",
                                    message=f"Поле '{display_name}' должно быть целым числом.",
                                    timeout=3
                                )
                                return None
                            new_values[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                new_values[col_name] = float(text)
                            except ValueError:
                                notification.notify(
                                    title="Ошибка",
                                    message=f"Поле '{display_name}' должно быть числом.",
                                    timeout=3
                                )
                                return None
                        else:
                            new_values[col_name] = text

            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка при обработке поля '{display_name}': {str(e)}",
                    timeout=5
                )
                return None

        return new_values


if __name__ == "__main__":
    # Пример использования (для тестирования)
    import sys
    from PySide6.QtWidgets import QApplication


    class MockDB:
        def __init__(self):
            from sqlalchemy import Table, Column, MetaData, Integer, String
            metadata = MetaData()
            self.tables = {
                "users": Table('users', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('name', String(100)),
                               Column('email', String(100)),
                               Column('age', Integer)
                               )
            }
            self.connected = True

        def is_connected(self):
            return self.connected

        def get_table_names(self):
            return ["users"]

        def count_records_filtered(self, table_name, condition):
            return 1

        def execute_query(self, query, params, fetch="dict"):
            return [{"id": 1, "name": "Test User", "email": "test@example.com", "age": 25}]

        def update_data(self, table_name, condition, new_values):
            return True


    app = QApplication(sys.argv)

    COLUMN_HEADERS_MAP = {
        "id": "ID",
        "name": "Имя",
        "email": "Email",
        "age": "Возраст"
    }

    REVERSE_COLUMN_HEADERS_MAP = {v: k for k, v in COLUMN_HEADERS_MAP.items()}

    dialog = EditRecordDialog(MockDB(), COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP)
    dialog.show()

    sys.exit(app.exec())