"""
Диалог для работы с представлениями (VIEW) в базе данных PostgreSQL
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea, QListWidget, QListWidgetItem, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification


class ViewsDialog(QDialog):
    """Диалог для управления представлениями (VIEW)"""
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Управление представлениями (VIEW)")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.resize(900, 700)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("УПРАВЛЕНИЕ ПРЕДСТАВЛЕНИЯМИ (VIEW)")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Вкладка создания представления
        create_tab = self.create_view_tab()
        tab_widget.addTab(create_tab, "Создать VIEW")
        
        # Вкладка управления представлениями
        manage_tab = self.manage_views_tab()
        tab_widget.addTab(manage_tab, "Управление VIEW")
        
        main_layout.addWidget(tab_widget)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)
        
        self.apply_styles()
        
    def set_dark_palette(self):
        """Устанавливает тёмную цветовую палитру"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)
        
    def create_view_tab(self):
        """Создает вкладку для создания нового представления"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Группа настроек представления
        settings_group = QGroupBox("Настройки представления")
        settings_layout = QFormLayout()
        settings_group.setLayout(settings_layout)
        
        # Имя представления
        self.view_name_input = QLineEdit()
        self.view_name_input.setPlaceholderText("Введите имя представления (например: v_active_readers)")
        settings_layout.addRow("Имя VIEW:", self.view_name_input)
        
        # Выбор базовой таблицы
        self.base_table_combo = QComboBox()
        self.base_table_combo.currentTextChanged.connect(self.on_base_table_changed)
        settings_layout.addRow("Базовая таблица:", self.base_table_combo)
        
        layout.addWidget(settings_group)
        
        # Группа выбора столбцов
        columns_group = QGroupBox("Выбор столбцов")
        columns_layout = QVBoxLayout()
        columns_group.setLayout(columns_layout)
        
        # Список доступных столбцов
        columns_layout.addWidget(QLabel("Доступные столбцы:"))
        self.available_view_columns = QListWidget()
        self.available_view_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(self.available_view_columns)
        
        # Кнопки управления столбцами
        columns_buttons = QHBoxLayout()
        add_col_btn = QPushButton(">> Добавить")
        add_col_btn.clicked.connect(self.add_view_columns)
        add_all_col_btn = QPushButton(">>> Все")
        add_all_col_btn.clicked.connect(self.add_all_view_columns)
        columns_buttons.addWidget(add_col_btn)
        columns_buttons.addWidget(add_all_col_btn)
        columns_layout.addLayout(columns_buttons)
        
        # Выбранные столбцы
        columns_layout.addWidget(QLabel("Выбранные столбцы:"))
        self.selected_view_columns = QListWidget()
        self.selected_view_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(self.selected_view_columns)
        
        # Кнопки удаления
        remove_buttons = QHBoxLayout()
        remove_col_btn = QPushButton("<< Удалить")
        remove_col_btn.clicked.connect(self.remove_view_columns)
        remove_all_col_btn = QPushButton("<<< Все")
        remove_all_col_btn.clicked.connect(self.remove_all_view_columns)
        remove_buttons.addWidget(remove_col_btn)
        remove_buttons.addWidget(remove_all_col_btn)
        columns_layout.addLayout(remove_buttons)
        
        layout.addWidget(columns_group)
        
        # Группа условий WHERE
        where_group = QGroupBox("Условие WHERE (опционально)")
        where_layout = QVBoxLayout()
        where_group.setLayout(where_layout)
        
        self.view_where_input = QLineEdit()
        self.view_where_input.setPlaceholderText("Например: discount_percent > 0")
        where_layout.addWidget(self.view_where_input)
        
        layout.addWidget(where_group)
        
        # Кнопка создания
        create_button = QPushButton("Создать VIEW")
        create_button.setObjectName("createButton")
        create_button.clicked.connect(self.create_view)
        layout.addWidget(create_button)
        
        # Заполняем список таблиц
        self.populate_tables_for_view()
        
        return tab
        
    def manage_views_tab(self):
        """Создает вкладку для управления существующими представлениями"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Группа списка представлений
        views_list_group = QGroupBox("Существующие представления")
        views_list_layout = QVBoxLayout()
        views_list_group.setLayout(views_list_layout)
        
        # Кнопка обновления списка
        refresh_btn = QPushButton("Обновить список")
        refresh_btn.clicked.connect(self.refresh_views_list)
        views_list_layout.addWidget(refresh_btn)
        
        # Список представлений
        self.views_list = QListWidget()
        self.views_list.itemClicked.connect(self.on_view_selected)
        views_list_layout.addWidget(self.views_list)
        
        layout.addWidget(views_list_group)
        
        # Группа информации о представлении
        view_info_group = QGroupBox("Информация о представлении")
        view_info_layout = QVBoxLayout()
        view_info_group.setLayout(view_info_layout)
        
        # Определение представления (SQL)
        view_info_layout.addWidget(QLabel("SQL определение:"))
        self.view_definition_text = QTextEdit()
        self.view_definition_text.setReadOnly(True)
        self.view_definition_text.setMaximumHeight(150)
        view_info_layout.addWidget(self.view_definition_text)
        
        layout.addWidget(view_info_group)
        
        # Группа данных представления
        view_data_group = QGroupBox("Данные представления")
        view_data_layout = QVBoxLayout()
        view_data_group.setLayout(view_data_layout)
        
        # Таблица данных
        self.view_data_table = QTableWidget()
        self.view_data_table.setAlternatingRowColors(True)
        view_data_layout.addWidget(self.view_data_table)
        
        layout.addWidget(view_data_group)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        show_data_btn = QPushButton("Показать данные")
        show_data_btn.clicked.connect(self.show_view_data)
        
        delete_view_btn = QPushButton("Удалить VIEW")
        delete_view_btn.setObjectName("deleteButton")
        delete_view_btn.clicked.connect(self.delete_view)
        
        actions_layout.addWidget(show_data_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(delete_view_btn)
        layout.addLayout(actions_layout)
        
        # Загружаем список представлений
        self.refresh_views_list()
        
        return tab
        
    def populate_tables_for_view(self):
        """Заполняет список таблиц для выбора"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            tables = self.db_instance.get_tables()
            self.base_table_combo.clear()
            self.base_table_combo.addItems(tables)
            
        except Exception as e:
            self.show_error(f"Ошибка при получении списка таблиц: {e}")
            
    def on_base_table_changed(self, table_name):
        """Обработчик изменения базовой таблицы"""
        try:
            if not table_name or not self.db_instance:
                return
                
            columns = self.db_instance.get_table_columns(table_name)
            self.available_view_columns.clear()
            self.selected_view_columns.clear()
            self.available_view_columns.addItems(columns)
            
        except Exception as e:
            self.show_error(f"Ошибка при получении столбцов: {e}")
            
    def add_view_columns(self):
        """Добавляет выбранные столбцы"""
        selected_items = self.available_view_columns.selectedItems()
        for item in selected_items:
            if not self.selected_view_columns.findItems(item.text(), Qt.MatchExactly):
                self.selected_view_columns.addItem(item.text())
                
    def add_all_view_columns(self):
        """Добавляет все столбцы"""
        self.selected_view_columns.clear()
        for i in range(self.available_view_columns.count()):
            self.selected_view_columns.addItem(self.available_view_columns.item(i).text())
            
    def remove_view_columns(self):
        """Удаляет выбранные столбцы"""
        selected_items = self.selected_view_columns.selectedItems()
        for item in selected_items:
            self.selected_view_columns.takeItem(self.selected_view_columns.row(item))
            
    def remove_all_view_columns(self):
        """Удаляет все столбцы"""
        self.selected_view_columns.clear()
    
    def validate_identifier(self, name):
        """Валидирует SQL идентификатор (имя таблицы, представления и т.д.)"""
        if not name:
            return False
        # SQL идентификаторы должны начинаться с буквы или подчеркивания
        if not (name[0].isalpha() or name[0] == '_'):
            return False
        # Разрешаем только буквы, цифры и подчеркивания
        return name.replace('_', '').isalnum() and len(name) <= 63
    
    def validate_where_clause(self, where_clause):
        """Базовая валидация WHERE условия для защиты от SQL инъекций"""
        if not where_clause:
            return True, ""
        
        # Запрещенные ключевые слова
        dangerous_patterns = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE',
            'EXEC', 'EXECUTE', '--', '/*', '*/', ';'
        ]
        
        upper_clause = where_clause.upper()
        for pattern in dangerous_patterns:
            if pattern in upper_clause:
                return False, f"Запрещенное ключевое слово: {pattern}"
        
        # Проверяем сбалансированность скобок
        if where_clause.count('(') != where_clause.count(')'):
            return False, "Несбалансированные скобки"
        
        # Проверяем сбалансированность кавычек
        if where_clause.count("'") % 2 != 0:
            return False, "Незакрытые кавычки"
        
        return True, ""
        
    def create_view(self):
        """Создает новое представление"""
        try:
            view_name = self.view_name_input.text().strip()
            if not view_name:
                self.show_error("Введите имя представления")
                return
                
            # Валидация имени представления
            if not self.validate_identifier(view_name):
                self.show_error("Имя представления может содержать только буквы, цифры и подчеркивания (макс. 63 символа)")
                return
                
            table_name = self.base_table_combo.currentText()
            if not table_name:
                self.show_error("Выберите базовую таблицу")
                return
            
            # Валидируем имя таблицы (должно быть из списка существующих таблиц)
            available_tables = self.db_instance.get_tables()
            if table_name not in available_tables:
                self.show_error("Выбранная таблица не существует")
                return
                
            # Собираем столбцы (столбцы из списка, предварительно валидированы)
            columns = []
            for i in range(self.selected_view_columns.count()):
                col_name = self.selected_view_columns.item(i).text()
                # Столбцы берутся из таблицы, но дополнительно проверяем
                if self.validate_identifier(col_name):
                    columns.append(f'"{col_name}"')
                    
            if not columns:
                columns = ["*"]
                
            # Формируем SQL запрос
            select_clause = ", ".join(columns)
            where_clause = self.view_where_input.text().strip()
            
            # Валидируем WHERE условие
            is_valid, error_msg = self.validate_where_clause(where_clause)
            if not is_valid:
                self.show_error(f"Ошибка в WHERE условии: {error_msg}")
                return
            
            sql = f'CREATE VIEW "{view_name}" AS SELECT {select_clause} FROM "{table_name}"'
            if where_clause:
                sql += f" WHERE {where_clause}"
                
            # Выполняем запрос
            success = self.db_instance.execute_ddl(sql)
            
            if success:
                self.show_info(f"Представление '{view_name}' успешно создано!")
                self.view_name_input.clear()
                self.view_where_input.clear()
                self.refresh_views_list()
            else:
                self.show_error("Не удалось создать представление")
                
        except Exception as e:
            self.show_error(f"Ошибка при создании представления: {e}")
            
    def refresh_views_list(self):
        """Обновляет список представлений"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            # Запрос для получения списка представлений
            sql = """
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            
            results = self.db_instance.execute_custom_query(sql)
            
            self.views_list.clear()
            for row in results:
                view_name = row.get('table_name', '')
                if view_name:
                    self.views_list.addItem(view_name)
                    
        except Exception as e:
            self.show_error(f"Ошибка при получении списка представлений: {e}")
            
    def on_view_selected(self, item):
        """Обработчик выбора представления"""
        try:
            view_name = item.text()
            
            # Валидируем имя представления
            if not self.validate_identifier(view_name):
                self.view_definition_text.setPlainText("Ошибка: некорректное имя представления")
                return
            
            # Используем безопасный способ получения определения через регулярную переменную
            # pg_get_viewdef принимает имя представления безопасно
            sql = f"""
                SELECT pg_get_viewdef(c.oid, true) as definition
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind = 'v' AND n.nspname = 'public' AND c.relname = '{view_name.replace("'", "''")}'
            """
            
            results = self.db_instance.execute_custom_query(sql)
            
            if results:
                definition = results[0].get('definition', '')
                self.view_definition_text.setPlainText(definition)
            else:
                self.view_definition_text.setPlainText("Не удалось получить определение")
                
        except Exception as e:
            self.view_definition_text.setPlainText(f"Ошибка: {e}")
            
    def show_view_data(self):
        """Показывает данные выбранного представления"""
        try:
            selected_item = self.views_list.currentItem()
            if not selected_item:
                self.show_error("Выберите представление из списка")
                return
                
            view_name = selected_item.text()
            
            # Валидируем имя представления
            if not self.validate_identifier(view_name):
                self.show_error("Некорректное имя представления")
                return
            
            # Получаем данные из представления
            sql = f'SELECT * FROM "{view_name}" LIMIT 100'
            results = self.db_instance.execute_custom_query(sql)
            
            if not results:
                self.view_data_table.setRowCount(0)
                self.view_data_table.setColumnCount(1)
                self.view_data_table.setHorizontalHeaderLabels(["Нет данных"])
                return
                
            # Заполняем таблицу
            columns = list(results[0].keys())
            self.view_data_table.setColumnCount(len(columns))
            self.view_data_table.setHorizontalHeaderLabels(columns)
            self.view_data_table.setRowCount(len(results))
            
            for row_idx, row in enumerate(results):
                for col_idx, col in enumerate(columns):
                    value = row.get(col, "")
                    if value is None:
                        value = "NULL"
                    self.view_data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                    
            self.view_data_table.resizeColumnsToContents()
            
        except Exception as e:
            self.show_error(f"Ошибка при получении данных: {e}")
            
    def delete_view(self):
        """Удаляет выбранное представление"""
        try:
            selected_item = self.views_list.currentItem()
            if not selected_item:
                self.show_error("Выберите представление для удаления")
                return
                
            view_name = selected_item.text()
            
            # Валидируем имя представления
            if not self.validate_identifier(view_name):
                self.show_error("Некорректное имя представления")
                return
            
            # Подтверждение удаления
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить представление '{view_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # Удаляем представление
            sql = f'DROP VIEW IF EXISTS "{view_name}" CASCADE'
            success = self.db_instance.execute_ddl(sql)
            
            if success:
                self.show_info(f"Представление '{view_name}' успешно удалено!")
                self.refresh_views_list()
                self.view_definition_text.clear()
                self.view_data_table.setRowCount(0)
            else:
                self.show_error("Не удалось удалить представление")
                
        except Exception as e:
            self.show_error(f"Ошибка при удалении представления: {e}")
            
    def show_info(self, message):
        """Показывает информационное сообщение"""
        QMessageBox.information(self, "Информация", message)
        
    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        QMessageBox.warning(self, "Ошибка", message)
        
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
            }
            
            #headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 15px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
            }
            
            QTabWidget::pane {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.6);
            }
            
            QTabBar::tab {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 10px 15px;
                color: #f8f8f2;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QTabBar::tab:selected {
                background: rgba(100, 255, 218, 0.2);
                border-color: #64ffda;
                color: #64ffda;
            }
            
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background: rgba(10, 10, 15, 0.9);
            }
            
            QLabel {
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QLineEdit, QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #64ffda;
            }
            
            QListWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 5px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QListWidget::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
            }
            
            QTextEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QTableWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                gridline-color: #44475a;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                color: #f8f8f2;
                padding: 8px;
                border: 1px solid #6272a4;
                font-weight: bold;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #6272a4;
                border-radius: 6px;
                color: #f8f8f2;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px 12px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            
            #createButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                color: #0a0a0f;
                font-size: 14px;
                padding: 10px;
            }
            
            #createButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
            }
            
            #deleteButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                color: #ffffff;
            }
            
            #deleteButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
            }
            
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: none;
                font-size: 14px;
                padding: 10px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 12px;
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
        """)
