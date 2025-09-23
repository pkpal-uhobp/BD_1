from decimal import Decimal
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit)
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt


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
        scroll_area_search.setMinimumHeight(145)  # Установим одинаковую минимальную высоту
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
        scroll_area_update.setMinimumHeight(145)  # Установим одинаковую минимальную высоту
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

        # Подключаем сигналы изменения полей для активации кнопки сохранения
        self.connect_update_widgets_signals()

    def connect_update_widgets_signals(self):
        """Подключает сигналы изменения полей для активации кнопки сохранения"""
        # Этот метод будет вызываться после загрузки полей таблицы
        pass

    def create_field_row(self, label_text, widget):
        """Создает строку с меткой и виджетом ввода"""
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

            field_row = self.create_field_row(f"{display_name}:", widget)
            self.search_layout.addWidget(field_row)
            self.search_widgets[column.name] = widget

        # Поля для новых значений (пропускаем автоинкрементные PK)
        for column in table.columns:
            if column.primary_key and column.autoincrement:
                continue

            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = self.create_update_widget(column)

            field_row = self.create_field_row(f"{display_name}:", widget)
            self.update_layout.addWidget(field_row)
            self.update_widgets[display_name] = widget

            # Подключаем сигналы изменения для каждого виджета
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.check_update_button_state)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.check_update_button_state)
            elif isinstance(widget, QDateEdit):
                widget.dateChanged.connect(self.check_update_button_state)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.check_update_button_state)

        # Добавляем растягивающие элементы
        self.search_layout.addStretch()
        self.update_layout.addStretch()

    def check_update_button_state(self):
        """Проверяет состояние полей и активирует/деактивирует кнопку сохранения"""
        # Кнопка должна быть активна, если запись найдена и есть изменения в полях
        # или если поля заполнены (даже если запись еще не найдена)
        has_data = self.has_update_data()
        self.btn_update.setEnabled(has_data and self.found_record_id is not None)

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

            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка при обработке поля '{display_name}': {str(e)}",
                    timeout=5
                )
                return None

        return new_values