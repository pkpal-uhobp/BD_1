import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QPushButton, QLabel,
    QVBoxLayout, QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QSizePolicy, QWidgetAction,
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QComboBox, QPushButton, QLabel, QMessageBox
)
from decimal import Decimal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QDateEdit, QPushButton, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QDate
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
import re

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
from plyer import notification

from db.Class_DB import DB

class MainWindow(QMainWindow):
    def __init__(self, db_instance=None):
        super().__init__()
        self.db_instance = db_instance  # можно передать подключение к БД
        self.setWindowTitle("Главное окно — Управление базой данных")
        self.setGeometry(200, 100, 850, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Приветственный текст
        welcome_label = QLabel("Добро пожаловать! Выберите действие в меню сверху.")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 14pt; color: #555; margin: 20px;")
        layout.addWidget(welcome_label)

        # Таблица для просмотра данных (скрыта по умолчанию)
        # Таблица для просмотра данных (скрыта по умолчанию)
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)  # Альтернативные строки
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Только чтение
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # Выбор строк
        self.data_table.setSortingEnabled(True)  # Включаем сортировку
        self.data_table.horizontalHeader().setSortIndicatorShown(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)  # Последний столбец растягивается
        self.data_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)  # Плавная прокрутка
        self.data_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.data_table.setWordWrap(True)  # Обрыв текста по ширине
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
                font-size: 10pt;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
                color: #333;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #b3d9ff;
                color: black;
            }
        """)
        self.data_table.setVisible(False)
        layout.addWidget(self.data_table)
        layout.setStretchFactor(self.data_table, 1)  # Растягивает таблицу по высоте

        layout.addStretch()

        # === Создаем панель инструментов (меню из кнопок сверху) ===
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)  # чтобы панель нельзя было двигать
        self.addToolBar(toolbar)

        # Кнопка: Создать схему и таблицы
        btn_create_schema = QPushButton("Создать схему")
        btn_create_schema.clicked.connect(self.create_schema)
        toolbar.addWidget(btn_create_schema)

        toolbar.addSeparator()

        # Кнопка: Добавить данные
        btn_add_data = QPushButton("Добавить данные")
        btn_add_data.clicked.connect(self.add_data)
        toolbar.addWidget(btn_add_data)

        # Кнопка: Изменить данные
        btn_edit_data = QPushButton("Изменить данные")
        btn_edit_data.clicked.connect(self.edit_data)
        toolbar.addWidget(btn_edit_data)

        # Кнопка: Удалить данные
        btn_delete_data = QPushButton("Удалить данные")
        btn_delete_data.clicked.connect(self.delete_data)
        toolbar.addWidget(btn_delete_data)

        # Кнопка: Вывести таблицу
        btn_show_table = QPushButton("Вывести таблицу")
        btn_show_table.clicked.connect(self.show_table)
        toolbar.addWidget(btn_show_table)

        # Кнопка: Удалить схему
        btn_drop_schema = QPushButton("Удалить схему")
        btn_drop_schema.clicked.connect(self.drop_schema)
        toolbar.addWidget(btn_drop_schema)
        toolbar.addSeparator()

        # === Прижимаем следующие элементы вправо ===
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer_action = QWidgetAction(toolbar)
        spacer_action.setDefaultWidget(spacer)
        toolbar.addAction(spacer_action)




        # Кнопка: Отключиться (справа)
        btn_logout = QPushButton("Отключиться")
        btn_logout.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        font-weight: bold;
                        padding: 5px 15px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
        btn_logout.clicked.connect(self.logout)
        toolbar.addWidget(btn_logout)
        self.sort_order = {}  # { column_index: Qt.SortOrder }
        self.current_table_data = []  # храним текущие данные для сортировки

        # Подключаем обработчик клика по заголовку
        self.data_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.last_table_name = None  # для обычной таблицы
        self.last_join_params = None

        # === Обработчики кнопок ===

    def create_schema(self):
        """Создаёт схему и таблицы в БД."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        success = self.db_instance.create_schema()

        if success:
            notification.notify(
                title="✅ Успех",
                message="Схема успешно создана или уже существовала.",
                timeout=5
            )
        else:
            notification.notify(
                title="❌ Ошибка",
                message="Не удалось создать схему. Проверьте логи (db/db_app.log).",
                timeout=5
            )

    def drop_schema(self):
        """Удаляет схему и все таблицы из БД."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        reply = QMessageBox.warning(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите УДАЛИТЬ ВСЮ СХЕМУ и ВСЕ ДАННЫЕ?\nЭто действие необратимо!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = self.db_instance.drop_schema()

        if success:
            notification.notify(
                title="✅ Схема удалена",
                message="Схема успешно удалена из базы данных.",
                timeout=5
            )
            # Скрываем таблицу, если она была отображена
            self.data_table.setVisible(False)
            self.current_table_data = []
        else:
            notification.notify(
                title="❌ Ошибка",
                message="Не удалось удалить схему. Проверьте логи (db/db_app.log).",
                timeout=5
            )

    def _clear_layout(self, layout):
        """Рекурсивно очищает QLayout от всех виджетов и вложенных layout'ов."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def edit_data(self):
        """Открывает модальное окно для редактирования записей в выбранной таблице."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        # Создаём модальное диалоговое окно
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование данных")
        dialog.setModal(True)
        dialog.resize(600, 700)

        layout = QVBoxLayout(dialog)

        # Выбор таблицы
        table_label = QLabel("Таблица:")
        table_combo = QComboBox()

        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц.",
                timeout=3
            )
            return

        table_combo.addItems(table_names)
        layout.addWidget(table_label)
        layout.addWidget(table_combo)

        # Контейнеры для условий и новых значений
        search_container = QWidget()
        scroll_area_search = QScrollArea()
        scroll_area_search.setWidgetResizable(True)
        scroll_area_search.setWidget(search_container)
        scroll_area_search.setMaximumHeight(200)
        layout.addWidget(QLabel("Условия поиска записи:"))
        layout.addWidget(scroll_area_search)

        update_container = QWidget()
        scroll_area_update = QScrollArea()
        scroll_area_update.setWidgetResizable(True)
        scroll_area_update.setWidget(update_container)
        layout.addWidget(QLabel("Новые значения:"))
        layout.addWidget(scroll_area_update)

        # Словари для виджетов
        search_widgets = {}
        update_widgets = {}

        def clear_fields():
            """Очищает все поля в обоих контейнерах, пересоздавая layout'ы."""
            # Пересоздаём layout для search_container
            QWidget().setLayout(search_container.layout())
            new_search_layout = QVBoxLayout(search_container)
            search_container.setLayout(new_search_layout)

            # Пересоздаём layout для update_container
            QWidget().setLayout(update_container.layout())
            new_update_layout = QVBoxLayout(update_container)
            update_container.setLayout(new_update_layout)

            search_widgets.clear()
            update_widgets.clear()

        def load_table_fields(table_name: str):
            """Загружает поля для условий поиска и новых значений."""
            clear_fields()

            if table_name not in self.db_instance.tables:
                notification.notify(
                    title="Ошибка",
                    message=f"Метаданные для таблицы '{table_name}' не загружены.",
                    timeout=3
                )
                return

            table = self.db_instance.tables[table_name]

            # Получаем актуальные layout'ы после пересоздания
            search_layout = search_container.layout()
            update_layout = update_container.layout()

            # Поля для условий поиска (как в delete_data)
            for column in table.columns:
                row_layout = QHBoxLayout()
                label = QLabel(f"{column.name}:")
                label.setMinimumWidth(150)
                row_layout.addWidget(label)

                widget = None

                if isinstance(column.type, SQLEnum):
                    widget = QComboBox()
                    widget.addItem("")  # пустой вариант — не фильтровать
                    widget.addItems(column.type.enums)
                elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    widget.setPlaceholderText("Введите через запятую или оставьте пустым")
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

                row_layout.addWidget(widget)
                search_layout.addLayout(row_layout)
                search_widgets[column.name] = widget

            # Поля для новых значений (как в add_data, но без PK)
            for column in table.columns:
                # Пропускаем автоинкрементные PK — их нельзя изменить
                if column.primary_key and column.autoincrement:
                    continue

                row_layout = QHBoxLayout()
                label = QLabel(f"{column.name}:")
                label.setMinimumWidth(150)
                row_layout.addWidget(label)

                widget = None

                if isinstance(column.type, SQLEnum):
                    widget = QComboBox()
                    widget.addItems(column.type.enums)
                    widget.setEditable(False)
                elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    widget.setPlaceholderText("Введите через запятую, например: Автор1, Автор2")
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

                if isinstance(widget, QLineEdit):
                    widget.setPlaceholderText("Новое значение")

                row_layout.addWidget(widget)
                update_layout.addLayout(row_layout)
                update_widgets[column.name] = widget

        # Загружаем поля для первой таблицы
        load_table_fields(table_combo.currentText())

        # Обновляем поля при смене таблицы
        table_combo.currentTextChanged.connect(load_table_fields)

        # Кнопки
        btn_search = QPushButton("Найти запись")
        btn_update = QPushButton("Сохранить изменения")
        btn_update.setEnabled(False)  # активируем только после успешного поиска

        layout.addWidget(btn_search)
        layout.addWidget(btn_update)

        found_record_id = None  # будем хранить ID найденной записи (если PK)

        def on_search_clicked():
            nonlocal found_record_id
            table_name = table_combo.currentText()
            if not table_name:
                notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                return

            condition = {}
            table = self.db_instance.tables[table_name]

            for col_name, widget in search_widgets.items():
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
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть целым числом.", timeout=3)
                                return
                            condition[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                condition[col_name] = float(text)
                            except ValueError:
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть числом.", timeout=3)
                                return
                        else:
                            condition[col_name] = text

            if not condition:
                notification.notify(title="Ошибка", message="Укажите хотя бы одно условие для поиска!", timeout=3)
                return

            # Ищем запись
            try:
                # Сначала делаем SELECT * ... WHERE ... LIMIT 1
                where_clause = " AND ".join([f"{col} = :{col}" for col in condition.keys()])
                select_query = f"SELECT * FROM \"{table_name}\" WHERE {where_clause} LIMIT 1"
                result = self.db_instance.execute_query(select_query, condition, fetch="dict")

                if not result or len(result) == 0:
                    notification.notify(
                        title="Не найдено",
                        message="Запись, удовлетворяющая условиям, не найдена.",
                        timeout=3
                    )
                    btn_update.setEnabled(False)
                    found_record_id = None
                    return

                # Нашли запись — заполняем поля новыми значениями (для удобства)
                record = result[0]
                found_record_id = record.get("id_book") or record.get("reader_id") or record.get(
                    list(record.keys())[0])  # fallback на первый столбец

                # Автозаполнение полей для редактирования
                for col_name, widget in update_widgets.items():
                    if col_name in record:
                        value = record[col_name]
                        if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                            index = widget.findText(str(value))
                            if index >= 0:
                                widget.setCurrentIndex(index)
                            else:
                                widget.setCurrentIndex(0)
                        elif isinstance(widget, QLineEdit):
                            # Универсально для list и строки в формате Python-списка
                            if isinstance(value, list):
                                print(2)
                                widget.setText(', '.join(value))

                            elif isinstance(value, str):

                                # Избавляемся от скобок и кавычек, превращаем в строку с запятыми

                                value = value.strip('[]')  # убираем скобки

                                value = value.replace("'", "").replace('"', "")

                                widget.setText(', '.join([v.strip() for v in value.split(',') if v.strip()]))
                            elif isinstance(value, Decimal):
                                widget.setText(str(value))
                            elif isinstance(value, int):
                                widget.setText(str(value))
                            else:

                                widget.setText('')

                        elif isinstance(widget, QCheckBox):
                            widget.setChecked(bool(value))

                        elif isinstance(widget, QDateEdit):
                            if isinstance(value, str):
                                try:
                                    qdate = QDate.fromString(value, "yyyy-MM-dd")
                                    if qdate.isValid():
                                        widget.setDate(qdate)
                                except:
                                    pass

                        elif isinstance(widget, QLineEdit):
                            widget.setText(str(value) if value is not None else "")

                btn_update.setEnabled(True)
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

        def on_update_clicked():
            table_name = table_combo.currentText()
            if not table_name:
                notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                return

            new_values = {}
            table = self.db_instance.tables[table_name]

            for col_name, widget in update_widgets.items():
                column = getattr(table.c, col_name)
                if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                    value = widget.currentText()
                    if value:  # разрешаем пустое значение, если поле nullable
                        new_values[col_name] = value
                    elif not column.nullable:
                        notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                        return



                elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):

                    text = widget.text().strip()

                    if not text:

                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)

                            return

                        new_values[col_name] = []

                    else:

                        # Универсально: разбиваем по запятым

                        new_values[col_name] = [x.strip() for x in text.split(",") if x.strip()]


                elif isinstance(widget, QCheckBox):
                    new_values[col_name] = widget.isChecked()

                elif isinstance(widget, QDateEdit):
                    qdate = widget.date()
                    if qdate.isValid():
                        new_values[col_name] = qdate.toString("yyyy-MM-dd")
                    else:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                            return

                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                            return
                        new_values[col_name] = None
                    else:
                        if isinstance(column.type, Integer):
                            if not text.isdigit():
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть целым числом.", timeout=3)
                                return
                            new_values[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                new_values[col_name] = float(text)
                            except ValueError:
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть числом.", timeout=3)
                                return
                        else:
                            new_values[col_name] = text

            if not new_values:
                notification.notify(title="Ошибка", message="Нет данных для обновления!", timeout=3)
                return

            # Формируем условие поиска (из search_widgets)
            condition = {}
            for col_name, widget in search_widgets.items():
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
                    if index > 0:
                        condition[col_name] = widget.currentData()

                elif isinstance(widget, QDateEdit):
                    if widget.date().isValid() and widget.date().year() != 2000:
                        condition[col_name] = widget.date().toString("yyyy-MM-dd")

                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if text:
                        if isinstance(column.type, Integer):
                            if text.isdigit():
                                condition[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                condition[col_name] = float(text)
                            except:
                                pass
                        else:
                            condition[col_name] = text

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
                dialog.accept()
            else:
                notification.notify(
                    title="❌ Ошибка",
                    message="Не удалось обновить запись. Проверьте логи.",
                    timeout=5
                )

        btn_search.clicked.connect(on_search_clicked)
        btn_update.clicked.connect(on_update_clicked)

        # Показываем диалог
        dialog.exec()

    def add_data(self):
        """Открывает модальное окно для добавления записи в выбранную таблицу."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        # Создаём модальное диалоговое окно
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление данных")
        dialog.setModal(True)
        dialog.resize(500, 600)

        layout = QVBoxLayout(dialog)

        # Выбор таблицы
        table_label = QLabel("Таблица:")
        table_combo = QComboBox()

        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц.",
                timeout=3
            )
            return

        table_combo.addItems(table_names)
        layout.addWidget(table_label)
        layout.addWidget(table_combo)

        # Контейнер для полей ввода (будет обновляться при смене таблицы)
        fields_container = QWidget()
        fields_layout = QVBoxLayout(fields_container)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_container)
        layout.addWidget(scroll_area)

        # Словарь для хранения виджетов ввода по имени колонки
        input_widgets = {}

        def clear_fields():
            """Полностью очищает все поля ввода и пересоздаёт layout."""
            # Удаляем все дочерние виджеты
            while fields_layout.count():
                item = fields_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    # Рекурсивно очищаем вложенные layout'ы
                    self._clear_layout(item.layout())
            # Очищаем словарь
            input_widgets.clear()

        def load_table_fields(table_name: str):
            """Загружает и отображает поля для выбранной таблицы."""
            clear_fields()

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
                label = QLabel(f"{column.name}:")
                label.setMinimumWidth(150)
                row_layout.addWidget(label)

                # Определяем тип и создаём соответствующий виджет
                widget = None

                if isinstance(column.type, SQLEnum):
                    widget = QComboBox()
                    widget.addItems(column.type.enums)
                    widget.setEditable(False)
                    placeholder = "Выберите значение"
                elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    placeholder = "Введите через запятую, например: Автор1, Автор2"
                elif isinstance(column.type, Boolean):
                    widget = QCheckBox("Да")
                    placeholder = ""
                elif isinstance(column.type, Date):
                    widget = QDateEdit()
                    widget.setCalendarPopup(True)
                    widget.setDate(QDate.currentDate())
                    placeholder = "Выберите дату"
                elif isinstance(column.type, (Integer, Numeric)):
                    widget = QLineEdit()
                    widget.setPlaceholderText("Число")
                    placeholder = "Введите число"
                elif isinstance(column.type, String):
                    widget = QLineEdit()
                    placeholder = "Введите текст"
                else:
                    widget = QLineEdit()
                    placeholder = "Введите значение"

                if isinstance(widget, QLineEdit):
                    widget.setPlaceholderText(placeholder)

                row_layout.addWidget(widget)
                fields_layout.addLayout(row_layout)
                input_widgets[column.name] = widget

        # Загружаем поля для первой таблицы
        load_table_fields(table_combo.currentText())

        # Обновляем поля при смене таблицы
        table_combo.currentTextChanged.connect(load_table_fields)

        # Кнопка добавления
        btn_add = QPushButton("Добавить запись")
        layout.addWidget(btn_add)

        def on_add_clicked():
            table_name = table_combo.currentText()
            if not table_name:
                notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                return

            data = {}
            table = self.db_instance.tables[table_name]

            for col_name, widget in input_widgets.items():
                column = getattr(table.c, col_name)

                if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                    value = widget.currentText()
                    if not value:
                        notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                        return
                    data[col_name] = value

                elif isinstance(widget, QLineEdit) and isinstance(column.type, ARRAY):
                    text = widget.text().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                            return
                        data[col_name] = []
                    else:
                        # Разбиваем по запятой и очищаем пробелы
                        items = [item.strip() for item in text.split(",") if item.strip()]
                        if not items and not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' не может быть пустым.",
                                                timeout=3)
                            return
                        data[col_name] = items

                elif isinstance(widget, QCheckBox):
                    data[col_name] = widget.isChecked()

                elif isinstance(widget, QDateEdit):
                    qdate = widget.date()
                    if qdate.isValid():
                        data[col_name] = qdate.toString("yyyy-MM-dd")
                    else:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                            return

                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if not text:
                        if not column.nullable:
                            notification.notify(title="Ошибка", message=f"Поле '{col_name}' обязательно.", timeout=3)
                            return
                        data[col_name] = None
                    else:
                        # Пытаемся преобразовать в число, если нужно
                        if isinstance(column.type, Integer):
                            if not text.isdigit():
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть целым числом.", timeout=3)
                                return
                            data[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                data[col_name] = float(text)
                            except ValueError:
                                notification.notify(title="Ошибка", message=f"Поле '{col_name}' должно быть числом.",
                                                    timeout=3)
                                return
                        else:
                            data[col_name] = text

            # Вставляем данные
            success = self.db_instance.insert_data(table_name, data)
            if success:
                notification.notify(
                    title="✅ Успех",
                    message=f"Запись успешно добавлена в таблицу '{table_name}'.",
                    timeout=5
                )
                dialog.accept()
            else:
                notification.notify(
                    title="❌ Ошибка",
                    message=f"Не удалось добавить запись. Проверьте логи (db/db_app.log).",
                    timeout=5
                )

        btn_add.clicked.connect(on_add_clicked)

        # Показываем диалог
        dialog.exec()

    def delete_data(self):
        """Открывает модальное окно для удаления записей из выбранной таблицы с использованием DB.delete_data()."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Удаление данных")
        dialog.setModal(True)
        dialog.resize(500, 600)

        layout = QVBoxLayout(dialog)

        table_label = QLabel("Таблица:")
        table_combo = QComboBox()

        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц.",
                timeout=3
            )
            return

        table_combo.addItems(table_names)
        layout.addWidget(table_label)
        layout.addWidget(table_combo)

        fields_container = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_container)
        layout.addWidget(scroll_area)

        condition_widgets = {}

        def clear_fields():
            """Очищает все поля, удаляя и пересоздавая layout."""
            QWidget().setLayout(fields_container.layout())
            new_layout = QVBoxLayout(fields_container)
            fields_container.setLayout(new_layout)
            condition_widgets.clear()

        def load_table_fields(table_name: str):
            clear_fields()

            if table_name not in self.db_instance.tables:
                notification.notify(
                    title="Ошибка",
                    message=f"Метаданные для таблицы '{table_name}' не загружены.",
                    timeout=3
                )
                return

            table = self.db_instance.tables[table_name]
            current_layout = fields_container.layout()  # Получаем свежесозданный layout

            for column in table.columns:
                row_layout = QHBoxLayout()
                label = QLabel(f"{column.name}:")
                label.setMinimumWidth(150)
                row_layout.addWidget(label)

                widget = None

                if isinstance(column.type, SQLEnum):
                    widget = QComboBox()
                    widget.addItem("")
                    widget.addItems(column.type.enums)
                elif isinstance(column.type, ARRAY) and isinstance(column.type.item_type, String):
                    widget = QLineEdit()
                    widget.setPlaceholderText("Введите через запятую или оставьте пустым")
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

                row_layout.addWidget(widget)
                current_layout.addLayout(row_layout)  # ← Добавляем в актуальный layout
                condition_widgets[column.name] = widget

        load_table_fields(table_combo.currentText())
        table_combo.currentTextChanged.connect(load_table_fields)

        btn_delete = QPushButton("Удалить записи")
        layout.addWidget(btn_delete)
        def on_delete_clicked():
            table_name = table_combo.currentText()
            if not table_name:
                notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                return

            condition = {}
            table = self.db_instance.tables[table_name]

            for col_name, widget in condition_widgets.items():
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
                    if index > 0:  # пропускаем индекс 0 — "не задано"
                        condition[col_name] = widget.currentData()

                elif isinstance(widget, QDateEdit):
                    if widget.date().isValid() and widget.date().year() != 2000:
                        condition[col_name] = widget.date().toString("yyyy-MM-dd")

                elif isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if text:
                        if isinstance(column.type, Integer):
                            if not text.isdigit():
                                notification.notify(title="Ошибка",
                                                    message=f"Поле '{col_name}' должно быть целым числом.", timeout=3)
                                return
                            condition[col_name] = int(text)
                        elif isinstance(column.type, Numeric):
                            try:
                                condition[col_name] = float(text)
                            except ValueError:
                                notification.notify(title="Ошибка", message=f"Поле '{col_name}' должно быть числом.",
                                                    timeout=3)
                                return
                        else:
                            condition[col_name] = text

            # Если условий нет — предупреждаем, что удалим всё
            if not condition:
                reply = QMessageBox.warning(
                    dialog,
                    "Подтверждение",
                    f"Вы не указали ни одного условия. Это удалит ВСЕ записи из таблицы '{table_name}'.\nПродолжить?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            # Сначала делаем SELECT COUNT(*) для подсчёта затронутых записей
            try:
                # Формируем WHERE часть запроса с параметрами
                if condition:
                    where_clause = " AND ".join([f"{col} = :{col}" for col in condition.keys()])
                    count_query = f"SELECT COUNT(*) FROM \"{table_name}\" WHERE {where_clause}"
                else:
                    count_query = f"SELECT COUNT(*) FROM \"{table_name}\""

                # Используем execute_query для выполнения
                result = self.db_instance.execute_query(count_query, condition, fetch="one")

                if result is None:
                    count = 0
                else:
                    # Результат — кортеж (count,)
                    count = result[0] if isinstance(result, (tuple, list)) else result


                if count == 0:
                    notification.notify(
                        title="Информация",
                        message="Нет записей, удовлетворяющих условию.",
                        timeout=3
                    )
                    return

                # Подтверждение удаления
                reply = QMessageBox.warning(
                    dialog,
                    "Подтверждение удаления",
                    f"Будет удалено {count} записей из таблицы '{table_name}'.\nПродолжить?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Вызываем метод класса DB
                    success = self.db_instance.delete_data(table_name, condition)
                    if success:
                        notification.notify(
                            title="✅ Успех",
                            message=f"Удалено {count} записей из таблицы '{table_name}'.",
                            timeout=5
                        )
                        dialog.accept()
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

        btn_delete.clicked.connect(on_delete_clicked)

        # Показываем диалог
        dialog.exec()

    def on_header_clicked(self, logical_index: int):
        """
        Обрабатывает клик по заголовку столбца: сортирует данные через запрос к БД.
        Автоматически определяет числовые столбцы и применяет CAST к ним в SQL.
        Сортировка переключается между возрастанием и убыванием при повторных кликах.
        """
        if self.data_table.rowCount() == 0:
            return

        header_item = self.data_table.horizontalHeaderItem(logical_index)
        if header_item is None:
            return

        column_name = header_item.text()

        # Получаем текущий порядок сортировки для данного столбца
        current_order = self.sort_order.get(logical_index, Qt.AscendingOrder)
        new_order = Qt.DescendingOrder if current_order == Qt.AscendingOrder else Qt.AscendingOrder
        self.sort_order[logical_index] = new_order

        # Определяем SQL-порядок
        sql_order = "ASC" if new_order == Qt.AscendingOrder else "DESC"

        # --- 🚀 НОВЫЙ КОД: Автоматическое определение числового столбца ---
        def detect_numeric_column(col_index):
            """Проверяет, является ли столбец числовым, по данным в таблице."""
            if self.data_table.rowCount() == 0:
                return False
            for row in range(min(3, self.data_table.rowCount())):  # Проверяем первые 3 строки
                item = self.data_table.item(row, col_index)
                if not item or not item.text().strip():
                    continue
                text = item.text().strip().replace(',', '')  # Убираем тысячи
                try:
                    float(text)  # Успешно преобразуется → числовой
                    return True
                except ValueError:
                    pass
            return False

        # Запоминаем числовые столбцы в словаре, чтобы не пересчитывать каждый раз
        if not hasattr(self, '_numeric_columns_cache'):
            self._numeric_columns_cache = {}

        if logical_index not in self._numeric_columns_cache:
            self._numeric_columns_cache[logical_index] = detect_numeric_column(logical_index)

        is_numeric = self._numeric_columns_cache[logical_index]

        # --- Формируем имя столбца для SQL: если числовой — оборачиваем в CAST ---
        sql_column_for_order = column_name
        if is_numeric:
            # Для PostgreSQL: CAST(column AS NUMERIC)
            # Для SQLite: CAST(column AS REAL) или CAST(column AS INTEGER)
            # Используем NUMERIC — работает и там, и там
            sql_column_for_order = f"CAST({column_name} AS NUMERIC)"

        # --- Основная логика: JOIN или простая таблица ---
        try:
            if self.last_join_params:
                left_table, right_table, join_on = self.last_join_params
                data = self.db_instance.get_joined_summary(
                    left_table=left_table,
                    right_table=right_table,
                    join_on=join_on,
                    sort_columns=sql_column_for_order,  # ← ИСПОЛЬЗУЕМ CAST!
                    sort_order=sql_order
                )
                self._display_data_in_table(data, title=f"{left_table} ⨝ {right_table}",
                                            join_params=self.last_join_params)
            else:
                if self.last_table_name:
                    data = self.db_instance.get_table_data(
                        table_name=self.last_table_name,
                        sort_column=sql_column_for_order,  # ← ИСПОЛЬЗУЕМ CAST!
                        sort_order=sql_order
                    )
                    self._display_data_in_table(data, title=f"Таблица {self.last_table_name}",
                                                table_name=self.last_table_name)

            # Устанавливаем индикатор сортировки
            self.data_table.horizontalHeader().setSortIndicator(logical_index, new_order)
            self.data_table.horizontalHeader().setSortIndicatorShown(True)

        except Exception as e:
            notification.notify(
                title="Ошибка сортировки",
                message=f"Не удалось отсортировать столбец '{column_name}': {str(e)}",
                timeout=3
            )

    def show_table(self):
        """Открывает модальное окно выбора таблицы или JOIN-запроса."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        # Создаём модальное диалоговое окно
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор данных для отображения")
        dialog.setModal(True)
        dialog.resize(400, 200)

        layout = QVBoxLayout(dialog)

        # Группа радиокнопок
        radio_group = QButtonGroup(dialog)

        radio_single = QRadioButton("Обычная таблица")
        radio_join = QRadioButton("Сводная таблица (JOIN)")
        radio_single.setChecked(True)  # по умолчанию

        radio_group.addButton(radio_single)
        radio_group.addButton(radio_join)

        layout.addWidget(radio_single)
        layout.addWidget(radio_join)

        # Контейнеры для динамических виджетов
        single_container = QWidget()
        single_layout = QHBoxLayout(single_container)
        single_label = QLabel("Таблица:")
        single_combo = QComboBox()

        join_container = QWidget()
        join_layout = QHBoxLayout(join_container)
        join_label_left = QLabel("Левая таблица:")
        join_combo_left = QComboBox()
        join_label_right = QLabel("Правая таблица:")
        join_combo_right = QComboBox()

        # Заполняем комбобоксы списком таблиц
        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц из БД.",
                timeout=3
            )
            return

        single_combo.addItems(table_names)
        join_combo_left.addItems(table_names)
        join_combo_right.addItems(table_names)

        single_layout.addWidget(single_label)
        single_layout.addWidget(single_combo)
        single_container.setLayout(single_layout)

        join_layout.addWidget(join_label_left)
        join_layout.addWidget(join_combo_left)
        join_layout.addWidget(join_label_right)
        join_layout.addWidget(join_combo_right)
        join_container.setLayout(join_layout)

        # По умолчанию показываем только обычную таблицу
        layout.addWidget(single_container)
        join_container.setVisible(False)
        layout.addWidget(join_container)

        # Обработчик переключения радиокнопок
        def on_radio_toggled():
            is_join = radio_join.isChecked()
            single_container.setVisible(not is_join)
            join_container.setVisible(is_join)

        radio_single.toggled.connect(on_radio_toggled)
        radio_join.toggled.connect(on_radio_toggled)

        # Кнопка действия
        btn_execute = QPushButton("Загрузить")
        layout.addWidget(btn_execute)

        # Обработчик кнопки
        def on_execute_clicked():
            try:
                if radio_single.isChecked():
                    table_name = single_combo.currentText()
                    if not table_name:
                        notification.notify(
                            title="Внимание",
                            message="Выберите таблицу!",
                            timeout=3
                        )
                        return

                    data = self.db_instance.get_table_data(table_name)
                    if data is None:
                        notification.notify(
                            title="Ошибка",
                            message=f"Не удалось загрузить данные из таблицы '{table_name}'.",
                            timeout=3
                        )
                        return

                    self._display_data_in_table(data, table_name)
                    dialog.accept()

                elif radio_join.isChecked():
                    left_table = join_combo_left.currentText()
                    right_table = join_combo_right.currentText()

                    if not left_table or not right_table:
                        notification.notify(
                            title="Внимание",
                            message="Выберите обе таблицы!",
                            timeout=3
                        )
                        return

                    if left_table == right_table:
                        notification.notify(
                            title="Внимание",
                            message="Левая и правая таблицы должны быть разными!",
                            timeout=3
                        )
                        return

                    # Жёстко заданные связи на основе вашей схемы
                    predefined_joins = {
                        ("Issued_Books", "Books"): ("book_id", "id_book"),
                        ("Issued_Books", "Readers"): ("reader_id", "reader_id"),
                        ("Books", "Issued_Books"): ("id_book", "book_id"),  # обратный порядок
                        ("Readers", "Issued_Books"): ("reader_id", "reader_id"),
                    }

                    join_on = predefined_joins.get((left_table, right_table))

                    if join_on is None:
                        # Если не нашли в прямом порядке — пробуем поменять местами
                        join_on = predefined_joins.get((right_table, left_table))
                        if join_on:
                            # Если нашли в обратном порядке — меняем колонки местами
                            join_on = (join_on[1], join_on[0])

                    if join_on is None:
                        # Fallback: ищем первую общую колонку
                        left_cols = set(self.db_instance.get_column_names(left_table))
                        right_cols = set(self.db_instance.get_column_names(right_table))
                        common_cols = list(left_cols & right_cols)

                        if not common_cols:
                            notification.notify(
                                title="Ошибка",
                                message=f"Не найдено общих колонок и предопределённых связей для JOIN между '{left_table}' и '{right_table}'.",
                                timeout=3
                            )
                            return

                        notification.notify(
                            title="Информация",
                            message=f"Используется общая колонка '{common_cols[0]}' для JOIN (предопределённые связи не найдены).",
                            timeout=3
                        )
                        join_key = common_cols[0]
                        join_on = (join_key, join_key)

                    # Выполняем JOIN
                    joined_data = self.db_instance.get_joined_summary(
                        left_table=left_table,
                        right_table=right_table,
                        join_on=join_on,
                        columns=None,  # все колонки
                        condition=None,
                        sort_columns=None
                    )

                    if joined_data is None:
                        notification.notify(
                            title="Ошибка",
                            message=f"Не удалось выполнить JOIN-запрос.",
                            timeout=3
                        )
                        return

                    display_name = f"{left_table} ⨝ {right_table}"
                    self._display_data_in_table(joined_data, display_name)
                    dialog.accept()

            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Произошла ошибка при загрузке данных:\n{str(e)}",
                    timeout=3)

        btn_execute.clicked.connect(on_execute_clicked)

        # Показываем диалог
        dialog.exec()

    def _display_data_in_table(self, data: list, title: str = "Результат",table_name=None, join_params=None):
        """
        Отображает данные в self.data_table и сохраняет их для последующей сортировки.
        """
        self.current_table_data = data  # Сохраняем для сортировки
        self.current_table_data = data
        self.last_table_name = table_name
        self.last_join_params = join_params

        if not data:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Нет данных"])
            self.data_table.setVisible(True)
            return

        sample_row = data[0]
        column_headers = list(sample_row.keys())
        num_columns = len(column_headers)
        num_rows = len(data)

        self.data_table.setVisible(True)
        self.data_table.setRowCount(num_rows)
        self.data_table.setColumnCount(num_columns)
        self.data_table.setHorizontalHeaderLabels(column_headers)

        for row_idx, row_dict in enumerate(data):
            for col_idx, col_name in enumerate(column_headers):
                value = row_dict.get(col_name, "")
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.data_table.resizeColumnsToContents()

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите отключиться?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from main import DBConnectionWindow
            self.login_window = DBConnectionWindow()
            self.login_window.show()
            notification.notify(
                title="✅ Успешное отключение",
                message="Вы отключились от базы данных.")
            self.close()


