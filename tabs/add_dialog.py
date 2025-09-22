from sqlalchemy import DateTime, Text
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QTextEdit, QLineEdit, QDateTimeEdit)
from PySide6.QtCore import QDate, QDateTime
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
import re
from plyer import notification


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
        self.resize(500, 600)
        self.input_widgets = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Выбор таблицы
        table_label = QLabel("Таблица:")
        self.table_combo = QComboBox()
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
        layout.addWidget(table_label)
        layout.addWidget(self.table_combo)
        # Контейнер для полей ввода
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.fields_container)
        layout.addWidget(scroll_area)
        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопка добавления
        self.btn_add = QPushButton("Добавить запись")
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

            row_layout = QHBoxLayout()
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            label = QLabel(f"{display_name}:")
            label.setMinimumWidth(150)
            row_layout.addWidget(label)

            # Определяем тип и создаём соответствующий виджет
            widget = None
            # Внутри цикла for column in table.columns:
            if hasattr(column.type, 'enums') and column.type.enums:
                widget = QComboBox()
                widget.addItems(column.type.enums)  # если enum задан явно
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
                # Можно уточнить: ARRAY of что?
                if isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    placeholder = "Введите значения через двоеточие: знач1:знач2"
                else:
                    widget = QLineEdit()
                    placeholder = "Введите значения через двоеточие"
            elif isinstance(column.type, Text):
                widget = QTextEdit()  # или QLineEdit, если не нужно многострочное
                placeholder = "Введите текст"
            else:
                widget = QLineEdit()
                placeholder = "Введите значение"
            if isinstance(widget, QLineEdit):
                widget.setPlaceholderText(placeholder)
            row_layout.addWidget(widget)
            self.fields_layout.addLayout(row_layout)
            self.input_widgets[display_name] = widget

    def on_add_clicked(self):
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        data = {}
        table = self.db_instance.tables[table_name]
        for display_name, widget in self.input_widgets.items():
            # Находим реальное имя колонки по отображаемому
            col_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name,
                                                           display_name)  # 👈 ИСПРАВЛЕНО: не нужно искать в цикле!
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
                    # Дополнительная валидация: значение должно быть в списке enums
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
                    # Валидация по типу колонки
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
                        # Поддержка и целых, и дробных: "5", "5.0", "3.14"
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
                        # Можно добавить ограничение по длине, если нужно
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
                        # fallback для неизвестных типов
                        data[col_name] = text

            else:
                notification.notify(
                    title="Ошибка",
                    message=f"Неизвестный тип виджета для поля '{display_name}'.",
                    timeout=5
                )
                return

        # --- Финальная валидация: все ли обязательные поля заполнены? ---
        # (опционально, если хочешь перестраховаться)
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
