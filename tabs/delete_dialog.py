from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit)
from PySide6.QtCore import QDate
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
import re


class DeleteRecordDialog(QDialog):
    """Модальное окно для удаления записей из выбранной таблицы."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        self.condition_widgets = {}  # {col_name: widget}
        self.error_labels = {}  # {col_name: QLabel} для отображения ошибок
        self.validation_errors = {}  # {col_name: error_message}

        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.setWindowTitle("Удаление данных")
        self.setModal(True)
        self.resize(600, 700)

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

            QLineEdit, QDateEdit {
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

            QLineEdit:hover, QDateEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit.invalid, QDateEdit.invalid {
                border: 2px solid #ff5555;
                background: rgba(75, 25, 35, 0.8);
            }

            QLineEdit::placeholder, QDateEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }

            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
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
                                          stop: 0 #ff5252, 
                                          stop: 1 #ff3838);
                border: 2px solid #ff6b6b;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff3838, 
                                          stop: 1 #ff1e1e);
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
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(75, 25, 35, 0.3);
                border-radius: 4px;
                margin-top: 2px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Заголовок
        title_label = QLabel("УДАЛЕНИЕ ДАННЫХ")
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

        # Контейнер для полей условий
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

        # Кнопка удаления
        self.btn_delete = QPushButton("🗑️ УДАЛИТЬ ЗАПИСИ")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def clear_fields(self):
        """Полностью очищает все поля ввода."""
        self._clear_layout(self.fields_layout)
        self.condition_widgets.clear()
        self.error_labels.clear()
        self.validation_errors.clear()

    def create_field_row(self, label_text, widget, column_name):
        """Создает строку с меткой, виджетом ввода и меткой ошибки"""
        # Основной контейнер для всего поля
        main_widget = QWidget()
        main_widget.setObjectName("fieldMain")
        main_widget.setStyleSheet("""
            #fieldMain {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)

        # Вертикальный layout для метки, поля ввода и ошибки
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)

        # Горизонтальный layout для метки и поля ввода
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")

        row_layout.addWidget(label)
        row_layout.addWidget(widget, 1)

        # Метка для отображения ошибки (изначально скрыта)
        error_label = QLabel("")
        error_label.setObjectName("errorLabel")
        error_label.setStyleSheet(".error-label { color: #ff5555; }")
        error_label.setFont(QFont("Consolas", 9))
        error_label.setWordWrap(True)
        error_label.setVisible(False)

        # Добавляем в основной layout
        main_layout.addWidget(row_widget)
        main_layout.addWidget(error_label)

        # Сохраняем ссылку на метку ошибки
        self.error_labels[column_name] = error_label

        return main_widget

    def validate_integer(self, text, column_name):
        """Валидация целочисленных значений"""
        if not text.strip():
            return None, None  # Пустое значение допустимо

        # Проверка на целое число
        if not re.match(r'^-?\d+$', text):
            return None, f"Поле '{column_name}' должно содержать целое число"

        # Проверка на переполнение
        try:
            value = int(text)
            if value < -2147483648 or value > 2147483647:
                return None, f"Число выходит за пределы диапазона (-2147483648 до 2147483647)"
            return value, None
        except ValueError:
            return None, f"Некорректное целое число в поле '{column_name}'"

    def validate_numeric(self, text, column_name):
        """Валидация числовых значений с плавающей точкой"""
        if not text.strip():
            return None, None  # Пустое значение допустимо

        # Проверка на число (включая отрицательные и с плавающей точкой)
        if not re.match(r'^-?\d*\.?\d+$', text):
            return None, f"Поле '{column_name}' должно содержать число"

        # Проверка на переполнение
        try:
            value = float(text)
            return value, None
        except ValueError:
            return None, f"Некорректное число в поле '{column_name}'"

    def validate_string_length(self, text, column):
        """Валидация длины строки"""
        if not text.strip():
            return None, None  # Пустое значение допустимо

        if hasattr(column.type, 'length') and column.type.length:
            if len(text) > column.type.length:
                return None, f"Длина текста превышает максимальную ({column.type.length} символов)"

        return text, None

    def validate_array(self, text, column_name):
        """Валидация массива строк"""
        if not text.strip():
            return None, None  # Пустое значение допустимо

        items = [item.strip() for item in text.split(",") if item.strip()]

        # Проверка каждого элемента массива
        for i, item in enumerate(items):
            if not item:
                return None, f"Элемент {i + 1} массива '{column_name}' не может быть пустым"
            if len(item) > 255:  # Ограничение длины элемента массива
                return None, f"Элемент {i + 1} массива слишком длинный (макс. 255 символов)"

        return items, None

    def validate_date(self, date_edit, column_name):
        """Валидация даты"""
        if not date_edit.date().isValid() or date_edit.date().year() == 2000:
            return None, None  # Не заданная дата допустима

        # Проверка на разумные пределы дат
        current_date = QDate.currentDate()
        min_date = QDate(1900, 1, 1)

        if date_edit.date() < min_date:
            return None, f"Дата не может быть раньше 1900 года"

        if date_edit.date() > current_date.addYears(10):  # +10 лет в будущее
            return None, f"Дата не может быть более чем на 10 лет в будущем"

        return date_edit.date().toString("yyyy-MM-dd"), None

    def update_field_validation_ui(self, column_name, is_valid=True, error_message=""):
        """Обновляет UI для отображения статуса валидации"""
        widget = self.condition_widgets.get(column_name)
        error_label = self.error_labels.get(column_name)

        if not widget or not error_label:
            return

        # Обновляем стиль поля ввода
        if is_valid:
            widget.setStyleSheet("""
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                color: #f8f8f2;
            """)
        else:
            widget.setStyleSheet("""
                background: rgba(75, 25, 35, 0.8);
                border: 2px solid #ff5555;
                border-radius: 8px;
                padding: 12px;
                color: #f8f8f2;
            """)

        # Обновляем метку ошибки
        if error_message:
            error_label.setText(error_message)
            error_label.setStyleSheet(".error-label { color: #ff5555; }")
            error_label.setVisible(True)
        else:
            error_label.setText("")
            error_label.setVisible(False)

    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля условий для выбранной таблицы."""
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
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = None

            if isinstance(column.type, SQLEnum):
                widget = QComboBox()
                widget.addItem("")  # пустой элемент = не задано
                widget.addItems(column.type.enums)
                # Добавляем валидацию при изменении значения
                widget.currentTextChanged.connect(lambda text, col=column: self.validate_field(col))

            elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                widget = QLineEdit()
                widget.setPlaceholderText("Введите через запятую или оставьте пустым")
                # Добавляем валидацию при изменении текста
                widget.textChanged.connect(lambda text, col=column: self.validate_field(col))

            elif isinstance(column.type, Boolean):
                widget = QComboBox()
                widget.addItem("")  # не задано
                widget.addItem("Да", True)
                widget.addItem("Нет", False)
                # Добавляем валидацию при изменении значения
                widget.currentIndexChanged.connect(lambda idx, col=column: self.validate_field(col))

            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setSpecialValueText("Не задано")
                widget.setDate(QDate(2000, 1, 1))  # маркер "не задано"
                # Добавляем валидацию при изменении даты
                widget.dateChanged.connect(lambda date, col=column: self.validate_field(col))

            elif isinstance(column.type, Integer):
                widget = QLineEdit()
                widget.setPlaceholderText("Целое число или оставьте пустым")
                # Добавляем валидацию при изменении текста
                widget.textChanged.connect(lambda text, col=column: self.validate_field(col))

            elif isinstance(column.type, Numeric):
                widget = QLineEdit()
                widget.setPlaceholderText("Число или оставьте пустым")
                # Добавляем валидацию при изменении текста
                widget.textChanged.connect(lambda text, col=column: self.validate_field(col))

            elif isinstance(column.type, String):
                widget = QLineEdit()
                widget.setPlaceholderText("Текст или оставьте пустым")
                # Добавляем валидацию при изменении текста
                widget.textChanged.connect(lambda text, col=column: self.validate_field(col))

            else:
                widget = QLineEdit()
                widget.setPlaceholderText("Значение или оставьте пустым")
                # Добавляем валидацию при изменении текста
                widget.textChanged.connect(lambda text, col=column: self.validate_field(col))

            # Создаем строку с полем ввода и меткой ошибки
            field_row = self.create_field_row(f"{display_name}:", widget, column.name)
            self.fields_layout.addWidget(field_row)
            self.condition_widgets[column.name] = widget

        # Добавляем растягивающий элемент для выравнивания
        self.fields_layout.addStretch()

    def validate_field(self, column):
        """Валидирует отдельное поле и обновляет его UI"""
        widget = self.condition_widgets.get(column.name)
        if not widget:
            return True

        value = None
        error_message = None

        try:
            if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                value = widget.currentText()
                if value:  # Пустое значение допустимо
                    if value not in column.type.enums:
                        error_message = f"Значение должно быть одним из: {', '.join(column.type.enums)}"

            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                value, error_message = self.validate_array(text, column.name)

            elif isinstance(widget, QComboBox) and isinstance(column.type, Boolean):
                # Для Boolean всегда валидно, так как значения предопределены
                index = widget.currentIndex()
                if index > 0:  # пропускаем "не задано"
                    value = widget.currentData()

            elif isinstance(widget, QDateEdit):
                value, error_message = self.validate_date(widget, column.name)

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()

                if isinstance(column.type, Integer):
                    value, error_message = self.validate_integer(text, column.name)
                elif isinstance(column.type, Numeric):
                    value, error_message = self.validate_numeric(text, column.name)
                elif isinstance(column.type, String):
                    value, error_message = self.validate_string_length(text, column)
                else:
                    # Для неизвестных типов принимаем любое значение
                    value = text if text else None

        except Exception as e:
            error_message = f"Ошибка валидации: {str(e)}"

        # Обновляем UI и сохраняем ошибку
        is_valid = error_message is None
        self.update_field_validation_ui(column.name, is_valid, error_message)

        if error_message:
            self.validation_errors[column.name] = error_message
        elif column.name in self.validation_errors:
            del self.validation_errors[column.name]

        return is_valid

    def validate_all_fields(self):
        """Валидирует все поля и возвращает результат"""
        self.validation_errors.clear()

        table_name = self.table_combo.currentText()
        if table_name not in self.db_instance.tables:
            return False

        table = self.db_instance.tables[table_name]
        all_valid = True

        for column in table.columns:
            if not self.validate_field(column):
                all_valid = False

        return all_valid

    def on_delete_clicked(self):
        # Валидируем все поля перед удалением
        if not self.validate_all_fields():
            error_text = "\n".join([f"• {error}" for error in self.validation_errors.values()])
            QMessageBox.warning(
                self,
                "Ошибки валидации",
                f"Обнаружены ошибки в полях ввода:\n\n{error_text}\n\nПожалуйста, исправьте ошибки и попробуйте снова.",
                QMessageBox.Ok
            )
            return

        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        condition = {}
        table = self.db_instance.tables[table_name]

        for col_name, widget in self.condition_widgets.items():
            column = getattr(table.c, col_name)

            if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                value = widget.currentText()
                if value:
                    condition[col_name] = value

            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                if text:
                    items = [item.strip() for item in text.split(",") if item.strip()]
                    condition[col_name] = items

            elif isinstance(widget, QComboBox) and isinstance(column.type, Boolean):
                index = widget.currentIndex()
                if index > 0:  # пропускаем "не задано"
                    condition[col_name] = widget.currentData()

            elif isinstance(widget, QDateEdit):
                if widget.date().isValid() and widget.date().year() != 2000:
                    condition[col_name] = widget.date().toString("yyyy-MM-dd")

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    if isinstance(column.type, Integer):
                        condition[col_name] = int(text)
                    elif isinstance(column.type, Numeric):
                        condition[col_name] = float(text)
                    else:
                        condition[col_name] = text

        # Если условий нет — предупреждаем
        if not condition:
            reply = QMessageBox.warning(
                self,
                "Подтверждение",
                f"Вы не указали ни одного условия. Это удалит ВСЕ записи из таблицы '{table_name}'.\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Подсчёт количества записей для удаления
        try:
            count = self.db_instance.count_records_filtered(table_name, condition)
            if count == 0:
                notification.notify(
                    title="Информация",
                    message="Нет записей, удовлетворяющих условию.",
                    timeout=3
                )
                return

            # Подтверждение удаления
            reply = QMessageBox.warning(
                self,
                "Подтверждение удаления",
                f"Будет удалено {count} записей из таблицы '{table_name}'.\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.db_instance.delete_data(table_name, condition)
                if success:
                    notification.notify(
                        title="✅ Успех",
                        message=f"Удалено {count} записей из таблицы '{table_name}'.",
                        timeout=5
                    )
                    self.accept()
                else:
                    notification.notify(
                        title="❌ Ошибка",
                        message="Не удалось выполнить удаление. Проверьте логи.",
                        timeout=5
                    )

        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при проверке записей: {str(e)}",
                timeout=5
            )