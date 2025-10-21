from sqlalchemy import DateTime, Text
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QTextEdit, QLineEdit, QDateTimeEdit)
from PySide6.QtCore import QDate, QDateTime
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from sqlalchemy import Float, BigInteger, SmallInteger
import re
from custom.array_line_edit import ArrayLineEdit
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
from sqlalchemy.exc import IntegrityError, DBAPIError


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
        self.first_attempt = True  # Флаг первой попытки добавления

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
                background: rgba(15, 15, 25, 0.8);
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

            QLineEdit, QTextEdit, QDateEdit, QDateTimeEdit {
                background: rgba(15, 15, 25, 0.8);
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
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
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
                background: rgba(15, 15, 25, 0.8);
            }

            QCheckBox::indicator:hover {
                border: 2px solid #6272a4;
            }

            QCheckBox::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
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
                min-height: 30px;
            }

            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
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
        """)

    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = False
                # Подсветка ошибки - красная рамка и фон
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet("""
                    background: rgba(75, 25, 35, 0.8);
                    border: 2px solid #ff5555;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                    color: #f8f8f2;
                """)
            else:
                self.clear_field_error(field_name)

    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setText("")
            self.field_validity[field_name] = True
            # Убираем подсветку
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet("""
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            """)

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

        # Полная валидация поля
        is_valid, value, error_message, success_message = self.validate_field(field_name, widget, column, table_name)

        if not is_valid:
            # В реальном времени показываем ошибки только для некорректных данных
            # НЕ показываем ошибки для пустых обязательных полей до первой попытки
            if "Обязательное поле" in error_message and self.first_attempt:
                # Не показываем ошибку для пустого поля до первой попытки
                self.clear_field_error(field_name)
                self.field_validity[field_name] = True
            else:
                self.set_field_error(field_name, error_message)
                self.field_validity[field_name] = False
        else:
            # Для корректных полей просто очищаем ошибки, не показываем сообщения об успехе
            self.clear_field_error(field_name)
            self.field_validity[field_name] = True

    def validate_field(self, display_name, widget, column, table_name):
        """Валидирует одно поле и возвращает (is_valid, value, error_message, success_message)"""
        import re
        from decimal import Decimal, InvalidOperation

        def validate_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        def validate_phone(phone):
            cleaned_phone = re.sub(r'\D', '', phone)
            return 7 <= len(cleaned_phone) <= 15

        def validate_safe_chars(text):
            dangerous_patterns = [r';', r'--', r'/\*', r'\*/', r'<script', r'javascript:', r'on\w+\s*=']
            return not any(re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns)

        def validate_url(url):
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return re.match(pattern, url) is not None

        def validate_postal_code(code):
            pattern = r'^\d{6}$'
            return re.match(pattern, code) is not None

        def is_email_field(field_name):
            email_indicators = ['email', 'e-mail', 'mail', 'почта']
            return any(indicator in field_name.lower() for indicator in email_indicators)

        def is_phone_field(field_name):
            phone_indicators = ['phone', 'tel', 'telephone', 'mobile', 'телефон']
            return any(indicator in field_name.lower() for indicator in phone_indicators)

        def is_url_field(field_name):
            url_indicators = ['url', 'website', 'site', 'ссылка', 'веб']
            return any(indicator in field_name.lower() for indicator in url_indicators)

        def is_postal_code_field(field_name):
            postal_indicators = ['postal', 'zip', 'индекс', 'почтовый']
            return any(indicator in field_name.lower() for indicator in postal_indicators)

        def is_price_field(field_name):
            price_indicators = ['цена', 'price', 'стоимость', 'cost', 'залог', 'pledge', 'штраф', 'fine', 'аренда', 'rental', 'руб', '₽', 'р.']
            return any(indicator in field_name.lower() for indicator in price_indicators)

        try:
            # ENUM
            if isinstance(widget, QComboBox) and (hasattr(column.type, 'enums') or isinstance(column.type, SQLEnum)):
                value = widget.currentText().strip()
                if not value:
                    if not column.nullable:
                        return False, None, "Обязательное поле", ""
                    return True, None, "", ""
                else:
                    allowed_values = getattr(column.type, 'enums', [])
                    if allowed_values and value not in allowed_values:
                        return False, None, f"Допустимые значения: {', '.join(allowed_values)}", ""
                    return True, value, "", ""

            # ARRAY
            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                try:
                    from custom.array_line_edit import ArrayLineEdit as _ArrayLE
                except Exception:
                    _ArrayLE = None

                values_raw = None
                if _ArrayLE is not None and isinstance(widget, _ArrayLE):
                    values_raw = widget.getArray()
                else:
                text = widget.text().strip()
                    values_raw = [item.strip() for item in text.split(":") if item.strip()]

                if (values_raw is None) or (len(values_raw) == 0):
                    if not column.nullable:
                        return False, None, "Обязательное поле (массив не может быть пустым)", ""
                    return True, [], "", ""

                validated_items = []
                for i, item in enumerate(values_raw):
                    item_str = str(item).strip()
                    if isinstance(column.type.item_type, (Integer, SmallInteger, BigInteger)):
                        if not item_str or (not item_str.isdigit() and not (item_str.startswith('-') and item_str[1:].isdigit())):
                            return False, None, f"Элемент {i + 1} должен быть целым числом", ""
                        validated_items.append(int(item_str))
                    elif isinstance(column.type.item_type, (Numeric, Float)):
                        if not re.match(r'^-?\d+(\.\d+)?$', item_str):
                            return False, None, f"Элемент {i + 1} должен быть числом", ""
                        validated_items.append(float(item_str))
                    else:
                        if not validate_safe_chars(item_str):
                            return False, None, f"Элемент {i + 1} содержит запрещенные символы", ""
                        validated_items.append(item_str)

                return True, validated_items, "", ""

            # BOOLEAN
            elif isinstance(widget, QCheckBox):
                return True, widget.isChecked(), "", ""

            # DATE
            elif isinstance(widget, QDateEdit):
                qdate = widget.date()
                if not qdate.isValid():
                    if not column.nullable:
                        return False, None, "Обязательное поле (выберите дату)", ""
                    return True, None, "", ""
                current_date = QDate.currentDate()
                if qdate < QDate(1900, 1, 1):
                    return False, None, "Дата слишком старая (минимум 1900 год)", ""
                if qdate > current_date.addYears(100):
                    return False, None, "Дата слишком далекая в будущем (максимум +100 лет)", ""
                return True, qdate.toString("yyyy-MM-dd"), "", ""

            # DATETIME
            elif isinstance(widget, QDateTimeEdit):
                qdatetime = widget.dateTime()
                if not qdatetime.isValid():
                    if not column.nullable:
                        return False, None, "Обязательное поле", ""
                    return True, None, "", ""
                return True, qdatetime.toString("yyyy-MM-dd HH:mm:ss"), "", ""

            # TEXT
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "Обязательное поле", ""
                    return True, None, "", ""
                if not validate_safe_chars(text):
                    return False, None, "Содержит запрещенные символы", ""
                return True, text, "", ""

            # LINEEDIT (String, Integer, Numeric)
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        return False, None, "Обязательное поле", ""
                    return True, None, "", ""

                if not validate_safe_chars(text):
                    return False, None, "Содержит запрещенные символы", ""

                # INTEGER
                if isinstance(column.type, (Integer, SmallInteger, BigInteger)):
                    if not text.isdigit() and not (text.startswith('-') and text[1:].isdigit()):
                        return False, None, "Должно быть целым числом", ""
                    value = int(text)
                    if isinstance(column.type, SmallInteger):
                        if value < -32768 or value > 32767:
                            return False, None, "Значение выходит за пределы SmallInteger (-32768 до 32767)", ""
                    elif isinstance(column.type, BigInteger):
                        if abs(value) > 9223372036854775807:
                            return False, None, "Значение слишком большое для BigInteger", ""
                    return True, value, "", ""

                # NUMERIC
                elif isinstance(column.type, (Numeric, Float)):
                    if not re.match(r'^-?\d+(\.\d+)?$', text):
                        return False, None, "Должно быть числом (например: 15 или 3.14)", ""
                    try:
                        value = float(text)
                        
                        # Проверка на отрицательные цены
                        if is_price_field(display_name) and value < 0:
                            return False, None, "Цена не может быть отрицательной", ""
                        
                        precision = getattr(column.type, 'precision', None)
                        scale = getattr(column.type, 'scale', None)
                        if scale is not None:
                            frac = text.split('.')[-1] if '.' in text else ''
                            if len(frac) > scale:
                                return False, None, f"Максимум {scale} знаков после точки", ""
                        if precision is not None:
                            digits = len(text.replace('.', '').replace('-', ''))
                            if digits > precision:
                                return False, None, f"Превышена точность ({digits}/{precision})", ""
                        return True, value, "", ""
                    except (ValueError, OverflowError):
                        return False, None, "Некорректное числовое значение", ""

                # STRING
                elif isinstance(column.type, String):
                    max_length = getattr(column.type, 'length', None)
                    if max_length and len(text) > max_length:
                        return False, None, f"Превышена длина ({len(text)}/{max_length} символов)", ""
                    if is_email_field(display_name) and not validate_email(text):
                        return False, None, "Некорректный email адрес", ""
                    if is_phone_field(display_name) and not validate_phone(text):
                        return False, None, "Некорректный номер телефона", ""
                    if is_url_field(display_name) and not validate_url(text):
                        return False, None, "Некорректный URL адрес", ""
                    if is_postal_code_field(display_name) and not validate_postal_code(text):
                        return False, None, "Некорректный почтовый индекс (должен быть 6 цифр)", ""
                    return True, text, "", ""

                else:
                    return True, text, "", ""

            else:
                return False, None, "Неизвестный тип поля", ""

        except Exception as e:
            return False, None, f"Ошибка валидации: {str(e)}", ""

    def on_add_clicked(self):
        """Добавление записи с подсветкой только ошибочных полей"""
        # Сбрасываем флаг первой попытки
        self.first_attempt = False
        
        # Очищаем все ошибки в начале
        for field_name in self.input_widgets:
            self.clear_field_error(field_name)
            
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        if table_name not in self.db_instance.tables:
            notification.notify(title="Ошибка", message=f"Таблица '{table_name}' не найдена.", timeout=3)
            return

        table = self.db_instance.tables[table_name]
        data = {}
        error_fields = {}

        # Проверяем все поля
        for display_name, widget in self.input_widgets.items():
            col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)
            try:
                column = getattr(table.c, col_name)
            except AttributeError:
                error_fields[display_name] = "❌ Колонка не найдена в таблице"
                continue

            # Проверяем пустые обязательные поля
            if not column.nullable:
                is_empty = False
                if isinstance(widget, QLineEdit):
                    is_empty = not widget.text().strip()
                elif isinstance(widget, QTextEdit):
                    is_empty = not widget.toPlainText().strip()
                elif isinstance(widget, QDateEdit):
                    is_empty = not widget.date().isValid()
                elif isinstance(widget, QDateTimeEdit):
                    is_empty = not widget.dateTime().isValid()
                elif isinstance(widget, QComboBox):
                    is_empty = not widget.currentText().strip()
                
                if is_empty:
                    error_fields[display_name] = "Обязательное поле"
                else:
                    # Собираем данные для вставки с правильными типами
                    if isinstance(widget, QLineEdit):
                        text_value = widget.text().strip()
                        # Преобразуем в правильный тип в зависимости от типа колонки
                        try:
                            if isinstance(column.type, (Integer, SmallInteger, BigInteger)):
                                data[col_name] = int(text_value) if text_value else None
                            elif isinstance(column.type, (Numeric, Float)):
                                data[col_name] = float(text_value) if text_value else None
                            else:
                                data[col_name] = text_value
                        except (ValueError, TypeError):
                            error_fields[display_name] = f"Некорректное значение для поля '{display_name}'"
                            continue
                    elif isinstance(widget, QTextEdit):
                        data[col_name] = widget.toPlainText().strip()
                    elif isinstance(widget, QDateEdit):
                        data[col_name] = widget.date().toString("yyyy-MM-dd")
                    elif isinstance(widget, QDateTimeEdit):
                        data[col_name] = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                    elif isinstance(widget, QComboBox):
                        data[col_name] = widget.currentText().strip()
                    elif isinstance(widget, QCheckBox):
                        data[col_name] = widget.isChecked()

        # Если есть ошибки — подсветим и покажем уведомление
        if error_fields:
            for field, message in error_fields.items():
                self.set_field_error(field, message)
            
            notification.notify(
                title="Ошибки валидации",
                message=f"Исправьте {len(error_fields)} ошиб(ки/ок) перед добавлением.",
                timeout=4
            )
            return

        # Попытка вставки записи
        try:
            result = self.db_instance.insert_data(table_name, data)
            
            if isinstance(result, tuple) and len(result) == 2:
                success, error_message = result
            else:
                success = result
                error_message = None

            if success:
                notification.notify(
                    title="Успех",
                    message=f"Запись успешно добавлена в '{table_name}'",
                    timeout=4
                )
                self.accept()
            else:
                if error_message:
                    # Очищаем все ошибки перед установкой новых
                    for field_name in self.input_widgets:
                        self.clear_field_error(field_name)
                    
                    # Ищем проблемные поля в тексте ошибки
                    err_text = error_message.lower()
                    for col in table.columns:
                        if col.name.lower() in err_text:
                            display = self.COLUMN_HEADERS_MAP.get(col.name, col.name)
                            self.set_field_error(display, f"Ошибка в поле '{display}'")
                
                notification.notify(
                    title="Ошибка базы данных",
                    message="Не удалось добавить запись. Проверьте введённые данные.",
                    timeout=5
                )

        except Exception as e:
            notification.notify(
                title="Ошибка",
                message=f"Ошибка при добавлении записи: {str(e)}",
                timeout=5
            )

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
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
                border: none;
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
        self.btn_add = QPushButton(" ДОБАВИТЬ ЗАПИСЬ")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.on_add_clicked)
        layout.addWidget(self.btn_add)

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
        
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(5)
        
        field_layout = QHBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")
        field_layout.addWidget(label)
        field_layout.addWidget(widget, 1)

        # Метка для ошибки
        error_label = QLabel()
        error_label.setObjectName("errorLabel")
        error_label.setProperty("class", "error-label")
        error_label.setStyleSheet(self.styleSheet())
        error_label.setWordWrap(True)
        error_label.hide()

        row_layout.addLayout(field_layout)
        row_layout.addWidget(error_label)

        return row_widget, error_label

    def clear_fields(self):
        """Очищает все поля ввода"""
        # Очищаем layout
        for i in reversed(range(self.fields_layout.count())):
            item = self.fields_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Очищаем словари
        self.input_widgets.clear()
        self.error_labels.clear()
        self.field_validity.clear()

    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля для выбранной таблицы"""
        # Очищаем существующие поля
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
            if hasattr(column.type, 'enums') and column.type.enums:
                widget = QComboBox()
                widget.addItems(column.type.enums)
                widget.setEditable(False)
            elif isinstance(column.type, String):
                widget = QLineEdit()
            elif isinstance(column.type, Integer):
                widget = QLineEdit()
            elif isinstance(column.type, Numeric):
                widget = QLineEdit()
            elif isinstance(column.type, Boolean):
                widget = QCheckBox("Да")
            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            elif isinstance(column.type, DateTime):
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDateTime(QDateTime.currentDateTime())
            elif isinstance(column.type, ARRAY):
                widget = ArrayLineEdit()
            elif isinstance(column.type, Text):
                widget = QTextEdit()
                widget.setMaximumHeight(80)
            else:
                widget = QLineEdit()

            # Создаем строку с меткой ошибки
            field_row, error_label = self.create_field_row(f"{display_name}:", widget)
            self.fields_layout.addWidget(field_row)

            self.input_widgets[display_name] = widget
            self.error_labels[display_name] = error_label
            self.field_validity[display_name] = True

            # Подключаем валидацию в реальном времени
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(lambda: self.validate_real_time(display_name))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QDateEdit):
                widget.dateChanged.connect(lambda date, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QDateTimeEdit):
                widget.dateTimeChanged.connect(lambda dt, dn=display_name: self.validate_real_time(dn))
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda state, dn=display_name: self.validate_real_time(dn))

        self.fields_layout.addStretch()


        field_layout.addWidget(widget, 1)



        # Метка для ошибки
        error_label = QLabel()

        error_label.setObjectName("errorLabel")

        error_label.setProperty("class", "error-label")

        error_label.setStyleSheet(self.styleSheet())

        error_label.setWordWrap(True)

        error_label.hide()



        row_layout.addLayout(field_layout)

        row_layout.addWidget(error_label)



        return row_widget, error_label



    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля для выбранной таблицы"""
        # Очищаем существующие поля
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.itemAt(i).widget().setParent(None)
        
        self.input_widgets.clear()
        self.error_labels.clear()
        self.field_validity.clear()


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

            if hasattr(column.type, 'enums') and column.type.enums:

                widget = QComboBox()

                widget.addItems(column.type.enums)

                widget.setEditable(False)

            elif isinstance(column.type, String):

                widget = QLineEdit()

            elif isinstance(column.type, Integer):

                widget = QLineEdit()

            elif isinstance(column.type, Numeric):

                widget = QLineEdit()

            elif isinstance(column.type, Boolean):

                widget = QCheckBox("Да")

            elif isinstance(column.type, Date):

                widget = QDateEdit()

                widget.setCalendarPopup(True)

                widget.setDate(QDate.currentDate())

            elif isinstance(column.type, DateTime):

                widget = QDateTimeEdit()

                widget.setCalendarPopup(True)

                widget.setDateTime(QDateTime.currentDateTime())

            elif isinstance(column.type, ARRAY):

                widget = ArrayLineEdit()

            elif isinstance(column.type, Text):

                widget = QTextEdit()

                widget.setMaximumHeight(80)

            else:

                widget = QLineEdit()



            # Создаем строку с меткой ошибки

            field_row, error_label = self.create_field_row(f"{display_name}:", widget)

            self.fields_layout.addWidget(field_row)



            self.input_widgets[display_name] = widget

            self.error_labels[display_name] = error_label

            self.field_validity[display_name] = True


            # Подключаем валидацию в реальном времени

            if isinstance(widget, QLineEdit):

                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QTextEdit):

                widget.textChanged.connect(lambda: self.validate_real_time(display_name))

            elif isinstance(widget, QComboBox):

                widget.currentTextChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QDateEdit):

                widget.dateChanged.connect(lambda date, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QDateTimeEdit):

                widget.dateTimeChanged.connect(lambda dt, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QCheckBox):

                widget.stateChanged.connect(lambda state, dn=display_name: self.validate_real_time(dn))



        self.fields_layout.addStretch()




        field_layout.addWidget(widget, 1)



        # Метка для ошибки
        error_label = QLabel()

        error_label.setObjectName("errorLabel")

        error_label.setProperty("class", "error-label")

        error_label.setStyleSheet(self.styleSheet())

        error_label.setWordWrap(True)

        error_label.hide()



        row_layout.addLayout(field_layout)

        row_layout.addWidget(error_label)



        return row_widget, error_label



    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля для выбранной таблицы"""
        # Очищаем существующие поля
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.itemAt(i).widget().setParent(None)
        
        self.input_widgets.clear()
        self.error_labels.clear()
        self.field_validity.clear()


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

            if hasattr(column.type, 'enums') and column.type.enums:

                widget = QComboBox()

                widget.addItems(column.type.enums)

                widget.setEditable(False)

            elif isinstance(column.type, String):

                widget = QLineEdit()

            elif isinstance(column.type, Integer):

                widget = QLineEdit()

            elif isinstance(column.type, Numeric):

                widget = QLineEdit()

            elif isinstance(column.type, Boolean):

                widget = QCheckBox("Да")

            elif isinstance(column.type, Date):

                widget = QDateEdit()

                widget.setCalendarPopup(True)

                widget.setDate(QDate.currentDate())

            elif isinstance(column.type, DateTime):

                widget = QDateTimeEdit()

                widget.setCalendarPopup(True)

                widget.setDateTime(QDateTime.currentDateTime())

            elif isinstance(column.type, ARRAY):

                widget = ArrayLineEdit()

            elif isinstance(column.type, Text):

                widget = QTextEdit()

                widget.setMaximumHeight(80)

            else:

                widget = QLineEdit()



            # Создаем строку с меткой ошибки

            field_row, error_label = self.create_field_row(f"{display_name}:", widget)

            self.fields_layout.addWidget(field_row)



            self.input_widgets[display_name] = widget

            self.error_labels[display_name] = error_label

            self.field_validity[display_name] = True


            # Подключаем валидацию в реальном времени

            if isinstance(widget, QLineEdit):

                widget.textChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QTextEdit):

                widget.textChanged.connect(lambda: self.validate_real_time(display_name))

            elif isinstance(widget, QComboBox):

                widget.currentTextChanged.connect(lambda text, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QDateEdit):

                widget.dateChanged.connect(lambda date, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QDateTimeEdit):

                widget.dateTimeChanged.connect(lambda dt, dn=display_name: self.validate_real_time(dn))

            elif isinstance(widget, QCheckBox):

                widget.stateChanged.connect(lambda state, dn=display_name: self.validate_real_time(dn))



        self.fields_layout.addStretch()


