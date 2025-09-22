from sqlalchemy import DateTime, Text
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QTextEdit, QLineEdit, QDateTimeEdit)
from PySide6.QtCore import QDate, QDateTime
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
import re
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt


class AddRecordDialog(QDialog):
    """Модальное окно для добавления записи в выбранную таблицу БД."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.setWindowTitle("Добавление данных")
        self.setModal(True)
        self.resize(600, 700)
        self.input_widgets = {}
        self.error_labels = {}  # Словарь для хранения меток ошибок
        self.field_validity = {}  # Словарь для отслеживания валидности полей

        # Устанавливаем тёмную палитру
        self.set_dark_palette()
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
                color: #8892b0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }

            QComboBox {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
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

            QLineEdit, QTextEdit, QDateEdit, QDateTimeEdit {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }

            QLineEdit:hover, QTextEdit:hover, QDateEdit:hover, QDateTimeEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QDateTimeEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit.error, QTextEdit.error, QDateEdit.error, QDateTimeEdit.error, QComboBox.error {
                border: 2px solid #ff5555;
                background: rgba(75, 25, 35, 0.8);
            }

            QTextEdit {
                padding: 8px;
            }

            QCheckBox {
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
                spacing: 8px;
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
                font-size: 16px;
                font-weight: bold;
                padding: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-height: 50px;
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

            .error-label {
                color: #ff5555;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                margin-top: 2px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Заголовок
        title_label = QLabel("ДОБАВЛЕНИЕ ЗАПИСИ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title_label)

        # Контейнер для выбора таблицы
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_container.setStyleSheet("""
            #tableContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        table_layout = QVBoxLayout(table_container)

        table_label = QLabel("Выберите таблицу:")
        table_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.table_combo = QComboBox()
        self.table_combo.setMinimumHeight(40)

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

        # Контейнер для полей ввода
        fields_container = QWidget()
        fields_container.setObjectName("fieldsContainer")
        fields_container.setStyleSheet("""
            #fieldsContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.fields_layout = QVBoxLayout(fields_container)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_container)
        scroll_area.setMinimumHeight(400)
        layout.addWidget(scroll_area)

        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопка добавления
        self.btn_add = QPushButton("✅ ДОБАВИТЬ ЗАПИСЬ")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.on_add_clicked)
        layout.addWidget(self.btn_add)

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def clear_fields(self):
        """Полностью очищает все поля ввода и пересоздаёт layout."""
        self._clear_layout(self.fields_layout)
        self.input_widgets.clear()
        self.error_labels.clear()
        self.field_validity.clear()

    def create_field_row(self, label_text, widget):
        """Создает строку с меткой, виджетом ввода и меткой ошибки"""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_widget.setStyleSheet("""
            #fieldRow {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0px;
            }
        """)

        # Основной layout строки
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 8, 10, 8)
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
        error_label.setObjectName("errorLabel")
        error_label.setStyleSheet("""
            #errorLabel {
                color: #ff5555;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                margin-left: 180px;
            }
        """)
        error_label.setWordWrap(True)
        error_label.hide()

        row_layout.addLayout(field_layout)
        row_layout.addWidget(error_label)

        return row_widget, error_label

    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = False

                # Добавляем CSS класс для подсветки ошибки
                widget = self.input_widgets[field_name]
                if hasattr(widget, 'setStyleSheet'):
                    current_style = widget.styleSheet()
                    if 'error' not in current_style:
                        widget.setStyleSheet(current_style + " border: 2px solid #ff5555;")
            else:
                self.clear_field_error(field_name)

    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.field_validity[field_name] = True

            # Убираем CSS класс ошибки
            widget = self.input_widgets[field_name]
            if hasattr(widget, 'setStyleSheet'):
                # Восстанавливаем стандартные стили
                if isinstance(widget, (QLineEdit, QTextEdit, QDateEdit, QDateTimeEdit)):
                    widget.setStyleSheet("""
                        background: rgba(25, 25, 35, 0.8);
                        border: 2px solid #44475a;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        color: #f8f8f2;
                        selection-background-color: #64ffda;
                        selection-color: #0a0a0f;
                    """)
                elif isinstance(widget, QComboBox):
                    widget.setStyleSheet("""
                        background: rgba(25, 25, 35, 0.8);
                        border: 2px solid #44475a;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        color: #f8f8f2;
                        min-height: 20px;
                    """)

    def validate_field(self, display_name, widget, column):
        """Валидирует одно поле и возвращает (is_valid, value, error_message)"""
        col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)

        # Вспомогательные функции валидации
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
            # ВАЛИДАЦИЯ ДЛЯ КОМБОБОКСОВ (ENUM)
            if isinstance(widget, QComboBox) and (hasattr(column.type, 'enums') or isinstance(column.type, SQLEnum)):
                value = widget.currentText().strip()
                if not value:
                    if not column.nullable:
                        return False, None, "Обязательное поле"
                    return True, None, ""
                else:
                    allowed_values = getattr(column.type, 'enums', [])
                    if allowed_values and value not in allowed_values:
                        return False, None, f"Допустимые значения: {', '.join(allowed_values)}"
                    return True, value, ""

            # ВАЛИДАЦИЯ ДЛЯ МАССИВОВ
            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "Обязательное поле"
                    return True, [], ""

                items = [item.strip() for item in text.split(":") if item.strip()]
                if not items and not column.nullable:
                    return False, None, "Не может быть пустым"

                # Валидация элементов массива
                validated_items = []
                for i, item in enumerate(items):
                    if isinstance(column.type.item_type, Integer):
                        if not item.isdigit() and not (item.startswith('-') and item[1:].isdigit()):
                            return False, None, f"Элемент {i + 1} должен быть целым числом"
                        validated_items.append(int(item))
                    elif isinstance(column.type.item_type, Numeric):
                        if not re.match(r'^-?\d+(\.\d+)?$', item):
                            return False, None, f"Элемент {i + 1} должен быть числом"
                        validated_items.append(float(item))
                    else:
                        if not validate_safe_chars(item):
                            return False, None, f"Элемент {i + 1} содержит запрещенные символы"
                        validated_items.append(item)

                return True, validated_items, ""

            # ВАЛИДАЦИЯ ДЛЯ CHECKBOX (BOOLEAN)
            elif isinstance(widget, QCheckBox):
                return True, widget.isChecked(), ""

            # ВАЛИДАЦИЯ ДЛЯ ДАТЫ
            elif isinstance(widget, QDateEdit):
                qdate = widget.date()
                if not qdate.isValid():
                    if not column.nullable:
                        return False, None, "Требуется valid дата"
                    return True, None, ""

                current_date = QDate.currentDate()
                if qdate < QDate(1900, 1, 1):
                    return False, None, "Дата слишком старая"
                if qdate > current_date.addYears(100):
                    return False, None, "Дата слишком далекая в будущем"

                return True, qdate.toString("yyyy-MM-dd"), ""

            # ВАЛИДАЦИЯ ДЛЯ ДАТЫ И ВРЕМЕНИ
            elif isinstance(widget, QDateTimeEdit):
                qdatetime = widget.dateTime()
                if not qdatetime.isValid():
                    if not column.nullable:
                        return False, None, "Требуется valid дата и время"
                    return True, None, ""

                return True, qdatetime.toString("yyyy-MM-dd HH:mm:ss"), ""

            # ВАЛИДАЦИЯ ДЛЯ ТЕКСТОВЫХ ПОЛЕЙ
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "Обязательное поле"
                    return True, None, ""

                if not validate_safe_chars(text):
                    return False, None, "Содержит запрещенные символы"

                return True, text, ""

            # ВАЛИДАЦИЯ ДЛЯ ТЕКСТОВЫХ ПОЛЕЙ ВВОДА
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "Обязательное поле"
                    return True, None, ""

                if not validate_safe_chars(text):
                    return False, None, "Содержит запрещенные символы"

                # Валидация для Integer
                if isinstance(column.type, Integer):
                    if not text.isdigit() and not (text.startswith('-') and text[1:].isdigit()):
                        return False, None, "Должно быть целым числом"

                    value = int(text)
                    if hasattr(column.type, 'display_width'):
                        max_val = 2 ** (column.type.display_width * 8 - 1) - 1
                        if abs(value) > max_val:
                            return False, None, f"Число слишком большое (макс: {max_val})"

                    return True, value, ""

                # Валидация для Numeric
                elif isinstance(column.type, Numeric):
                    if not re.match(r'^-?\d+(\.\d+)?$', text):
                        return False, None, "Должно быть числом (например: 15 или 3.14)"

                    try:
                        value = float(text)
                        if abs(value) > 10 ** 15:
                            return False, None, "Число слишком большое"
                        return True, value, ""
                    except (ValueError, OverflowError):
                        return False, None, "Некорректное числовое значение"

                # Валидация для String
                elif isinstance(column.type, String):
                    max_length = getattr(column.type, 'length', None)
                    if max_length and len(text) > max_length:
                        return False, None, f"Превышена длина ({len(text)}/{max_length} символов)"

                    # Специфическая валидация для email
                    if is_email_field(display_name) and not validate_email(text):
                        return False, None, "Некорректный email адрес"

                    # Специфическая валидация для телефона
                    if is_phone_field(display_name) and not validate_phone(text):
                        return False, None, "Некорректный номер телефона"

                    return True, text, ""

                else:
                    return True, text, ""

            # НЕИЗВЕСТНЫЙ ТИП ВИДЖЕТА
            else:
                return False, None, "Неизвестный тип поля"

        except Exception as e:
            return False, None, f"Ошибка обработки: {str(e)}"

    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля для выбранной таблицы."""
        self.clear_fields()

        if table_name not in self.db_instance.tables:
            notification.notify(
                title="Ошибка",
                message=f"Метаданные для таблицы '{table_name}' не загружены.",
                timeout=3
            )
            return

        table = self.db_instance.tables[table_name]

        for column in table.columns:
            # Пропускаем автоинкрементные PK
            if column.primary_key and column.autoincrement:
                continue

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)

            # Создаем соответствующий виджет
            widget = None
            placeholder = ""

            if hasattr(column.type, 'enums') and column.type.enums:
                widget = QComboBox()
                widget.addItems(column.type.enums)
                widget.setEditable(False)
                placeholder = "Выберите значение"
            elif isinstance(column.type, String):
                widget = QLineEdit()
                placeholder = "Введите текст"
                # Подключаем валидацию в реальном времени для текстовых полей
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, Integer):
                widget = QLineEdit()
                placeholder = "Введите целое число"
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, Numeric):
                widget = QLineEdit()
                placeholder = "Введите число (с точкой)"
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, Boolean):
                widget = QCheckBox("Да")
                placeholder = ""
                widget.stateChanged.connect(lambda state, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                placeholder = "Выберите дату"
                widget.dateChanged.connect(lambda date, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, DateTime):
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDateTime(QDateTime.currentDateTime())
                placeholder = "Выберите дату и время"
                widget.dateTimeChanged.connect(lambda datetime, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, ARRAY):
                widget = QLineEdit()
                placeholder = "Введите значения через двоеточие: знач1:знач2"
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(column.type, Text):
                widget = QTextEdit()
                widget.setMaximumHeight(80)
                placeholder = "Введите текст"
                widget.textChanged.connect(lambda: self.validate_real_time(display_name))
            else:
                widget = QLineEdit()
                placeholder = "Введите значение"
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))

            if isinstance(widget, (QLineEdit, QTextEdit)) and placeholder:
                widget.setPlaceholderText(placeholder)

            # Создаем строку с меткой ошибки
            field_row, error_label = self.create_field_row(f"{display_name}:", widget)
            self.fields_layout.addWidget(field_row)
            self.input_widgets[display_name] = widget
            self.error_labels[display_name] = error_label
            self.field_validity[display_name] = True  # Изначально поле валидно

        self.fields_layout.addStretch()

    def validate_real_time(self, field_name):
        """Валидация в реальном времени при изменении поля"""
        if field_name not in self.input_widgets:
            return

        widget = self.input_widgets[field_name]
        table_name = self.table_combo.currentText()

        if table_name not in self.db_instance.tables:
            return

        table = self.db_instance.tables[table_name]
        col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(field_name, field_name)

        try:
            column = getattr(table.c, col_name)
        except AttributeError:
            return

        is_valid, value, error_message = self.validate_field(field_name, widget, column)
        self.set_field_error(field_name, error_message)

    def on_add_clicked(self):
        """Обработчик нажатия кнопки добавления с валидацией"""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        # Валидируем все поля перед отправкой
        all_valid = True
        data = {}
        table = self.db_instance.tables[table_name]

        for display_name, widget in self.input_widgets.items():
            col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)

            try:
                column = getattr(table.c, col_name)
            except AttributeError:
                self.set_field_error(display_name, "Колонка не найдена в таблице")
                all_valid = False
                continue

            is_valid, value, error_message = self.validate_field(display_name, widget, column)

            if not is_valid:
                self.set_field_error(display_name, error_message)
                all_valid = False
            else:
                self.clear_field_error(display_name)
                if value is not None:
                    data[col_name] = value

        # Проверка обязательных полей, которые могли быть пропущены
        for column in table.columns:
            if (not column.nullable and
                    not column.primary_key and
                    not column.autoincrement and
                    column.name not in data):

                display = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
                if display in self.input_widgets:  # Если поле есть в форме
                    self.set_field_error(display, "Обязательное поле")
                all_valid = False

        if not all_valid:
            notification.notify(
                title="❌ Ошибки валидации",
                message="Исправьте ошибки в форме перед отправкой",
                timeout=3
            )
            return

        # Проверка уникальности (если реализовано)
        if hasattr(self.db_instance, 'check_existing_record'):
            try:
                for column in table.columns:
                    if column.primary_key or column.unique:
                        if column.name in data:
                            exists = self.db_instance.check_existing_record(
                                table_name,
                                {column.name: data[column.name]}
                            )
                            if exists:
                                display = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
                                notification.notify(
                                    title="Ошибка уникальности",
                                    message=f"Запись с таким значением '{display}' уже существует",
                                    timeout=5
                                )
                                return
            except Exception as e:
                print(f"Ошибка проверки уникальности: {e}")

        # Вставляем данные
        try:
            success = self.db_instance.insert_data(table_name, data)
            if success:
                notification.notify(
                    title="✅ Успех",
                    message=f"Запись успешно добавлена в таблицу '{table_name}'",
                    timeout=5
                )
                self.accept()
            else:
                notification.notify(
                    title="❌ Ошибка базы данных",
                    message=f"Не удалось добавить запись в таблицу '{table_name}'",
                    timeout=5
                )
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при добавлении записи: {str(e)}",
                timeout=5
            )