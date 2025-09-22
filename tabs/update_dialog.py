from decimal import Decimal
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit)
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification



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

        # Словари для хранения виджетов условий поиска и новых значений
        self.search_widgets = {}
        self.update_widgets = {}

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

        # Область условий поиска
        layout.addWidget(QLabel("Условия поиска записи:"))
        self.search_container = QWidget()
        self.search_layout = QVBoxLayout(self.search_container)
        scroll_area_search = QScrollArea()
        scroll_area_search.setWidgetResizable(True)
        scroll_area_search.setWidget(self.search_container)
        scroll_area_search.setMaximumHeight(200)
        layout.addWidget(scroll_area_search)

        # Область новых значений
        layout.addWidget(QLabel("Новые значения:"))
        self.update_container = QWidget()
        self.update_layout = QVBoxLayout(self.update_container)
        scroll_area_update = QScrollArea()
        scroll_area_update.setWidgetResizable(True)
        scroll_area_update.setWidget(self.update_container)
        layout.addWidget(scroll_area_update)

        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопки
        self.btn_search = QPushButton("Найти запись")
        self.btn_update = QPushButton("Сохранить изменения")
        self.btn_update.setEnabled(False)  # Активируем после успешного поиска

        layout.addWidget(self.btn_search)
        layout.addWidget(self.btn_update)

        # Подключаем обработчики
        self.btn_search.clicked.connect(self.on_search_clicked)
        self.btn_update.clicked.connect(self.on_update_clicked)

    def clear_fields(self):
        """Полностью очищает все поля ввода в обоих контейнерах."""
        # Очистка условий поиска
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self.search_widgets.clear()

        # Очистка полей для новых значений
        while self.update_layout.count():
            item = self.update_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self.update_widgets.clear()

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

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

        # Поля для условий поиска (аналогично удалению)
        for column in table.columns:
            row_layout = QHBoxLayout()

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            label = QLabel(f"{display_name}:")
            label.setMinimumWidth(150)
            row_layout.addWidget(label)

            widget = self.create_search_widget(column)
            row_layout.addWidget(widget)
            self.search_layout.addLayout(row_layout)
            self.search_widgets[column.name] = widget

        # Поля для новых значений (пропускаем автоинкрементные PK)
        for column in table.columns:
            if column.primary_key and column.autoincrement:
                continue  # Пропускаем — нельзя редактировать

            row_layout = QHBoxLayout()

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            label = QLabel(f"{display_name}:")
            label.setMinimumWidth(150)
            row_layout.addWidget(label)

            widget = self.create_update_widget(column)
            row_layout.addWidget(widget)
            self.update_layout.addLayout(row_layout)
            # Используем отображаемое имя как ключ (для обратной совместимости с заполнением)
            self.update_widgets[display_name] = widget

    def create_search_widget(self, column):
        """Создает виджет для условия поиска на основе типа столбца."""
        if isinstance(column.type, SQLEnum):
            widget = QComboBox()
            widget.addItem("")  # пустой вариант — не фильтровать
            widget.addItems(column.type.enums)
        elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
            widget = QLineEdit()
            widget.setPlaceholderText("Введите через двоеточие(без пробела) или оставьте пустым")
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
                # На всякий случай, хотя count=1 должен гарантировать наличие
                notification.notify(
                    title="Ошибка",
                    message="Запись не найдена, несмотря на подсчёт. Повторите поиск.",
                    timeout=3
                )
                self.btn_update.setEnabled(False)
                self.found_record_id = None
                return

            record = result[0]

            # 🔥 Определяем ID записи через первичный ключ таблицы (метаданные SQLAlchemy)
            table = self.db_instance.tables[table_name]
            pk_columns = [col.name for col in table.primary_key.columns]  # список имён PK-столбцов

            if pk_columns:
                # Берём значение первого PK (обычно он один)
                self.found_record_id = record.get(pk_columns[0])
            else:
                # Fallback: если PK нет — берём первое значение в записи
                self.found_record_id = next(iter(record.values()), None)

            # Заполняем поля формы данными из записи
            self.populate_update_fields(record, table_name)

            # Разблокируем кнопку сохранения
            self.btn_update.setEnabled(True)

            # Уведомляем пользователя
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
            # Находим оригинальное имя столбца по отображаемому имени
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
                        # Очистка строки от скобок и кавычек
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

            except Exception as e:
                print(f"Ошибка при заполнении поля {display_name}: {e}")
                widget.setText('')

    def on_update_clicked(self):
        """Обрабатывает нажатие кнопки 'Сохранить изменения'."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        new_values = self.build_update_values(table_name)
        if new_values is None:  # Ошибка валидации
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
            # Находим оригинальное имя столбца по отображаемому имени
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
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
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
                            notification.notify(title="Ошибка", message=f"Поле '{display_name}' обязательно.", timeout=3)
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

            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка при обработке поля '{display_name}': {str(e)}",
                    timeout=5
                )
                return None

        return new_values