"""
Диалог для работы с материализованными представлениями (MATERIALIZED VIEW) в базе данных PostgreSQL
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


class MaterializedViewsDialog(QDialog):
    """Диалог для управления материализованными представлениями (MATERIALIZED VIEW)"""
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Управление материализованными представлениями")
        self.setModal(True)
        self.setMinimumSize(950, 750)
        self.resize(950, 750)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("МАТЕРИАЛИЗОВАННЫЕ ПРЕДСТАВЛЕНИЯ (MATERIALIZED VIEW)")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Информационный блок
        info_label = QLabel(
            "Материализованные представления хранят результаты запроса физически.\n"
            "Используйте REFRESH для обновления данных после изменения базовых таблиц."
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Вкладка создания
        create_tab = self.create_matview_tab()
        tab_widget.addTab(create_tab, "Создать MATERIALIZED VIEW")
        
        # Вкладка управления
        manage_tab = self.manage_matviews_tab()
        tab_widget.addTab(manage_tab, "Управление")
        
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
        
    def create_matview_tab(self):
        """Создает вкладку для создания материализованного представления"""
        tab = QWidget()
        tab_outer_layout = QVBoxLayout()
        tab_outer_layout.setContentsMargins(0, 0, 0, 0)
        tab.setLayout(tab_outer_layout)
        
        # Scroll area для содержимого вкладки
        scroll_area = QScrollArea()
        scroll_area.setObjectName("matviewCreateScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        tab_outer_layout.addWidget(scroll_area)
        
        # Группа настроек
        settings_group = QGroupBox("Настройки материализованного представления")
        settings_layout = QFormLayout()
        settings_group.setLayout(settings_layout)
        
        # Имя представления
        self.matview_name_input = QLineEdit()
        self.matview_name_input.setPlaceholderText("Введите имя (например: mv_book_stats)")
        settings_layout.addRow("Имя MV:", self.matview_name_input)
        
        # Выбор базовой таблицы
        self.matview_table_combo = QComboBox()
        self.matview_table_combo.currentTextChanged.connect(self.on_matview_table_changed)
        settings_layout.addRow("Базовая таблица:", self.matview_table_combo)
        
        layout.addWidget(settings_group)
        
        # Группа выбора столбцов
        columns_group = QGroupBox("Выбор столбцов")
        columns_layout = QVBoxLayout()
        columns_group.setLayout(columns_layout)
        
        # Список доступных столбцов
        columns_layout.addWidget(QLabel("Доступные столбцы:"))
        self.available_matview_columns = QListWidget()
        self.available_matview_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(self.available_matview_columns)
        
        # Кнопки
        columns_buttons = QHBoxLayout()
        add_col_btn = QPushButton(">> Добавить")
        add_col_btn.clicked.connect(self.add_matview_columns)
        add_all_col_btn = QPushButton(">>> Все")
        add_all_col_btn.clicked.connect(self.add_all_matview_columns)
        columns_buttons.addWidget(add_col_btn)
        columns_buttons.addWidget(add_all_col_btn)
        columns_layout.addLayout(columns_buttons)
        
        # Выбранные столбцы
        columns_layout.addWidget(QLabel("Выбранные столбцы:"))
        self.selected_matview_columns = QListWidget()
        self.selected_matview_columns.setSelectionMode(QListWidget.MultiSelection)
        columns_layout.addWidget(self.selected_matview_columns)
        
        # Кнопки удаления
        remove_buttons = QHBoxLayout()
        remove_col_btn = QPushButton("<< Удалить")
        remove_col_btn.clicked.connect(self.remove_matview_columns)
        remove_all_col_btn = QPushButton("<<< Все")
        remove_all_col_btn.clicked.connect(self.remove_all_matview_columns)
        remove_buttons.addWidget(remove_col_btn)
        remove_buttons.addWidget(remove_all_col_btn)
        columns_layout.addLayout(remove_buttons)
        
        layout.addWidget(columns_group)
        
        # Группа агрегатных функций
        agg_group = QGroupBox("Агрегатные функции (опционально)")
        agg_layout = QVBoxLayout()
        agg_group.setLayout(agg_layout)
        
        agg_buttons = QHBoxLayout()
        add_agg_btn = QPushButton("+ Добавить агрегат")
        add_agg_btn.clicked.connect(self.add_matview_aggregate)
        agg_buttons.addWidget(add_agg_btn)
        agg_buttons.addStretch()
        agg_layout.addLayout(agg_buttons)
        
        self.matview_aggregates = QListWidget()
        agg_layout.addWidget(self.matview_aggregates)
        
        remove_agg_btn = QPushButton("<< Удалить агрегат")
        remove_agg_btn.clicked.connect(self.remove_matview_aggregate)
        agg_layout.addWidget(remove_agg_btn)
        
        layout.addWidget(agg_group)
        
        # Группа GROUP BY
        groupby_group = QGroupBox("GROUP BY (опционально)")
        groupby_layout = QVBoxLayout()
        groupby_group.setLayout(groupby_layout)
        
        self.matview_groupby_list = QListWidget()
        self.matview_groupby_list.setSelectionMode(QListWidget.MultiSelection)
        groupby_layout.addWidget(self.matview_groupby_list)
        
        layout.addWidget(groupby_group)
        
        # Группа WHERE
        where_group = QGroupBox("Условие WHERE (опционально)")
        where_layout = QVBoxLayout()
        where_group.setLayout(where_layout)
        
        self.matview_where_input = QLineEdit()
        self.matview_where_input.setPlaceholderText("Например: deposit_amount > 100")
        where_layout.addWidget(self.matview_where_input)
        
        layout.addWidget(where_group)
        
        # Кнопка создания
        create_button = QPushButton("Создать MATERIALIZED VIEW")
        create_button.setObjectName("createButton")
        create_button.clicked.connect(self.create_matview)
        layout.addWidget(create_button)
        
        # Заполняем список таблиц
        self.populate_tables_for_matview()
        
        return tab
        
    def manage_matviews_tab(self):
        """Создает вкладку для управления материализованными представлениями"""
        tab = QWidget()
        tab_outer_layout = QVBoxLayout()
        tab_outer_layout.setContentsMargins(0, 0, 0, 0)
        tab.setLayout(tab_outer_layout)
        
        # Scroll area для содержимого вкладки
        scroll_area = QScrollArea()
        scroll_area.setObjectName("matviewManageScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        tab_outer_layout.addWidget(scroll_area)
        
        # Группа списка
        list_group = QGroupBox("Существующие материализованные представления")
        list_layout = QVBoxLayout()
        list_group.setLayout(list_layout)
        
        refresh_btn = QPushButton("Обновить список")
        refresh_btn.clicked.connect(self.refresh_matviews_list)
        list_layout.addWidget(refresh_btn)
        
        self.matviews_list = QListWidget()
        self.matviews_list.itemClicked.connect(self.on_matview_selected)
        list_layout.addWidget(self.matviews_list)
        
        layout.addWidget(list_group)
        
        # Группа информации
        info_group = QGroupBox("Информация о материализованном представлении")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_layout.addWidget(QLabel("SQL определение:"))
        self.matview_definition_text = QTextEdit()
        self.matview_definition_text.setReadOnly(True)
        self.matview_definition_text.setMaximumHeight(120)
        info_layout.addWidget(self.matview_definition_text)
        
        layout.addWidget(info_group)
        
        # Группа данных
        data_group = QGroupBox("Данные материализованного представления")
        data_layout = QVBoxLayout()
        data_group.setLayout(data_layout)
        
        self.matview_data_table = QTableWidget()
        self.matview_data_table.setAlternatingRowColors(True)
        data_layout.addWidget(self.matview_data_table)
        
        layout.addWidget(data_group)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        show_data_btn = QPushButton("Показать данные")
        show_data_btn.clicked.connect(self.show_matview_data)
        
        refresh_data_btn = QPushButton("REFRESH (Обновить данные)")
        refresh_data_btn.setObjectName("refreshButton")
        refresh_data_btn.clicked.connect(self.refresh_matview_data)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(self.delete_matview)
        
        actions_layout.addWidget(show_data_btn)
        actions_layout.addWidget(refresh_data_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(delete_btn)
        layout.addLayout(actions_layout)
        
        # Загружаем список
        self.refresh_matviews_list()
        
        return tab
        
    def populate_tables_for_matview(self):
        """Заполняет список таблиц"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            tables = self.db_instance.get_tables()
            self.matview_table_combo.clear()
            self.matview_table_combo.addItems(tables)
            
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def on_matview_table_changed(self, table_name):
        """Обработчик изменения таблицы"""
        try:
            if not table_name or not self.db_instance:
                return
                
            columns = self.db_instance.get_table_columns(table_name)
            self.available_matview_columns.clear()
            self.selected_matview_columns.clear()
            self.matview_groupby_list.clear()
            self.available_matview_columns.addItems(columns)
            self.matview_groupby_list.addItems(columns)
            
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def add_matview_columns(self):
        """Добавляет выбранные столбцы"""
        selected_items = self.available_matview_columns.selectedItems()
        for item in selected_items:
            if not self.selected_matview_columns.findItems(item.text(), Qt.MatchExactly):
                self.selected_matview_columns.addItem(item.text())
                
    def add_all_matview_columns(self):
        """Добавляет все столбцы"""
        self.selected_matview_columns.clear()
        for i in range(self.available_matview_columns.count()):
            self.selected_matview_columns.addItem(self.available_matview_columns.item(i).text())
            
    def remove_matview_columns(self):
        """Удаляет выбранные столбцы"""
        selected_items = self.selected_matview_columns.selectedItems()
        for item in selected_items:
            self.selected_matview_columns.takeItem(self.selected_matview_columns.row(item))
            
    def remove_all_matview_columns(self):
        """Удаляет все столбцы"""
        self.selected_matview_columns.clear()
        
    def add_matview_aggregate(self):
        """Добавляет агрегатную функцию"""
        from .advanced_select_dialog import AggregateFunctionDialog
        dialog = AggregateFunctionDialog(self.selected_matview_columns, self)
        if dialog.exec() == QDialog.Accepted:
            agg_func = dialog.get_aggregate_function()
            if agg_func:
                self.matview_aggregates.addItem(agg_func)
                
    def remove_matview_aggregate(self):
        """Удаляет агрегатную функцию"""
        selected_items = self.matview_aggregates.selectedItems()
        for item in selected_items:
            self.matview_aggregates.takeItem(self.matview_aggregates.row(item))
    
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
            
    def create_matview(self):
        """Создает материализованное представление"""
        try:
            mv_name = self.matview_name_input.text().strip()
            if not mv_name:
                self.show_error("Введите имя материализованного представления")
                return
                
            if not self.validate_identifier(mv_name):
                self.show_error("Имя может содержать только буквы, цифры и подчеркивания (макс. 63 символа)")
                return
                
            table_name = self.matview_table_combo.currentText()
            if not table_name:
                self.show_error("Выберите базовую таблицу")
                return
            
            # Валидируем имя таблицы
            available_tables = self.db_instance.get_tables()
            if table_name not in available_tables:
                self.show_error("Выбранная таблица не существует")
                return
                
            # Собираем столбцы
            columns = []
            for i in range(self.selected_matview_columns.count()):
                col_name = self.selected_matview_columns.item(i).text()
                if self.validate_identifier(col_name):
                    columns.append(f'"{col_name}"')
                
            # Добавляем агрегатные функции
            for i in range(self.matview_aggregates.count()):
                columns.append(self.matview_aggregates.item(i).text())
                
            if not columns:
                columns = ["*"]
                
            # Собираем GROUP BY
            groupby_cols = []
            for item in self.matview_groupby_list.selectedItems():
                col_name = item.text()
                if self.validate_identifier(col_name):
                    groupby_cols.append(f'"{col_name}"')
                
            # Формируем SQL
            select_clause = ", ".join(columns)
            where_clause = self.matview_where_input.text().strip()
            
            # Валидируем WHERE условие
            is_valid, error_msg = self.validate_where_clause(where_clause)
            if not is_valid:
                self.show_error(f"Ошибка в WHERE условии: {error_msg}")
                return
            
            sql = f'CREATE MATERIALIZED VIEW "{mv_name}" AS SELECT {select_clause} FROM "{table_name}"'
            if where_clause:
                sql += f" WHERE {where_clause}"
            if groupby_cols:
                sql += f" GROUP BY {', '.join(groupby_cols)}"
                
            # Выполняем
            success = self.db_instance.execute_ddl(sql)
            
            if success:
                self.show_info(f"Материализованное представление '{mv_name}' успешно создано!")
                self.matview_name_input.clear()
                self.matview_where_input.clear()
                self.matview_aggregates.clear()
                self.refresh_matviews_list()
            else:
                self.show_error("Не удалось создать материализованное представление")
                
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def refresh_matviews_list(self):
        """Обновляет список материализованных представлений"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
                
            sql = """
                SELECT matviewname 
                FROM pg_matviews 
                WHERE schemaname = 'public'
                ORDER BY matviewname
            """
            
            results = self.db_instance.execute_custom_query(sql)
            
            self.matviews_list.clear()
            for row in results:
                mv_name = row.get('matviewname', '')
                if mv_name:
                    self.matviews_list.addItem(mv_name)
                    
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def on_matview_selected(self, item):
        """Обработчик выбора материализованного представления"""
        try:
            mv_name = item.text()
            
            # Валидируем имя
            if not self.validate_identifier(mv_name):
                self.matview_definition_text.setPlainText("Ошибка: некорректное имя")
                return
            
            # Используем безопасное экранирование
            safe_name = mv_name.replace("'", "''")
            sql = f"""
                SELECT definition 
                FROM pg_matviews 
                WHERE schemaname = 'public' AND matviewname = '{safe_name}'
            """
            
            results = self.db_instance.execute_custom_query(sql)
            
            if results:
                definition = results[0].get('definition', '')
                self.matview_definition_text.setPlainText(definition)
            else:
                self.matview_definition_text.setPlainText("Не удалось получить определение")
                
        except Exception as e:
            self.matview_definition_text.setPlainText(f"Ошибка: {e}")
            
    def show_matview_data(self):
        """Показывает данные материализованного представления"""
        try:
            selected_item = self.matviews_list.currentItem()
            if not selected_item:
                self.show_error("Выберите материализованное представление из списка")
                return
                
            mv_name = selected_item.text()
            
            # Валидируем имя
            if not self.validate_identifier(mv_name):
                self.show_error("Некорректное имя представления")
                return
            
            sql = f'SELECT * FROM "{mv_name}" LIMIT 100'
            results = self.db_instance.execute_custom_query(sql)
            
            if not results:
                self.matview_data_table.setRowCount(0)
                self.matview_data_table.setColumnCount(1)
                self.matview_data_table.setHorizontalHeaderLabels(["Нет данных"])
                return
                
            columns = list(results[0].keys())
            self.matview_data_table.setColumnCount(len(columns))
            self.matview_data_table.setHorizontalHeaderLabels(columns)
            self.matview_data_table.setRowCount(len(results))
            
            for row_idx, row in enumerate(results):
                for col_idx, col in enumerate(columns):
                    value = row.get(col, "")
                    if value is None:
                        value = "NULL"
                    self.matview_data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                    
            self.matview_data_table.resizeColumnsToContents()
            
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def refresh_matview_data(self):
        """Обновляет данные материализованного представления (REFRESH)"""
        try:
            selected_item = self.matviews_list.currentItem()
            if not selected_item:
                self.show_error("Выберите материализованное представление для обновления")
                return
                
            mv_name = selected_item.text()
            
            # Валидируем имя
            if not self.validate_identifier(mv_name):
                self.show_error("Некорректное имя представления")
                return
            
            sql = f'REFRESH MATERIALIZED VIEW "{mv_name}"'
            success = self.db_instance.execute_ddl(sql)
            
            if success:
                self.show_info(f"Данные '{mv_name}' успешно обновлены (REFRESH)!")
                self.show_matview_data()
            else:
                self.show_error("Не удалось обновить данные")
                
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def delete_matview(self):
        """Удаляет материализованное представление"""
        try:
            selected_item = self.matviews_list.currentItem()
            if not selected_item:
                self.show_error("Выберите материализованное представление для удаления")
                return
                
            mv_name = selected_item.text()
            
            # Валидируем имя
            if not self.validate_identifier(mv_name):
                self.show_error("Некорректное имя представления")
                return
            
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить '{mv_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            sql = f'DROP MATERIALIZED VIEW IF EXISTS "{mv_name}" CASCADE'
            success = self.db_instance.execute_ddl(sql)
            
            if success:
                self.show_info(f"'{mv_name}' успешно удалено!")
                self.refresh_matviews_list()
                self.matview_definition_text.clear()
                self.matview_data_table.setRowCount(0)
            else:
                self.show_error("Не удалось удалить")
                
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
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
                font-size: 18px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 12px;
                background: rgba(10, 10, 15, 0.7);
                border-radius: 8px;
            }
            
            #infoLabel {
                color: #8892b0;
                font-size: 12px;
                font-style: italic;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 8px;
                background: rgba(100, 255, 218, 0.1);
                border-radius: 6px;
                border-left: 3px solid #64ffda;
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
                font-size: 13px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 20px;
                margin-bottom: 10px;
                padding: 15px;
                padding-top: 25px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 5px;
                padding: 0 8px;
                background: rgba(10, 10, 15, 0.9);
            }
            
            /* Scroll areas */
            #matviewCreateScrollArea, #matviewManageScrollArea {
                border: none;
                background: transparent;
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
                padding: 6px 10px;
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
                font-size: 13px;
                padding: 10px;
            }
            
            #createButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
            }
            
            #refreshButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ffd700, 
                                          stop: 1 #ffb347);
                border: none;
                color: #0a0a0f;
            }
            
            #refreshButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ffed4e, 
                                          stop: 1 #ffa726);
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
        """)
