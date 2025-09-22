from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit)
from PySide6.QtCore import QDate
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification


class DeleteRecordDialog(QDialog):
    """Модальное окно для удаления записей из выбранной таблицы."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        self.condition_widgets = {}  # {col_name: widget}

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
        self.resize(500, 600)

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

        # Контейнер для полей условий
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

        # Кнопка удаления
        self.btn_delete = QPushButton("Удалить записи")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def clear_fields(self):
        """Полностью очищает все поля ввода."""
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self.condition_widgets.clear()

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

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
            row_layout = QHBoxLayout()

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            label = QLabel(f"{display_name}:")
            label.setMinimumWidth(150)
            row_layout.addWidget(label)

            widget = None

            if isinstance(column.type, SQLEnum):
                widget = QComboBox()
                widget.addItem("")  # пустой элемент = не задано
                widget.addItems(column.type.enums)

            elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                widget = QLineEdit()
                widget.setPlaceholderText("Введите через двоеточие(без пробела) или оставьте пустым")

            elif isinstance(column.type, Boolean):
                widget = QComboBox()
                widget.addItem("")  # не задано
                widget.addItem("Да", True)
                widget.addItem("Нет", False)

            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setSpecialValueText("Не задано")
                widget.setDate(QDate(2000, 1, 1))  # маркер "не задано"

            elif isinstance(column.type, (Integer, Numeric)):
                widget = QLineEdit()
                widget.setPlaceholderText("Число или оставьте пустым")

            elif isinstance(column.type, String):
                widget = QLineEdit()
                widget.setPlaceholderText("Текст или оставьте пустым")

            else:
                widget = QLineEdit()
                widget.setPlaceholderText("Значение или оставьте пустым")

            row_layout.addWidget(widget)
            self.fields_layout.addLayout(row_layout)
            self.condition_widgets[column.name] = widget

    def on_delete_clicked(self):
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
                        if not text.isdigit():
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{col_name}' должно быть целым числом.",
                                timeout=3
                            )
                            return
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
                            return
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
