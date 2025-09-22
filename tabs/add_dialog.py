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

    def create_field_row(self, label_text, widget):
        """Создает строку с меткой и виджетом ввода"""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_widget.setStyleSheet("""
            #fieldRow {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")

        row_layout.addWidget(label)
        row_layout.addWidget(widget, 1)

        return row_widget

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
            # Пропускаем автоинкрементные PK — они генерируются БД
            if column.primary_key and column.autoincrement:
                continue

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)

            # Определяем тип и создаём соответствующий виджет
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
            elif isinstance(column.type, Integer):
                widget = QLineEdit()
                placeholder = "Введите целое число"
            elif isinstance(column.type, Numeric):
                widget = QLineEdit()
                placeholder = "Введите число (с точкой)"
            elif isinstance(column.type, Boolean):
                widget = QCheckBox("Да")
                placeholder = ""
            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                placeholder = "Выберите дату"
            elif isinstance(column.type, DateTime):
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDateTime(QDateTime.currentDateTime())
                placeholder = "Выберите дату и время"
            elif isinstance(column.type, ARRAY):
                if isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    placeholder = "Введите значения через двоеточие: знач1:знач2"
                else:
                    widget = QLineEdit()
                    placeholder = "Введите значения через двоеточие"
            elif isinstance(column.type, Text):
                widget = QTextEdit()
                widget.setMaximumHeight(80)
                placeholder = "Введите текст"
            else:
                widget = QLineEdit()
                placeholder = "Введите значение"

            if isinstance(widget, (QLineEdit, QTextEdit)) and placeholder:
                widget.setPlaceholderText(placeholder)

            # Добавляем строку в layout
            field_row = self.create_field_row(f"{display_name}:", widget)
            self.fields_layout.addWidget(field_row)
            self.input_widgets[display_name] = widget

        # Добавляем растягивающий элемент для выравнивания
        self.fields_layout.addStretch()

    def on_add_clicked(self):
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        data = {}
        table = self.db_instance.tables[table_name]

        for display_name, widget in self.input_widgets.items():
            # Находим реальное имя колонки по отображаемому
            col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)
            try:
                column = getattr(table.c, col_name)
            except AttributeError:
                notification.notify(
                    title="Ошибка",
                    message=f"Колонка '{col_name}' не найдена в таблице '{table_name}'.",
                    timeout=5
                )
                return

            # --- Валидация по типам ---
            if isinstance(widget, QComboBox) and (hasattr(column.type, 'enums') or isinstance(column.type, SQLEnum)):
                value = widget.currentText()
                if not value:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    else:
                        data[col_name] = None
                else:
                    allowed_values = getattr(column.type, 'enums', [])
                    if allowed_values and value not in allowed_values:
                        notification.notify(
                            title="Ошибка",
                            message=f"Значение '{value}' не допустимо для поля '{display_name}'.",
                            timeout=5
                        )
                        return
                    data[col_name] = value

            elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    data[col_name] = []
                else:
                    items = [item.strip() for item in text.split(":") if item.strip()]
                    if not items and not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' не может быть пустым.",
                                            timeout=3)
                        return
                    data[col_name] = items

            elif isinstance(widget, QCheckBox):  # Boolean
                data[col_name] = widget.isChecked()

            elif isinstance(widget, QDateEdit):  # Date
                qdate = widget.date()
                if qdate.isValid():
                    data[col_name] = qdate.toString("yyyy-MM-dd")
                else:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    else:
                        data[col_name] = None

            elif isinstance(widget, QDateTimeEdit):  # DateTime
                qdatetime = widget.dateTime()
                if qdatetime.isValid():
                    data[col_name] = qdatetime.toString("yyyy-MM-dd HH:mm:ss")
                else:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    else:
                        data[col_name] = None

            elif isinstance(widget, QTextEdit):  # Text
                text = widget.toPlainText().strip()
                if not text:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    data[col_name] = None
                else:
                    data[col_name] = text

            elif isinstance(widget, QLineEdit):  # String / Integer / Numeric
                text = widget.text().strip()
                if not text:
                    if not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
                        return
                    data[col_name] = None
                else:
                    if isinstance(column.type, Integer):
                        if not text.isdigit():
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{display_name}' должно быть целым числом.",
                                timeout=3
                            )
                            return
                        data[col_name] = int(text)

                    elif isinstance(column.type, Numeric):
                        if not re.match(r'^-?\d+(\.\d+)?$', text):
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{display_name}' должно быть числом (например: 10 или 3.14).",
                                timeout=3
                            )
                            return
                        try:
                            data[col_name] = float(text)
                        except ValueError:
                            notification.notify(
                                title="Ошибка",
                                message=f"Некорректное числовое значение в поле '{display_name}'.",
                                timeout=3
                            )
                            return

                    elif isinstance(column.type, String):
                        max_length = getattr(column.type, 'length', None)
                        if max_length and len(text) > max_length:
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{display_name}' не должно превышать {max_length} символов.",
                                timeout=5
                            )
                            return
                        data[col_name] = text

                    else:
                        data[col_name] = text

            else:
                notification.notify(
                    title="Ошибка",
                    message=f"Неизвестный тип виджета для поля '{display_name}'.",
                    timeout=5
                )
                return

        # Финальная валидация
        for col in table.columns:
            if not col.nullable and not col.primary_key and col.name not in data:
                display = self.COLUMN_HEADERS_MAP.get(col.name, col.name)
                notification.notify(
                    title="Ошибка",
                    message=f"Поле '{display}' обязательно для заполнения.",
                    timeout=5
                )
                return

        # Вставляем данные
        success = self.db_instance.insert_data(table_name, data)
        if success:
            notification.notify(
                title="✅ Успех",
                message=f"Запись успешно добавлена в таблицу '{table_name}'.",
                timeout=5
            )
            self.accept()
        else:
            notification.notify(
                title="❌ Ошибка",
                message=f"Не удалось добавить запись. Проверьте логи (db/db_app.log).",
                timeout=5
            )