from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QSizePolicy, QWidgetAction, QTableView,
    QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QStandardItem, QStandardItemModel
from decimal import Decimal
from datetime import date
from plyer import notification
# Импорты из локальных модулей (предполагается, что структура проекта такая)
from tabs.add_dialog import AddRecordDialog
from tabs.delete_dialog import DeleteRecordDialog
from tabs.update_dialog import EditRecordDialog
from tabs.get_table import ShowTableDialog


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
        self.data_table = QTableView()
        self.table_model = QStandardItemModel()  # ← Создаём модель
        self.data_table.setModel(self.table_model)
        self.data_table.setAlternatingRowColors(True)  # Альтернативные строки
        self.data_table.setEditTriggers(QTableView.NoEditTriggers)  # Только чтение
        self.data_table.setSelectionBehavior(QTableView.SelectRows)  # Выбор строк
        self.data_table.setSortingEnabled(False)  # Включаем сортировку
        self.data_table.horizontalHeader().setSortIndicatorShown(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)  # Последний столбец растягивается
        self.data_table.setVerticalScrollMode(QTableView.ScrollPerPixel)  # Плавная прокрутка
        self.data_table.setHorizontalScrollMode(QTableView.ScrollPerPixel)
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
        self.sort = {}
        self.COLUMN_HEADERS_MAP = {
            # === Книги ===
            "book_id": "ID Книги (в выдаче)",
            "title": "Название книги (Books)",
            "authors": "Авторы (массив)",
            "genre": "Жанр книги",
            "deposit_amount": "Залог (₽)",
            "daily_rental_rate": "Цена аренды в день (₽)",

            # === Читатели ===
            "reader_id": "ID Читателя",
            "first_name": "Имя читателя",
            "middle_name": "Отчество читателя",
            "last_name": "Фамилия читателя",
            "address": "Адрес читателя",
            "phone": "Телефон читателя",
            "discount_category": "Категория скидки",
            "discount_percent": "Процент скидки (%)",

            # === Выдачи ===
            "id_book": "ID Книги",
            "reader_id=": "ID Читателя (в выдаче)",  # ← ИЗМЕНЁНО! Уникальное имя
            "issue_date": "Дата выдачи",
            "expected_return_date": "Ожидаемая дата возврата",
            "actual_return_date": "Фактическая дата возврата",
            "damage_type": "Тип повреждения",
            "damage_fine": "Штраф за повреждение (₽)",
            "final_rental_cost": "Итоговая стоимость аренды (₽)",
            "paid": "Оплачено",
            "actual_rental_days": "Фактические дни аренды",

            # === JOIN-поля (если используешь их в других местах) ===
            # "book_title": "Название книги (из JOIN)",
            # "reader_name": "Полное имя читателя (из JOIN)",
            # "author": "Автор (из JOIN)",
        }

        self.REVERSE_COLUMN_HEADERS_MAP = {display_name: db_name for db_name, display_name in
                                           self.COLUMN_HEADERS_MAP.items()}
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
        dialog = EditRecordDialog(self.db_instance, self.COLUMN_HEADERS_MAP, self.REVERSE_COLUMN_HEADERS_MAP,
                                  parent=self)
        dialog.exec()
        self._display_data_in_table()

    def add_data(self):
        dialog = AddRecordDialog(self.db_instance, self.COLUMN_HEADERS_MAP, self.REVERSE_COLUMN_HEADERS_MAP, self)
        dialog.exec()
        self._display_data_in_table()

    def delete_data(self):
        dialog = DeleteRecordDialog(self.db_instance, self.COLUMN_HEADERS_MAP, self.REVERSE_COLUMN_HEADERS_MAP,
                                    parent=self)
        dialog.exec()
        self._display_data_in_table()

    def on_header_clicked(self, logical_index: int):
        """
        Обрабатывает клик по заголовку столбца: меняет параметр сортировки в self.sort и перезагружает данные.
        """
        # Проверяем, есть ли данные и заголовок
        if self.data_table.model().rowCount() == 0:
            return

        header_item = self.data_table.model().horizontalHeaderItem(logical_index)
        if header_item is None:
            return

        display_name = header_item.text()
        original_column_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)

        # Проверяем, есть ли self.sort и режим
        if not hasattr(self, 'sort') or not isinstance(self.sort, dict):
            return

        current_sort_columns = self.sort.get('sort_columns', [])
        if not isinstance(current_sort_columns, list) or len(current_sort_columns) == 0:
            # Если сортировка не задана — устанавливаем по умолчанию по кликнутому столбцу по возрастанию
            new_sort_columns = [(original_column_name, True)]
        else:
            current_col, current_order = current_sort_columns[
                0]  # Берём первый (и пока единственный) столбец сортировки

            if current_col == original_column_name:
                # Клик по тому же столбцу — инвертируем порядок
                new_sort_columns = [(original_column_name, not current_order)]
            else:
                # Клик по другому столбцу — сортируем по нему по возрастанию
                new_sort_columns = [(original_column_name, True)]

        # Обновляем параметр сортировки
        self.sort['sort_columns'] = new_sort_columns

        # Перезагружаем данные с новой сортировкой
        self._display_data_in_table()

    def show_table(self):
        dialog = ShowTableDialog(self.db_instance, parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.result:
            self.sort = dialog.result
            self._display_data_in_table()

    def _display_data_in_table(self):
        """
        Выполняет запрос на основе self.sort и отображает результат в self.data_table через QStandardItemModel.
        """
        if not hasattr(self, 'sort') or not isinstance(self.sort, dict):
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Ошибка: параметры запроса не заданы"])
            self.data_table.setVisible(True)
            self.data_table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            return

        mode = self.sort.get('mode')

        if mode == 'single':
            table_name = self.sort.get('table_name')
            sort_columns = self.sort.get('sort_columns')

            if not table_name or not sort_columns:
                self.table_model.clear()
                self.table_model.setHorizontalHeaderLabels(["Ошибка: недостаточно параметров для single-запроса"])
                self.data_table.setVisible(True)
                return

            # Выполняем запрос
            data = self.db_instance.get_sorted_data(
                table_name=table_name,
                sort_columns=sort_columns
            )
            self.current_table_data = data

        elif mode == 'join':
            left_table = self.sort.get('left_table')
            right_table = self.sort.get('right_table')
            join_on = self.sort.get('join_on')
            columns = self.sort.get('columns')
            sort_columns = self.sort.get('sort_columns')

            if not all([left_table, right_table, join_on, columns, sort_columns]):
                self.table_model.clear()
                self.table_model.setHorizontalHeaderLabels(["Ошибка: недостаточно параметров для join-запроса"])
                self.data_table.setVisible(True)
                return

            # Выполняем JOIN-запрос
            data = self.db_instance.get_joined_summary(
                left_table=left_table,
                right_table=right_table,
                join_on=join_on,
                columns=columns,
                sort_columns=sort_columns
            )
            self.current_table_data = data

        else:
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Неизвестный режим отображения"])
            self.data_table.setVisible(True)
            return

        # --- ОТРИСОВКА ДАННЫХ ЧЕРЕЗ QStandardItemModel ---
        if not self.current_table_data or not isinstance(self.current_table_data, list) or len(
                self.current_table_data) == 0:
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Нет данных"])
            self.data_table.setVisible(True)
            self.data_table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            return

        sample_row = self.current_table_data[0]
        if not isinstance(sample_row, dict):
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Ошибка: данные не в формате словаря"])
            self.data_table.setVisible(True)
            return

        # Получаем оригинальные имена столбцов
        original_headers = list(sample_row.keys())

        # Преобразуем в отображаемые имена
        column_headers = [
            self.COLUMN_HEADERS_MAP.get(col, col)
            for col in original_headers
        ]

        # Очищаем модель и устанавливаем заголовки
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(column_headers)

        # Заполняем строки
        for row_dict in self.current_table_data:
            row_items = []
            for col_name in original_headers:
                value = row_dict.get(col_name, "")
                # Форматирование значений
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                elif isinstance(value, (int, float, Decimal)):
                    value = f"{value:.2f}" if isinstance(value, (float, Decimal)) else str(value)
                elif isinstance(value, date):
                    value = value.strftime("%Y-%m-%d")
                elif value is None:
                    value = ""
                else:
                    value = str(value)
                item = QStandardItem(value)
                item.setEditable(False)
                row_items.append(item)
            self.table_model.appendRow(row_items)

        # Настройка отображения
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSortingEnabled(False)
        self.data_table.setVisible(True)

        # 🔥 Устанавливаем индикатор сортировки на основе self.sort
        sort_col_index = -1
        sort_order = Qt.AscendingOrder

        if self.sort and isinstance(self.sort, dict):
            sort_columns = self.sort.get('sort_columns', [])
            if sort_columns and isinstance(sort_columns, list) and len(sort_columns) > 0:
                sort_col_name, is_asc = sort_columns[0]  # Берём первый столбец сортировки

                # Ищем столбец в original_headers
                for i, col in enumerate(original_headers):
                    if col == sort_col_name:
                        sort_col_index = i
                        break

                # Если не нашли — пробуем очистить от алиаса t1./t2.
                if sort_col_index == -1 and '.' in sort_col_name:
                    clean_name = sort_col_name.split('.', 1)[1]  # "t1.id_book" → "id_book"
                    for i, col in enumerate(original_headers):
                        if col == clean_name:
                            sort_col_index = i
                            break

                sort_order = Qt.AscendingOrder if is_asc else Qt.DescendingOrder

        self.data_table.horizontalHeader().setSortIndicator(sort_col_index, sort_order)

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

    def closeEvent(self, event):
        if hasattr(self, 'db_instance') and self.db_instance:
            try:
                self.db_instance.disconnect()
                notification.notify(
                    title="Информация",
                    message="Отключение от базы данных выполнено.",
                    timeout=5
                )
            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка при отключении от базы данных: {e}",
                    timeout=5
                )
        event.accept()
