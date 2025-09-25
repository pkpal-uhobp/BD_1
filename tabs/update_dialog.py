from decimal import Decimal
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit, QTextEdit)
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
import re


class EditRecordDialog(QDialog):
    """Модальное окно для редактирования записей в выбранной таблице."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        self.setWindowTitle("Редактирование данных")
        self.setModal(True)
        self.resize(600, 700)

        # Устанавливаем тёмную палитру
        self.set_dark_palette()

        # Словари для хранения виджетов условий поиска и новых значений
        self.search_widgets = {}
        self.update_widgets = {}
        self.update_error_labels = {}  # Метки ошибок для обновления
        self.field_validity = {}  # Словарь для отслеживания валидности полей

        # ID найденной записи (для возможного использования в будущем)
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
                color: #64ffda;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px 0;
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

            QLineEdit, QDateEdit {
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

            QLineEdit:hover, QDateEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit::placeholder, QDateEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }

            QLineEdit.error, QDateEdit.error, QComboBox.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }

            QLineEdit.success, QDateEdit.success, QComboBox.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }

            QTextEdit {
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

            QTextEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QTextEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
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
                min-height: 30px;
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
                padding: 15px;
                margin: 5px 0;
                border: none;
            }

            #fieldRow {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0px;
            }

            .section-label {
                color: #8892b0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 0;
                border-bottom: 2px solid #ff79c6;
                margin-bottom: 10px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("РЕДАКТИРОВАНИЕ ДАННЫХ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title_label)

        # Контейнер для выбора таблицы
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_layout = QVBoxLayout(table_container)

        table_label = QLabel("Выберите таблицу:")
        table_label.setFont(QFont("Consolas", 12, QFont.Bold))
        table_label.setProperty("class", "section-label")
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
        search_label = QLabel("Условия поиска записи:")
        search_label.setFont(QFont("Consolas", 12, QFont.Bold))
        search_label.setProperty("class", "section-label")
        layout.addWidget(search_label)

        self.search_container = QWidget()
        self.search_container.setObjectName("searchContainer")
        self.search_layout = QVBoxLayout(self.search_container)

        scroll_area_search = QScrollArea()
        scroll_area_search.setWidgetResizable(True)
        scroll_area_search.setWidget(self.search_container)
        scroll_area_search.setMinimumHeight(145)
        layout.addWidget(scroll_area_search)

        # Область новых значений
        update_label = QLabel("Новые значения:")
        update_label.setFont(QFont("Consolas", 12, QFont.Bold))
        update_label.setProperty("class", "section-label")
        layout.addWidget(update_label)

        self.update_container = QWidget()
        self.update_container.setObjectName("updateContainer")
        self.update_layout = QVBoxLayout(self.update_container)

        scroll_area_update = QScrollArea()
        scroll_area_update.setWidgetResizable(True)
        scroll_area_update.setWidget(self.update_container)
        scroll_area_update.setMinimumHeight(145)
        layout.addWidget(scroll_area_update)

        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_search = QPushButton("НАЙТИ ЗАПИСЬ")
        self.btn_update = QPushButton("СОХРАНИТЬ ИЗМЕНЕНИЯ")
        self.btn_update.setEnabled(False)

        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_update.setCursor(Qt.PointingHandCursor)

        buttons_layout.addWidget(self.btn_search)
        buttons_layout.addWidget(self.btn_update)

        layout.addLayout(buttons_layout)

        # Подключаем обработчики
        self.btn_search.clicked.connect(self.on_search_clicked)
        self.btn_update.clicked.connect(self.on_update_clicked)

    def create_simple_field_row(self, label_text, widget):
        """Создает строку с меткой и виджетом, без метки ошибки."""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")

        row_layout.addWidget(label)
        row_layout.addWidget(widget, 1)

        return row_widget

    def create_field_row(self, label_text, widget):
        """Создает строку с меткой, виджетом ввода и меткой ошибки"""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)
        row_layout.setSpacing(5)

        # Горизонтальный layout для метки и виджета
        field_layout = QHBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")
        field_layout.addWidget(label)
        field_layout.addWidget(widget, 1)

        # Метка для ошибки (изначально скрыта)
        error_label = QLabel()
        error_label.setProperty("class", "error-label")
        error_label.setStyleSheet(self.styleSheet())
        error_label.setWordWrap(True)
        error_label.hide()

        row_layout.addLayout(field_layout)
        row_layout.addWidget(error_label)

        return row_widget, error_label

    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.update_error_labels:
            if error_message:
                self.update_error_labels[field_name].setText(error_message)
                self.update_error_labels[field_name].show()
                self.field_validity[field_name] = False
                # Подсветка ошибки
                widget = self.update_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def set_field_success(self, field_name, success_message):
        """Устанавливает сообщение об успехе для поля"""
        if field_name in self.update_error_labels:
            if success_message:
                self.update_error_labels[field_name].setText(success_message)
                self.update_error_labels[field_name].show()
                self.update_error_labels[field_name].setProperty("class", "success-label")
                self.update_error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка успеха
                widget = self.update_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.update_error_labels:
            self.update_error_labels[field_name].hide()
            self.update_error_labels[field_name].setText("")
            self.update_error_labels[field_name].setProperty("class", "error-label")
            self.update_error_labels[field_name].setStyleSheet(self.styleSheet())
            self.field_validity[field_name] = True
            # Убираем подсветку
            widget = self.update_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    def validate_field(self, display_name, widget, column, table_name):
        """Валидирует одно поле и возвращает (is_valid, value, error_message, success_message)"""
        import re

        def validate_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        def validate_phone(phone):
            cleaned_phone = re.sub(r'\D', '', phone)
            return 7 <= len(cleaned_phone) <= 15

        def validate_safe_chars(text):
            dangerous_patterns = [r';', r'--', r'/\*', r'\*/']
            return not any(re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns)

        def is_email_field(field_name):
            email_indicators = ['email', 'e-mail', 'mail', 'почта']
            return any(indicator in field_name.lower() for indicator in email_indicators)

        def is_phone_field(field_name):
            phone_indicators = ['phone', 'tel', 'telephone', 'mobile', 'телефон']
            return any(indicator in field_name.lower() for indicator in phone_indicators)

        try:
            # ENUM
            if isinstance(widget, QComboBox) and (hasattr(column.type, 'enums') or isinstance(column.type, SQLEnum)):
                value = widget.currentText().strip()
                if not value:
                    if not column.nullable:
                        return False, None, "⚠️ Обязательное поле", ""
                    return True, None, "", ""
                else:
                    allowed_values = getattr(column.type, 'enums', [])
                    if allowed_values and value not in allowed_values:
                        return False, None, f"❌ Допустимые значения: {', '.join(allowed_values)}", ""
                    return True, value, "", f"✅ Выбрано: {value}"

            # ARRAY
            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "⚠️ Обязательное поле", ""
                    return True, [], "", ""
                items = [item.strip() for item in text.split(":") if item.strip()]
                if not items and not column.nullable:
                    return False, None, "❌ Не может быть пустым", ""

                validated_items = []
                for i, item in enumerate(items):
                    if isinstance(column.type.item_type, Integer):
                        if not item.isdigit() and not (item.startswith('-') and item[1:].isdigit()):
                            return False, None, f"❌ Элемент {i + 1} должен быть целым числом", ""
                        validated_items.append(int(item))
                    elif isinstance(column.type.item_type, Numeric):
                        if not re.match(r'^-?\d+(\.\d+)?$', item):
                            return False, None, f"❌ Элемент {i + 1} должен быть числом", ""
                        validated_items.append(float(item))
                    else:
                        if not validate_safe_chars(item):
                            return False, None, f"❌ Элемент {i + 1} содержит запрещенные символы", ""
                        validated_items.append(item)

                # Проверка: длина массива > 0 (для Books.authors)
                if table_name == "Books" and column.name == "authors" and len(validated_items) == 0:
                    return False, None, "❌ Массив авторов не может быть пустым", ""

                return True, validated_items, "", f"✅ {len(validated_items)} элементов"

            # BOOLEAN
            elif isinstance(widget, QCheckBox):
                return True, widget.isChecked(), "", "✅ Установлено" if widget.isChecked() else "☑️ Не установлено"

            # DATE
            elif isinstance(widget, QDateEdit):
                qdate = widget.date()
                if not qdate.isValid():
                    if not column.nullable:
                        return False, None, "⚠️ Обязательное поле", ""
                    return True, None, "", ""
                current_date = QDate.currentDate()
                if qdate < QDate(1900, 1, 1):
                    return False, None, "❌ Дата слишком старая", ""
                if qdate > current_date.addYears(100):
                    return False, None, "❌ Дата слишком далекая в будущем", ""

                # Проверка для Issued_Books: даты должны быть >= issue_date
                if table_name == "Issued_Books":
                    issue_date_widget = self.update_widgets.get("Дата выдачи")
                    if issue_date_widget and issue_date_widget.date().isValid():
                        issue_date = issue_date_widget.date()
                        if qdate < issue_date:
                            if column.name == "expected_return_date":
                                return False, None, "❌ Ожидаемая дата возврата должна быть позже даты выдачи", ""
                            elif column.name == "actual_return_date":
                                return False, None, "❌ Фактическая дата возврата должна быть позже даты выдачи", ""

                return True, qdate.toString("yyyy-MM-dd"), "", f"✅ {qdate.toString('dd.MM.yyyy')}"

            # TEXT
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "⚠️ Обязательное поле", ""
                    return True, None, "", ""
                if not validate_safe_chars(text):
                    return False, None, "❌ Содержит запрещенные символы", ""
                return True, text, "", f"✅ {len(text)} символов"

            # LINEEDIT (String, Integer, Numeric)
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "⚠️ Обязательное поле", ""
                    return True, None, "", ""

                if not validate_safe_chars(text):
                    return False, None, "❌ Содержит запрещенные символы", ""

                # INTEGER
                if isinstance(column.type, Integer):
                    if not text.isdigit() and not (text.startswith('-') and text[1:].isdigit()):
                        return False, None, "❌ Должно быть целым числом", ""
                    value = int(text)
                    # CheckConstraint: discount_percent BETWEEN 0 AND 100
                    if table_name == "Readers" and column.name == "discount_percent":
                        if value < 0 or value > 100:
                            return False, None, "❌ Скидка должна быть от 0 до 100%", ""
                    # CheckConstraint: actual_rental_days >= 0
                    elif table_name == "Issued_Books" and column.name == "actual_rental_days":
                        if value < 0:
                            return False, None, "❌ Дни не могут быть отрицательными", ""
                    return True, value, "", f"✅ Целое: {value}"

                # NUMERIC
                elif isinstance(column.type, Numeric):
                    if not re.match(r'^-?\d+(\.\d+)?$', text):
                        return False, None, "❌ Должно быть числом (например: 15 или 3.14)", ""
                    try:
                        value = float(text)
                        # CheckConstraint: deposit_amount >= 0
                        if table_name == "Books" and column.name == "deposit_amount":
                            if value < 0:
                                return False, None, "❌ Залог не может быть отрицательным", ""
                        # CheckConstraint: daily_rental_rate > 0
                        elif table_name == "Books" and column.name == "daily_rental_rate":
                            if value <= 0:
                                return False, None, "❌ Стоимость аренды должна быть больше 0", ""
                        # CheckConstraint: damage_fine >= 0
                        elif table_name == "Issued_Books" and column.name == "damage_fine":
                            if value < 0:
                                return False, None, "❌ Штраф не может быть отрицательным", ""
                        # CheckConstraint: final_rental_cost >= 0 (если указано)
                        elif table_name == "Issued_Books" and column.name == "final_rental_cost":
                            if value < 0:
                                return False, None, "❌ Стоимость аренды не может быть отрицательной", ""
                        # Проверка точности NUMERIC(10,2)
                        if abs(value) > 99999999.99:
                            return False, None, "❌ Слишком большое число (макс. 99999999.99)", ""
                        return True, value, "", f"✅ Число: {value}"
                    except (ValueError, OverflowError):
                        return False, None, "❌ Некорректное числовое значение", ""

                # STRING
                elif isinstance(column.type, String):
                    max_length = getattr(column.type, 'length', None)
                    if max_length and len(text) > max_length:
                        return False, None, f"❌ Превышена длина ({len(text)}/{max_length} символов)", ""
                    # Специфическая валидация
                    if is_email_field(display_name) and not validate_email(text):
                        return False, None, "❌ Некорректный email адрес", ""
                    if is_phone_field(display_name) and not validate_phone(text):
                        return False, None, "❌ Некорректный номер телефона", ""
                    return True, text, "", f"✅ {len(text)} символов"

                else:
                    return True, text, "", f"✅ Текст: {text}"

            else:
                return False, None, "❌ Неизвестный тип поля", ""

        except Exception as e:
            return False, None, f"❌ Ошибка валидации: {str(e)}", ""

    def validate_date_constraints_real_time(self):
        """Перепроверяет все даты в Issued_Books при изменении любой из них."""
        table_name = "Issued_Books"
        if table_name not in self.db_instance.tables:
            return

        # Получаем виджеты по отображаемым именам
        issue_widget = self.update_widgets.get("Дата выдачи")
        expected_widget = self.update_widgets.get("Ожидаемая дата возврата")
        actual_widget = self.update_widgets.get("Фактическая дата возврата")

        if not issue_widget:
            return

        issue_date = issue_widget.date()
        if not issue_date.isValid():
            # Если дата выдачи не установлена — очищаем ошибки других дат
            if expected_widget:
                self.clear_field_error("Ожидаемая дата возврата")
            if actual_widget:
                self.clear_field_error("Фактическая дата возврата")
            return

        # Проверка: expected >= issue
        if expected_widget and expected_widget.date().isValid():
            expected_date = expected_widget.date()
            if expected_date < issue_date:
                self.set_field_error("Ожидаемая дата возврата", "❌ Ожидаемая дата возврата должна быть позже даты выдачи")
            else:
                self.clear_field_error("Ожидаемая дата возврата")
        elif expected_widget:
            self.clear_field_error("Ожидаемая дата возврата")

        # Проверка: actual >= issue
        if actual_widget and actual_widget.date().isValid():
            actual_date = actual_widget.date()
            if actual_date < issue_date:
                self.set_field_error("Фактическая дата возврата", "❌ Фактическая дата возврата должна быть позже даты выдачи")
            else:
                self.clear_field_error("Фактическая дата возврата")
        elif actual_widget:
            self.clear_field_error("Фактическая дата возврата")

    def validate_real_time(self, field_name):
        """Валидация в реальном времени при изменении поля"""
        if field_name not in self.update_widgets:
            return
        widget = self.update_widgets[field_name]
        table_name = self.table_combo.currentText()
        if table_name not in self.db_instance.tables:
            return

        table = self.db_instance.tables[table_name]
        col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(field_name, field_name)

        try:
            column = getattr(table.c, col_name)
        except AttributeError:
            self.set_field_error(field_name, "❌ Колонка не найдена в таблице")
            self.field_validity[field_name] = False
            return

        is_valid, value, error_message, success_message = self.validate_field(field_name, widget, column, table_name)

        if not is_valid:
            self.set_field_error(field_name, error_message)
            self.field_validity[field_name] = False
        else:
            if success_message:
                self.set_field_success(field_name, success_message)
            else:
                self.clear_field_error(field_name)
            self.field_validity[field_name] = True

        # === ВАЖНО: ПЕРЕПРОВЕРКА ДАТ ===
        # Если таблица Issued_Books и поле — одна из дат — перепроверяем все даты
        if table_name == "Issued_Books" and field_name in ["Дата выдачи", "Ожидаемая дата возврата", "Фактическая дата возврата"]:
            self.validate_date_constraints_real_time()
        # ===============================

        # Обновляем состояние кнопки "СОХРАНИТЬ ИЗМЕНЕНИЯ"
        self.check_update_button_state()

    def clear_fields(self):
        """Полностью очищает все поля ввода в обоих контейнерах."""
        # Очистка условий поиска
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.search_widgets.clear()

        # Очистка полей для новых значений
        while self.update_layout.count():
            item = self.update_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.update_widgets.clear()
        self.update_error_labels.clear()
        self.field_validity.clear()

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

        # Поля для условий поиска (без валидации)
        for column in table.columns:
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = self.create_search_widget(column)

            # Используем обычный метод, без метки ошибки
            field_row = self.create_simple_field_row(f"{display_name}:", widget)
            self.search_layout.addWidget(field_row)
            self.search_widgets[column.name] = widget

        # Поля для новых значений (пропускаем автоинкрементные PK)
        for column in table.columns:
            if column.primary_key and column.autoincrement:
                continue

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = self.create_update_widget(column)

            # Для update_widgets используем метод с меткой ошибки
            field_row, error_label = self.create_field_row(f"{display_name}:", widget)
            self.update_layout.addWidget(field_row)
            self.update_widgets[display_name] = widget
            self.update_error_labels[display_name] = error_label
            self.field_validity[display_name] = True  # Изначально валидно

            # Подключаем валидацию в реальном времени
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QDateEdit):
                widget.dateChanged.connect(lambda date, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda state, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(lambda: self.validate_real_time(display_name))

        # Добавляем растягивающие элементы
        self.search_layout.addStretch()
        self.update_layout.addStretch()

    def check_update_button_state(self):
        """Проверяет состояние полей и активирует/деактивирует кнопку сохранения"""
        # Кнопка должна быть активна, если запись найдена и все поля валидны
        has_data = self.has_update_data()
        all_valid = all(self.field_validity.values()) if self.field_validity else True
        self.btn_update.setEnabled(has_data and self.found_record_id is not None and all_valid)

    def has_update_data(self):
        """Проверяет, есть ли данные для обновления в полях"""
        for widget in self.update_widgets.values():
            if isinstance(widget, QLineEdit) and widget.text().strip():
                return True
            elif isinstance(widget, QComboBox) and widget.currentText():
                return True
            elif isinstance(widget, QDateEdit) and widget.date().isValid():
                return True
            elif isinstance(widget, QCheckBox):
                return True  # Чекбокс всегда имеет значение
        return False

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
        elif isinstance(column.type, (Integer, Numeric)):
            widget = QLineEdit()
            widget.setPlaceholderText("Число или оставьте пустым")
        elif isinstance(column.type, String):
            widget = QLineEdit()
            widget.setPlaceholderText("Текст или оставьте пустым")
        else:
            widget = QLineEdit()
            widget.setPlaceholderText("Значение или оставьте пустым")
        return widget

    def create_update_widget(self, column):
        """Создает виджет для ввода нового значения на основе типа столбца."""
        if isinstance(column.type, SQLEnum):
            widget = QComboBox()
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
        elif isinstance(column.type, (Integer, Numeric)):
            widget = QLineEdit()
            widget.setPlaceholderText("Число")
        elif isinstance(column.type, String):
            widget = QLineEdit()
        else:
            widget = QLineEdit()
            widget.setPlaceholderText("Новое значение")
        return widget

    def on_search_clicked(self):
        """Обрабатывает нажатие кнопки 'Найти запись'."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
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

            # Проверяем состояние кнопки сохранения
            self.check_update_button_state()

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

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    if isinstance(column.type, Integer):
                        if not text.isdigit():
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{col_name}' должно быть целым числом.",
                                timeout=3
                            )
                            return None
                        condition[col_name] = int(text)
                    elif isinstance(column.type, Numeric):
                        try:
                            condition[col_name] = float(text)
                        except ValueError:
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{col_name}' должно быть числом.",
                                timeout=3
                            )
                            return None
                    else:
                        condition[col_name] = text

        return condition

    def populate_update_fields(self, record, table_name):
        """Автозаполняет поля для редактирования на основе найденной записи."""
        table = self.db_instance.tables[table_name]

        for display_name, widget in self.update_widgets.items():
            col_name = next((k for k, v in self.COLUMN_HEADERS_MAP.items() if v == display_name), display_name)
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
                    if isinstance(value, str):
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
                self.validate_real_time(display_name)

            except Exception as e:
                print(f"Ошибка при заполнении поля {display_name}: {e}")
                widget.setText('')

    def on_update_clicked(self):
        """Обрабатывает нажатие кнопки 'Сохранить изменения'."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        # Проверяем, все ли поля валидны
        all_valid = all(self.field_validity.values())
        if not all_valid:
            notification.notify(
                title="❌ Ошибки валидации",
                message="Исправьте ошибки в форме перед отправкой",
                timeout=3
            )
            return

        # Проверка дат для Issued_Books
        if table_name == "Issued_Books":
            # Повторно проверим даты перед отправкой
            issue_widget = self.update_widgets.get("Дата выдачи")
            expected_widget = self.update_widgets.get("Ожидаемая дата возврата")
            actual_widget = self.update_widgets.get("Фактическая дата возврата")

            if issue_widget and issue_widget.date().isValid():
                issue_date = issue_widget.date()
                if expected_widget and expected_widget.date().isValid():
                    if expected_widget.date() < issue_date:
                        notification.notify(title="❌ Ошибка", message="Ожидаемая дата возврата должна быть позже даты выдачи", timeout=3)
                        return
                if actual_widget and actual_widget.date().isValid():
                    if actual_widget.date() < issue_date:
                        notification.notify(title="❌ Ошибка", message="Фактическая дата возврата должна быть позже даты выдачи", timeout=3)
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

    def build_update_values(self, table_name):
        """Формирует словарь новых значений из виджетов."""
        new_values = {}
        table = self.db_instance.tables[table_name]

        for display_name, widget in self.update_widgets.items():
            col_name = next((k for k, v in self.COLUMN_HEADERS_MAP.items() if v == display_name), display_name)
            column = getattr(table.c, col_name)

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

                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.",
                                                timeout=3)
                            return None
                        new_values[col_name] = None
                    else:
                        if isinstance(column.type, Integer):
                            if not text.isdigit():
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

                elif isinstance(widget, QTextEdit):
                    text = widget.toPlainText().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.",
                                                timeout=3)
                            return None
                        new_values[col_name] = None
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
