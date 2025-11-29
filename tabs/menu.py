from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QSizePolicy, QWidgetAction, QTableView,
    QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
    QHBoxLayout, QApplication, QMenu
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QStandardItem, QStandardItemModel, QPalette, QColor
from decimal import Decimal
from datetime import date
from plyer import notification
from tabs.modules.data_operations import AddRecordDialog, DeleteRecordDialog, EditRecordDialog, ShowTableDialog
from tabs.modules.table_operations import AddColumnDialog
from tabs.modules.custom_types import CustomTypesDialog


class MainWindow(QMainWindow):
    def __init__(self, db_instance=None):
        super().__init__()
        self.db_instance = db_instance
        self.setWindowTitle("СИСТЕМА УПРАВЛЕНИЯ БИБЛИОТЕКОЙ")
        self.setGeometry(200, 100, 1200, 800)
        """Устанавливаем тёмную палитру"""
        self.set_dark_palette()
        """Центральный виджет"""
        central_widget = QWidget()
        central_widget.setObjectName("mainWidget")
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        central_widget.setLayout(layout)
        """Заголовок приложения"""
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)
        title_label = QLabel("СИСТЕМА УПРАВЛЕНИЯ БИБЛИОТЕКОЙ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("subtitleLabel")
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_widget)
        self.setup_enhanced_toolbar()
        """Виджет статуса подключения"""
        self.setup_connection_status(layout)
        self.setup_data_table(layout)
        self.apply_styles()
        self.sort_order = {}
        self.current_table_data = []
        self.last_table_name = None
        self.last_join_params = None
        self.sort = {}
        """Словари для преобразования заголовков"""
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
            "reader_id": "ID Читателя (в выдаче)",
            "issue_date": "Дата выдачи",
            "expected_return_date": "Ожидаемая дата возврата",
            "actual_return_date": "Фактическая дата возврата",
            "damage_type": "Тип повреждения",
            "damage_fine": "Штраф за повреждение (₽)",
            "final_rental_cost": "Итоговая стоимость аренды (₽)",
            "paid": "Оплачено",
            "actual_rental_days": "Фактические дни аренды",
        }
        self.REVERSE_COLUMN_HEADERS_MAP = {display_name: db_name for db_name, display_name in
                                           self.COLUMN_HEADERS_MAP.items()}

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

    def setup_enhanced_toolbar(self):
        """Создает улучшенную панель инструментов"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(28, 28))
        toolbar.setMovable(False)
        toolbar.setMinimumHeight(70)
        self.addToolBar(toolbar)

        """Левая группа: операции с базой"""
        left_widget = QWidget()
        left_layout = QHBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 8, 15, 8)
        left_widget.setLayout(left_layout)

        btn_create_schema = self.create_toolbar_button("Создать схему", self.create_schema, "#0")
        left_layout.addWidget(btn_create_schema)

        btn_drop_schema = self.create_toolbar_button("Удалить схему", self.drop_schema, "#0")
        left_layout.addWidget(btn_drop_schema)

        toolbar.addWidget(left_widget)
        toolbar.addSeparator()

        """Центральная группа: операции с данными"""
        center_widget = QWidget()
        center_layout = QHBoxLayout()
        center_layout.setSpacing(8)
        center_layout.setContentsMargins(15, 8, 15, 8)
        center_widget.setLayout(center_layout)

        # === Выпадающая кнопка "Действия" ===
        actions_button = QPushButton("Действия")
        actions_menu = QMenu(actions_button)

        # Добавляем пункты меню
        actions_menu.addAction("Добавить", lambda: self.add_data())
        actions_menu.addAction("Изменить", lambda: self.edit_data())
        actions_menu.addAction("Удалить", lambda: self.delete_data())

        # Применяем стиль
        self.style_dropdown_button(actions_button, actions_menu)

        # Назначаем меню кнопке
        actions_button.setMenu(actions_menu)
        center_layout.addWidget(actions_button)

        # === Выпадающая кнопка "Поиск" ===
        search_button = QPushButton("Поиск")
        search_menu = QMenu(search_button)

        # Добавляем пункты меню поиска
        search_menu.addAction("Поиск по тексту", lambda: self.open_text_search())
        search_menu.addAction("Расширенный SELECT", lambda: self.open_advanced_select())
        search_menu.addAction("Строковые функции", lambda: self.open_string_functions())

        # Применяем стиль
        self.style_dropdown_button(search_button, search_menu)

        # Назначаем меню кнопке
        search_button.setMenu(search_menu)
        center_layout.addWidget(search_button)

        alter_menu_button = QPushButton("Структура")
        alter_menu_button.setMinimumHeight(45)
        alter_menu_button.setMinimumWidth(160)
        alter_menu_button.setCursor(Qt.PointingHandCursor)

        alter_menu = QMenu(alter_menu_button)
        alter_menu_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #0a0a0f, 
                                            stop: 1 #1a1a2e);
                border: 2px solid #64ffda60;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #1a1a2e,
                                            stop: 1 #2a2a3a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3bc1a8, 
                                            stop: 1 #00838f);
                color: #0a0a0f;
            }
        """)

        alter_menu = QMenu(alter_menu_button)
        alter_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(15, 15, 25, 0.95);
                color: #f8f8f2;
                border: 1px solid #64ffda80;
                border-radius: 10px;
                padding: 6px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
            }
        """)

        alter_menu.addAction("Добавить столбец", lambda: self.alter_table_action("add"))
        alter_menu.addAction("Удалить столбец", lambda: self.alter_table_action("drop"))
        alter_menu.addAction("Переименовать", lambda: self.alter_table_action("rename"))
        alter_menu.addAction("Изменить тип столбца", lambda: self.alter_table_action("type"))

        alter_menu_button.setMenu(alter_menu)
        center_layout.addWidget(alter_menu_button)
        
        # === Кнопка "Типы данных" ===
        types_button = QPushButton("Типы данных")
        types_button.setObjectName("typesButton")
        types_button.setMinimumHeight(45)
        types_button.setMinimumWidth(140)
        types_button.setCursor(Qt.PointingHandCursor)
        types_button.clicked.connect(self.open_custom_types)
        types_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #0a0a0f, 
                                            stop: 1 #1a1a2e);
                border: 2px solid #64ffda60;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #1a1a2e,
                                            stop: 1 #2a2a3a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3bc1a8, 
                                            stop: 1 #00838f);
                color: #0a0a0f;
            }
        """)
        center_layout.addWidget(types_button)
        
        toolbar.addWidget(center_widget)

        # Добавляем растягивающийся спейсер для правильного размещения кнопок
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer_action = QWidgetAction(toolbar)
        spacer_action.setDefaultWidget(spacer)
        toolbar.addAction(spacer_action)
        btn_show_table = self.create_toolbar_button("Показать таблицу", self.show_table, "#0")
        center_layout.addWidget(btn_show_table)

        """Правая группа: системные кнопки — только одна кнопка 'Отключиться'"""
        toolbar.addSeparator()
        right_widget = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(15, 8, 15, 8)
        right_widget.setLayout(right_layout)

        btn_logout = self.create_toolbar_button("Отключиться", self.logout, "#0")
        right_layout.addWidget(btn_logout)

        toolbar.addWidget(right_widget)

    def create_toolbar_button(self, text, callback, color):
        """Создает стилизованную кнопку для панели инструментов"""
        button = QPushButton(text)
        button.setMinimumHeight(45)
        button.setMinimumWidth(120)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {color}40, 
                                          stop: 0.5 {color}20,
                                          stop: 1 {color}10);
                border: 2px solid {color}60;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {color}60, 
                                          stop: 0.5 {color}40,
                                          stop: 1 {color}20);
                border: 2px solid {color};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {color}80, 
                                          stop: 0.5 {color}60,
                                          stop: 1 {color}40);
                padding: 7px 11px;
            }}
        """)
        return button

    def style_dropdown_button(self, button, menu):
        """Применяет единый неон-тёмный стиль к выпадающим кнопкам"""
        button.setMinimumHeight(45)
        button.setMinimumWidth(160)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #0a0a0f;
                border: 2px solid #5effa1;
                border-radius: 10px;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1a1a2e;
                border: 2px solid #00ff88;
                color: #00ff88;
            }
            QPushButton:pressed {
                background-color: #002b1a;
                border: 2px solid #00cc77;
                color: #aaffdd;
                padding: 7px 15px;
            }
        """)

        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(15, 15, 25, 0.95);
                color: #f8f8f2;
                border: 1px solid #00ff88;
                border-radius: 10px;
                padding: 6px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #00ff8840;
                color: #00ff88;
            }
        """)
    def setup_connection_status(self, layout):
        """Создает виджет статуса подключения"""
        status_widget = QWidget()
        status_widget.setObjectName("statusWidget")
        status_layout = QHBoxLayout()
        status_widget.setLayout(status_layout)
        status_icon = QLabel("[*]")
        status_icon.setObjectName("statusIcon")
        status_text = QLabel("Подключено к базе данных")
        status_text.setObjectName("statusText")
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        layout.addWidget(status_widget)

    def setup_data_table(self, layout):
        """Настраивает таблицу для отображения данных"""
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)
        """Заголовок таблицы"""
        table_header = QLabel("ДАННЫЕ БАЗЫ ДАННЫХ")
        table_header.setObjectName("tableHeader")
        table_header.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(table_header)
        """Таблица"""
        self.data_table = QTableView()
        self.data_table.setObjectName("dataTable")
        self.table_model = QStandardItemModel()
        self.data_table.setModel(self.table_model)
        """Настройки таблицы"""
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableView.NoEditTriggers)
        self.data_table.setSelectionBehavior(QTableView.SelectRows)
        self.data_table.setSortingEnabled(False)
        self.data_table.horizontalHeader().setSortIndicatorShown(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.data_table.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.data_table.setWordWrap(True)
        self.data_table.setVisible(False)
        self.data_table.verticalHeader().setDefaultSectionSize(40)
        self.data_table.verticalHeader().setMinimumSectionSize(30)
        table_layout.addWidget(self.data_table)
        layout.addWidget(table_container, 1)

        """Подключаем обработчик клика по заголовку"""
        self.data_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

    def apply_styles(self):
        """Применяет CSS стили"""
        self.setStyleSheet("""
            /* Основной виджет */
            #mainWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
            }

            /* Заголовок приложения */
            #headerWidget {
                background: rgba(10, 10, 15, 0.7);
                border-radius: 15px;
                border: 2px solid #64ffda;
                padding: 20px;
                margin-bottom: 10px;
            }

            #add_data {
                background: #000000;
            }

            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                letter-spacing: 2px;
                padding-top: 10px;
            }

            /* Панель инструментов */
            #mainToolbar {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 12px;
                spacing: 10px;
                margin: 10px 0;
            }

            /* Виджет статуса */
            #statusWidget {
               background: rgba(15, 15, 25, 0.8);
                border-radius: 8px;
                padding: 12px 20px;
                margin: 10px 0;
            }

            #statusIcon {
                font-size: 18px;
                color: #50fa7b;
                margin-right: 10px;
            }

            #statusText {
                font-size: 14px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-weight: bold;
            }

            /* Контейнер таблицы */
            #tableContainer {
                background: rgba(15, 15, 25, 0.6);
                border: 2px solid #44475a;
                border-radius: 15px;
                padding: 20px;
                margin-top: 10px;
            }

            #tableHeader {
                font-size: 18px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 20px;
                background: rgba(10, 10, 15, 0.5);
                border-radius: 8px;
                border: none;
            }

            /* Таблица */
            #dataTable {
                background: rgba(25, 25, 35, 0.8);
                border: 1px solid #44475a;
                border-radius: 8px;
                gridline-color: #44475a;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 16px;
            }

            #dataTable::item {
                padding: 8px;
                border-bottom: 1px solid #44475a40;
                color: #f8f8f2;
            }

            #dataTable::item:selected {
                background-color: #64ffda40;
                color: #0a0a0f;
            }

            #dataTable::item:alternate {
                background-color: rgba(40, 40, 50, 0.4);
            }

            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                color: #f8f8f2;
                padding: 12px;
                border: 1px solid #6272a4;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 11px;
            }

            QHeaderView::section:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #64ffda, 
                                          stop: 1 #50e3c2);
                color: #0a0a0f;
            }

            /* Стилизация QMessageBox */
            QMessageBox {
                background-color: #1a1a2e;
                color: #f8f8f2;
                border: 1px solid #44475a;
                border-radius: 8px;
            }

            QMessageBox QLabel {
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 1px solid #64ffda;
            }

            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
            }

            /* Скроллбары */
            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #64ffda;
                border-radius: 6px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background: #50e3c2;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                border: none;
                background: #1a1a2e;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #64ffda;
                border-radius: 6px;
                min-width: 25px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #50e3c2;
            }
        """)

    def create_schema(self):
        """Создаёт схему и таблицы в БД."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        success = self.db_instance.create_schema()

        if success:
            notification.notify(
                title="Успех",
                message="Схема успешно создана или уже существовала.",
                timeout=5
            )
        else:
            notification.notify(
                title="Ошибка",
                message="Не удалось создать схему. Проверьте логи (db/db_app.log).",
                timeout=5
            )

    def drop_schema(self):
        """Удаляет схему и все таблицы из БД."""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        # Стилизованный QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение удаления")
        msg.setText("Вы уверены, что хотите УДАЛИТЬ ВСЮ СХЕМУ и ВСЕ ДАННЫЕ?\nЭто действие необратимо!")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        # Применяем стили
        msg.setStyleSheet(self.styleSheet())
        reply = msg.exec()

        if reply != QMessageBox.Yes:
            return

        success = self.db_instance.drop_schema()

        if success:
            notification.notify(
                title="Схема удалена",
                message="Схема успешно удалена из базы данных.",
                timeout=5
            )
            self.data_table.setVisible(False)
            self.current_table_data = []
        else:
            notification.notify(
                title="Ошибка",
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
        if self.data_table.model().rowCount() == 0:
            return

        header_item = self.data_table.model().horizontalHeaderItem(logical_index)
        if header_item is None:
            return

        display_name = header_item.text()
        original_column_name = self.REVERSE_COLUMN_HEADERS_MAP.get(display_name, display_name)

        if not hasattr(self, 'sort') or not isinstance(self.sort, dict):
            return

        current_sort_columns = self.sort.get('sort_columns', [])
        if not isinstance(current_sort_columns, list) or len(current_sort_columns) == 0:
            new_sort_columns = [(original_column_name, True)]
        else:
            current_col, current_order = current_sort_columns[0]

            if current_col == original_column_name:
                new_sort_columns = [(original_column_name, not current_order)]
            else:
                new_sort_columns = [(original_column_name, True)]

        self.sort['sort_columns'] = new_sort_columns
        self._display_data_in_table()

    def show_table(self):
        dialog = ShowTableDialog(self.db_instance, parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.result:
            self.sort = dialog.result
            self._display_data_in_table()
            
    def open_text_search(self):
        """Открывает диалоговое окно поиска по тексту"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
            
        from tabs.modules.search_operations import TextSearchDialog
        dialog = TextSearchDialog(self.db_instance, parent=self)
        dialog.exec()
        
    def open_advanced_select(self):
        """Открывает диалоговое окно расширенного SELECT"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
            
        from tabs.modules.search_operations import AdvancedSelectDialog
        dialog = AdvancedSelectDialog(self.db_instance, parent=self)
        dialog.results_to_main_table.connect(self.display_advanced_select_results)
        dialog.exec()
        
    def open_string_functions(self):
        """Открывает диалоговое окно строковых функций"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
            
        from tabs.modules.string_operations import StringFunctionsDialog
        dialog = StringFunctionsDialog(self.db_instance, parent=self)
        dialog.exec()
    
    def open_custom_types(self):
        """Открывает диалоговое окно управления пользовательскими типами"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return
        
        dialog = CustomTypesDialog(self.db_instance, parent=self)
        dialog.exec()
        
    def display_advanced_select_results(self, results):
        """Отображает результаты расширенного SELECT в основной таблице"""
        if not results:
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Нет данных"])
            self.data_table.setVisible(True)
            return
            
        # Получаем заголовки столбцов
        if results and isinstance(results[0], dict):
            original_headers = list(results[0].keys())
        else:
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Неверный формат результатов"])
            self.data_table.setVisible(True)
            return
            
        # Преобразуем заголовки
        column_headers = [
            self.COLUMN_HEADERS_MAP.get(col, col)
            for col in original_headers
        ]
        
        # Очищаем и настраиваем таблицу
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(column_headers)
        
        # Заполняем данные
        for row_dict in results:
            row_items = []
            for col_name in original_headers:
                value = row_dict.get(col_name, "")
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                elif isinstance(value, (int, float, Decimal)):
                    value = f"{value:.2f}" if isinstance(value, (float, Decimal)) else str(value)
                elif isinstance(value, date):
                    value = value.strftime("%Y-%m-%d")
                elif hasattr(value, 'isoformat'):  # datetime/date
                    value = value.isoformat()
                elif value is None:
                    value = ""
                else:
                    value = str(value)
                item = QStandardItem(value)
                item.setEditable(False)
                row_items.append(item)
            self.table_model.appendRow(row_items)
            
        # Настраиваем таблицу
        self.data_table.setVisible(True)
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        # Сохраняем данные для возможного использования
        self.current_table_data = results
        
        # Показываем уведомление
        notification.notify(
            title="Результаты загружены",
            message=f"Найдено {len(results)} записей",
            timeout=3
        )

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

            # Получаем выбранные пользователем столбцы (если ShowTableDialog их вернул)
            selected_columns = self.sort.get('columns')
            data = self.db_instance.get_sorted_data(
                table_name=table_name,
                sort_columns=sort_columns,
                columns=selected_columns
            )
            self.current_table_data = data
        elif mode == 'join':
            left_table = self.sort.get('left_table')
            right_table = self.sort.get('right_table')
            join_on = self.sort.get('join_on')
            join_type = self.sort.get('join_type', 'INNER')  # Получаем тип соединения, по умолчанию INNER
            columns = self.sort.get('columns')
            sort_columns = self.sort.get('sort_columns')
            if not all([left_table, right_table, join_on, columns, sort_columns]):
                self.table_model.clear()
                self.table_model.setHorizontalHeaderLabels(["Ошибка: недостаточно параметров для join-запроса"])
                self.data_table.setVisible(True)
                return
            data = self.db_instance.get_joined_summary(
                left_table=left_table,
                right_table=right_table,
                join_on=join_on,
                join_type=join_type,  # Передаём тип соединения
                columns=columns,
                sort_columns=sort_columns
            )
            self.current_table_data = data
        else:
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(["Неизвестный режим отображения"])
            self.data_table.setVisible(True)
            return

        # Отрисовка данных
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

        original_headers = list(sample_row.keys())
        column_headers = [
            self.COLUMN_HEADERS_MAP.get(col, col)
            for col in original_headers
        ]

        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(column_headers)

        for row_dict in self.current_table_data:
            row_items = []
            for col_name in original_headers:
                value = row_dict.get(col_name, "")
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

        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSortingEnabled(False)
        self.data_table.setVisible(True)

        sort_col_index = -1
        sort_order = Qt.AscendingOrder

        if self.sort and isinstance(self.sort, dict):
            sort_columns = self.sort.get('sort_columns', [])
            if sort_columns and isinstance(sort_columns, list) and len(sort_columns) > 0:
                sort_col_name, is_asc = sort_columns[0]

                for i, col in enumerate(original_headers):
                    if col == sort_col_name:
                        sort_col_index = i
                        break

                if sort_col_index == -1 and '.' in sort_col_name:
                    clean_name = sort_col_name.split('.', 1)[1]
                    for i, col in enumerate(original_headers):
                        if col == clean_name:
                            sort_col_index = i
                            break

                sort_order = Qt.AscendingOrder if is_asc else Qt.DescendingOrder

        self.data_table.horizontalHeader().setSortIndicator(sort_col_index, sort_order)

    def alter_table_action(self, action_type):
        """Обрабатывает действия из выпадающего списка ALTER TABLE"""
        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка подключения",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            return

        if action_type == "add":
            dialog = AddColumnDialog(self.db_instance, parent=self)
            if dialog.exec() == QDialog.Accepted:
                # Если столбец успешно добавлен, обновляем данные таблицы, если она открыта
                if hasattr(self, 'sort') and self.sort:
                    self._display_data_in_table()
            return
        
        elif action_type == "rename":
            from tabs.modules.table_operations import RenameDialog
            dialog = RenameDialog(self.db_instance, parent=self)
            if dialog.exec() == QDialog.Accepted:
                # Если столбец или таблица успешно переименованы, обновляем данные таблицы, если она открыта
                if hasattr(self, 'sort') and self.sort:
                    self._display_data_in_table()
            return

        # Реализация для удаления столбца
        if action_type == "drop":
            from tabs.modules.table_operations import DropColumnDialog
            dialog = DropColumnDialog(self.db_instance, parent=self)
            if dialog.exec() == QDialog.Accepted:
                if hasattr(self, 'sort') and self.sort:
                    self._display_data_in_table()
            return

        # Здесь реализуем изменение типа столбца
        if action_type == "type":
            from tabs.modules.table_operations import ChangeTypeDialog
            dialog = ChangeTypeDialog(self.db_instance, parent=self)
            if dialog.exec() == QDialog.Accepted:
                if hasattr(self, 'sort') and self.sort:
                    self._display_data_in_table()
            return
        # Здесь можно будет добавить реализацию для других действий
        action_texts = {
            "type": "Изменение типа столбца"
        }

        dialog = QDialog(self)
        dialog.setWindowTitle(f"ALTER TABLE — {action_texts.get(action_type, 'Действие')}")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(f"Вы выбрали: {action_texts.get(action_type, 'Неизвестное действие')}")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        info = QLabel("Эта функция пока не реализована.")
        info.setWordWrap(True)
        layout.addWidget(info)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        # Применяем стили для соответствия главному окну
        dialog.setStyleSheet(self.styleSheet())

        dialog.exec()

    def logout(self):
        # Стилизованный QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText("Вы действительно хотите отключиться?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        # Применяем стили
        msg.setStyleSheet(self.styleSheet())
        reply = msg.exec()

        if reply == QMessageBox.Yes:
            from main import DBConnectionWindow
            self.login_window = DBConnectionWindow()
            self.login_window.show()
            notification.notify(
                title="Успешное отключение",
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