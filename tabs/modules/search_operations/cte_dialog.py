"""
Диалог для работы с Common Table Expressions (CTE / WITH-запросы) в базе данных PostgreSQL
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea, QListWidget, QListWidgetItem, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification


class CTEDialog(QDialog):
    """Диалог для работы с Common Table Expressions (CTE)"""
    
    # Сигнал для передачи результатов в главную таблицу
    results_to_main_table = Signal(list)
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Конструктор CTE (WITH-запросы)")
        self.setModal(True)
        self.setMinimumSize(1000, 800)
        self.resize(1000, 800)
        
        # Список CTE блоков
        self.cte_blocks = []
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("КОНСТРУКТОР CTE (WITH-ЗАПРОСЫ)")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Информационный блок
        info_label = QLabel(
            "Common Table Expressions (CTE) позволяют создавать временные именованные\n"
            "результирующие наборы, которые можно использовать в основном запросе.\n"
            "CTE улучшают читаемость и позволяют разбивать сложные запросы на части."
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Создаем scrollable область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        # Группа CTE блоков
        cte_blocks_group = QGroupBox("CTE блоки (WITH)")
        cte_blocks_layout = QVBoxLayout()
        cte_blocks_group.setLayout(cte_blocks_layout)
        
        # Кнопка добавления CTE блока
        add_cte_btn = QPushButton("+ Добавить CTE блок")
        add_cte_btn.setObjectName("addCTEBtn")
        add_cte_btn.clicked.connect(self.add_cte_block)
        cte_blocks_layout.addWidget(add_cte_btn)
        
        # Контейнер для CTE блоков
        self.cte_container = QWidget()
        self.cte_container_layout = QVBoxLayout()
        self.cte_container_layout.setContentsMargins(0, 0, 0, 0)
        self.cte_container.setLayout(self.cte_container_layout)
        cte_blocks_layout.addWidget(self.cte_container)
        
        scroll_layout.addWidget(cte_blocks_group)
        
        # Группа основного запроса
        main_query_group = QGroupBox("Основной запрос (SELECT)")
        main_query_layout = QVBoxLayout()
        main_query_group.setLayout(main_query_layout)
        
        # Выбор источника данных для основного запроса
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Источник данных:"))
        
        self.main_source_combo = QComboBox()
        self.main_source_combo.setObjectName("mainSourceCombo")
        self.main_source_combo.currentTextChanged.connect(self.on_main_source_changed)
        source_layout.addWidget(self.main_source_combo)
        source_layout.addStretch()
        main_query_layout.addLayout(source_layout)
        
        # Список столбцов для основного запроса
        columns_layout = QHBoxLayout()
        
        # Доступные столбцы
        available_cols_layout = QVBoxLayout()
        available_cols_layout.addWidget(QLabel("Доступные столбцы:"))
        self.main_available_columns = QListWidget()
        self.main_available_columns.setSelectionMode(QListWidget.MultiSelection)
        available_cols_layout.addWidget(self.main_available_columns)
        columns_layout.addLayout(available_cols_layout)
        
        # Кнопки перемещения
        buttons_layout = QVBoxLayout()
        buttons_layout.addStretch()
        add_col_btn = QPushButton(">>")
        add_col_btn.clicked.connect(self.add_main_columns)
        remove_col_btn = QPushButton("<<")
        remove_col_btn.clicked.connect(self.remove_main_columns)
        add_all_btn = QPushButton(">>>")
        add_all_btn.clicked.connect(self.add_all_main_columns)
        remove_all_btn = QPushButton("<<<")
        remove_all_btn.clicked.connect(self.remove_all_main_columns)
        buttons_layout.addWidget(add_col_btn)
        buttons_layout.addWidget(remove_col_btn)
        buttons_layout.addWidget(add_all_btn)
        buttons_layout.addWidget(remove_all_btn)
        buttons_layout.addStretch()
        columns_layout.addLayout(buttons_layout)
        
        # Выбранные столбцы
        selected_cols_layout = QVBoxLayout()
        selected_cols_layout.addWidget(QLabel("Выбранные столбцы:"))
        self.main_selected_columns = QListWidget()
        self.main_selected_columns.setSelectionMode(QListWidget.MultiSelection)
        selected_cols_layout.addWidget(self.main_selected_columns)
        columns_layout.addLayout(selected_cols_layout)
        
        main_query_layout.addLayout(columns_layout)
        
        # WHERE условие для основного запроса
        where_layout = QHBoxLayout()
        where_layout.addWidget(QLabel("WHERE (опционально):"))
        self.main_where_input = QLineEdit()
        self.main_where_input.setPlaceholderText("Например: total_count > 5")
        where_layout.addWidget(self.main_where_input)
        main_query_layout.addLayout(where_layout)
        
        # ORDER BY для основного запроса
        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("ORDER BY (опционально):"))
        self.main_order_combo = QComboBox()
        self.main_order_combo.setEditable(True)
        order_layout.addWidget(self.main_order_combo)
        self.main_order_direction = QComboBox()
        self.main_order_direction.addItems(["ASC", "DESC"])
        order_layout.addWidget(self.main_order_direction)
        order_layout.addStretch()
        main_query_layout.addLayout(order_layout)
        
        # LIMIT
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("LIMIT (опционально):"))
        self.main_limit_spin = QSpinBox()
        self.main_limit_spin.setRange(0, 10000)
        self.main_limit_spin.setSpecialValueText("Без ограничения")
        limit_layout.addWidget(self.main_limit_spin)
        limit_layout.addStretch()
        main_query_layout.addLayout(limit_layout)
        
        scroll_layout.addWidget(main_query_group)
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Группа предпросмотра SQL
        preview_group = QGroupBox("Предпросмотр SQL")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)
        
        self.sql_preview = QTextEdit()
        self.sql_preview.setReadOnly(True)
        self.sql_preview.setMaximumHeight(150)
        preview_layout.addWidget(self.sql_preview)
        
        refresh_preview_btn = QPushButton("Обновить предпросмотр")
        refresh_preview_btn.clicked.connect(self.update_sql_preview)
        preview_layout.addWidget(refresh_preview_btn)
        
        main_layout.addWidget(preview_group)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        execute_btn = QPushButton("Выполнить и отправить в главную таблицу")
        execute_btn.setObjectName("executeButton")
        execute_btn.clicked.connect(self.execute_query)
        
        copy_btn = QPushButton("Копировать SQL")
        copy_btn.clicked.connect(self.copy_sql)
        
        clear_btn = QPushButton("Очистить всё")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self.clear_all)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.accept)
        
        actions_layout.addWidget(execute_btn)
        actions_layout.addWidget(copy_btn)
        actions_layout.addWidget(clear_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(close_btn)
        
        main_layout.addLayout(actions_layout)
        
        # Инициализируем список источников
        self.update_sources_list()
        
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
        
    def add_cte_block(self):
        """Добавляет новый CTE блок"""
        cte_block = CTEBlockWidget(self.db_instance, len(self.cte_blocks) + 1, self)
        cte_block.removed.connect(self.remove_cte_block)
        cte_block.updated.connect(self.update_sources_list)
        self.cte_blocks.append(cte_block)
        self.cte_container_layout.addWidget(cte_block)
        self.update_sources_list()
        
    def remove_cte_block(self, block):
        """Удаляет CTE блок"""
        if block in self.cte_blocks:
            self.cte_blocks.remove(block)
            self.cte_container_layout.removeWidget(block)
            block.deleteLater()
            # Обновляем номера блоков
            for i, b in enumerate(self.cte_blocks):
                b.update_number(i + 1)
            self.update_sources_list()
            
    def update_sources_list(self):
        """Обновляет список доступных источников для основного запроса"""
        current_source = self.main_source_combo.currentText()
        self.main_source_combo.clear()
        
        # Добавляем таблицы базы данных
        try:
            if self.db_instance and self.db_instance.is_connected():
                tables = self.db_instance.get_tables()
                for table in tables:
                    self.main_source_combo.addItem(f"Таблица: {table}")
        except Exception:
            pass
            
        # Добавляем CTE блоки
        for block in self.cte_blocks:
            cte_name = block.get_cte_name()
            if cte_name:
                self.main_source_combo.addItem(f"CTE: {cte_name}")
                
        # Восстанавливаем выбор если возможно
        index = self.main_source_combo.findText(current_source)
        if index >= 0:
            self.main_source_combo.setCurrentIndex(index)
            
    def on_main_source_changed(self, source):
        """Обработчик изменения источника основного запроса"""
        self.main_available_columns.clear()
        self.main_selected_columns.clear()
        self.main_order_combo.clear()
        
        if not source:
            return
            
        try:
            if source.startswith("Таблица: "):
                # Получаем столбцы из таблицы
                table_name = source.replace("Таблица: ", "")
                columns = self.db_instance.get_table_columns(table_name)
                self.main_available_columns.addItems(columns)
                self.main_order_combo.addItems(columns)
            elif source.startswith("CTE: "):
                # Получаем столбцы из CTE блока
                cte_name = source.replace("CTE: ", "")
                for block in self.cte_blocks:
                    if block.get_cte_name() == cte_name:
                        columns = block.get_columns()
                        self.main_available_columns.addItems(columns)
                        self.main_order_combo.addItems(columns)
                        break
        except Exception as e:
            self.show_error(f"Ошибка: {e}")
            
    def add_main_columns(self):
        """Добавляет выбранные столбцы в основной запрос"""
        selected_items = self.main_available_columns.selectedItems()
        for item in selected_items:
            if not self.main_selected_columns.findItems(item.text(), Qt.MatchExactly):
                self.main_selected_columns.addItem(item.text())
                
    def remove_main_columns(self):
        """Удаляет выбранные столбцы из основного запроса"""
        selected_items = self.main_selected_columns.selectedItems()
        for item in selected_items:
            self.main_selected_columns.takeItem(self.main_selected_columns.row(item))
            
    def add_all_main_columns(self):
        """Добавляет все столбцы в основной запрос"""
        self.main_selected_columns.clear()
        for i in range(self.main_available_columns.count()):
            self.main_selected_columns.addItem(self.main_available_columns.item(i).text())
            
    def remove_all_main_columns(self):
        """Удаляет все столбцы из основного запроса"""
        self.main_selected_columns.clear()
    
    def validate_identifier(self, name):
        """Валидирует SQL идентификатор"""
        if not name:
            return False
        # SQL идентификаторы должны начинаться с буквы или подчеркивания
        if not (name[0].isalpha() or name[0] == '_'):
            return False
        return name.replace('_', '').isalnum() and len(name) <= 63
    
    def validate_where_clause(self, where_clause):
        """Базовая валидация WHERE условия для защиты от SQL инъекций"""
        if not where_clause:
            return True, ""
        
        dangerous_patterns = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE',
            'EXEC', 'EXECUTE', '--', '/*', '*/', ';'
        ]
        
        upper_clause = where_clause.upper()
        for pattern in dangerous_patterns:
            if pattern in upper_clause:
                return False, f"Запрещенное ключевое слово: {pattern}"
        
        if where_clause.count('(') != where_clause.count(')'):
            return False, "Несбалансированные скобки"
        
        if where_clause.count("'") % 2 != 0:
            return False, "Незакрытые кавычки"
        
        return True, ""
        
    def build_sql_query(self):
        """Строит полный SQL запрос с CTE"""
        try:
            # Собираем CTE части
            cte_parts = []
            for block in self.cte_blocks:
                cte_sql = block.build_cte_sql()
                if cte_sql:
                    cte_parts.append(cte_sql)
                    
            # Собираем основной запрос
            source = self.main_source_combo.currentText()
            if not source:
                return None
                
            # Определяем источник
            if source.startswith("Таблица: "):
                table_name = source.replace("Таблица: ", "")
                if not self.validate_identifier(table_name):
                    self.show_error("Некорректное имя таблицы")
                    return None
                from_clause = f'"{table_name}"'
            elif source.startswith("CTE: "):
                cte_name = source.replace("CTE: ", "")
                if not self.validate_identifier(cte_name):
                    self.show_error("Некорректное имя CTE")
                    return None
                from_clause = f'"{cte_name}"'
            else:
                return None
                
            # Собираем столбцы
            columns = []
            for i in range(self.main_selected_columns.count()):
                col_name = self.main_selected_columns.item(i).text()
                if self.validate_identifier(col_name):
                    columns.append(f'"{col_name}"')
            if not columns:
                columns = ["*"]
                
            select_clause = ", ".join(columns)
            
            # Формируем основной SELECT
            main_query = f"SELECT {select_clause} FROM {from_clause}"
            
            # Добавляем WHERE с валидацией
            where = self.main_where_input.text().strip()
            if where:
                is_valid, error_msg = self.validate_where_clause(where)
                if not is_valid:
                    self.show_error(f"Ошибка в WHERE: {error_msg}")
                    return None
                main_query += f" WHERE {where}"
                
            # Добавляем ORDER BY
            order_col = self.main_order_combo.currentText().strip()
            if order_col and self.validate_identifier(order_col):
                direction = self.main_order_direction.currentText()
                main_query += f' ORDER BY "{order_col}" {direction}'
                
            # Добавляем LIMIT
            limit = self.main_limit_spin.value()
            if limit > 0:
                main_query += f" LIMIT {limit}"
                
            # Собираем полный запрос
            if cte_parts:
                full_query = f"WITH {', '.join(cte_parts)} {main_query}"
            else:
                full_query = main_query
                
            return full_query
            
        except Exception as e:
            self.show_error(f"Ошибка построения запроса: {e}")
            return None
            
    def update_sql_preview(self):
        """Обновляет предпросмотр SQL"""
        sql = self.build_sql_query()
        if sql:
            # Форматируем SQL для лучшей читаемости
            formatted_sql = sql.replace(" WITH ", "\nWITH ")
            formatted_sql = formatted_sql.replace(", ", ",\n     ")
            formatted_sql = formatted_sql.replace(" SELECT ", "\nSELECT ")
            formatted_sql = formatted_sql.replace(" FROM ", "\nFROM ")
            formatted_sql = formatted_sql.replace(" WHERE ", "\nWHERE ")
            formatted_sql = formatted_sql.replace(" ORDER BY ", "\nORDER BY ")
            formatted_sql = formatted_sql.replace(" LIMIT ", "\nLIMIT ")
            self.sql_preview.setPlainText(formatted_sql)
        else:
            self.sql_preview.setPlainText("Не удалось построить запрос")
            
    def execute_query(self):
        """Выполняет запрос и отправляет результаты"""
        try:
            sql = self.build_sql_query()
            if not sql:
                self.show_error("Не удалось построить запрос")
                return
                
            results = self.db_instance.execute_custom_query(sql)
            
            if not results:
                self.show_info("Запрос выполнен, но не вернул результатов")
                return
                
            # Отправляем результаты в главную таблицу
            self.results_to_main_table.emit(results)
            self.show_info(f"Запрос выполнен успешно! Найдено {len(results)} записей.")
            self.accept()
            
        except Exception as e:
            self.show_error(f"Ошибка выполнения: {e}")
            
    def copy_sql(self):
        """Копирует SQL в буфер обмена"""
        sql = self.build_sql_query()
        if sql:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(sql)
            self.show_info("SQL скопирован в буфер обмена")
            
    def clear_all(self):
        """Очищает все данные"""
        # Удаляем все CTE блоки
        for block in self.cte_blocks[:]:
            self.remove_cte_block(block)
            
        self.main_selected_columns.clear()
        self.main_where_input.clear()
        self.main_order_combo.clear()
        self.main_limit_spin.setValue(0)
        self.sql_preview.clear()
        
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
            
            #infoLabel {
                color: #8892b0;
                font-size: 12px;
                font-style: italic;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
                background: rgba(100, 255, 218, 0.1);
                border-radius: 6px;
                border-left: 3px solid #64ffda;
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
            
            QLineEdit, QComboBox, QSpinBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
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
                color: #50fa7b;
                font-size: 12px;
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
            
            #addCTEBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            
            #executeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                color: #0a0a0f;
                font-size: 13px;
                padding: 10px 15px;
            }
            
            #executeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
            }
            
            #clearButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                color: #ffffff;
            }
            
            #clearButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #f44336);
            }
            
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #6272a4, 
                                          stop: 1 #44475a);
                border: none;
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
            
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)


class CTEBlockWidget(QWidget):
    """Виджет для одного CTE блока"""
    
    removed = Signal(object)
    updated = Signal()
    
    def __init__(self, db_instance, number, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.number = number
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Заголовок блока
        header_layout = QHBoxLayout()
        self.header_label = QLabel(f"CTE блок #{self.number}")
        self.header_label.setObjectName("cteBlockHeader")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        
        remove_btn = QPushButton("✕ Удалить")
        remove_btn.setObjectName("removeCTEBtn")
        remove_btn.clicked.connect(lambda: self.removed.emit(self))
        header_layout.addWidget(remove_btn)
        main_layout.addLayout(header_layout)
        
        # Имя CTE
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя CTE:"))
        self.cte_name_input = QLineEdit()
        self.cte_name_input.setPlaceholderText(f"cte_{self.number}")
        self.cte_name_input.textChanged.connect(lambda: self.updated.emit())
        name_layout.addWidget(self.cte_name_input)
        main_layout.addLayout(name_layout)
        
        # Выбор таблицы-источника
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Таблица:"))
        self.source_combo = QComboBox()
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        source_layout.addWidget(self.source_combo)
        main_layout.addLayout(source_layout)
        
        # Столбцы
        columns_layout = QHBoxLayout()
        
        # Доступные столбцы
        avail_layout = QVBoxLayout()
        avail_layout.addWidget(QLabel("Столбцы:"))
        self.available_columns = QListWidget()
        self.available_columns.setSelectionMode(QListWidget.MultiSelection)
        self.available_columns.setMaximumHeight(100)
        avail_layout.addWidget(self.available_columns)
        columns_layout.addLayout(avail_layout)
        
        # Кнопки
        btns_layout = QVBoxLayout()
        add_btn = QPushButton(">>")
        add_btn.clicked.connect(self.add_columns)
        rem_btn = QPushButton("<<")
        rem_btn.clicked.connect(self.remove_columns)
        btns_layout.addStretch()
        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(rem_btn)
        btns_layout.addStretch()
        columns_layout.addLayout(btns_layout)
        
        # Выбранные столбцы
        sel_layout = QVBoxLayout()
        sel_layout.addWidget(QLabel("Выбрано:"))
        self.selected_columns = QListWidget()
        self.selected_columns.setSelectionMode(QListWidget.MultiSelection)
        self.selected_columns.setMaximumHeight(100)
        sel_layout.addWidget(self.selected_columns)
        columns_layout.addLayout(sel_layout)
        
        main_layout.addLayout(columns_layout)
        
        # WHERE условие
        where_layout = QHBoxLayout()
        where_layout.addWidget(QLabel("WHERE:"))
        self.where_input = QLineEdit()
        self.where_input.setPlaceholderText("Опционально")
        where_layout.addWidget(self.where_input)
        main_layout.addLayout(where_layout)
        
        # Заполняем список таблиц
        self.populate_tables()
        
        # Применяем стили
        self.setStyleSheet("""
            CTEBlockWidget {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #6272a4;
                border-radius: 8px;
                margin: 5px 0;
            }
            
            #cteBlockHeader {
                color: #64ffda;
                font-weight: bold;
                font-size: 14px;
            }
            
            #removeCTEBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                color: #ffffff;
                padding: 4px 8px;
                font-size: 11px;
            }
            
            QLabel {
                color: #f8f8f2;
                font-size: 12px;
            }
            
            QLineEdit, QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 1px solid #44475a;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                color: #f8f8f2;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #64ffda;
            }
            
            QListWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 1px solid #44475a;
                border-radius: 4px;
                padding: 3px;
                font-size: 11px;
                color: #f8f8f2;
            }
            
            QListWidget::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
            }
            
            QPushButton {
                background: #44475a;
                border: 1px solid #6272a4;
                border-radius: 4px;
                color: #f8f8f2;
                padding: 4px 8px;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background: #6272a4;
                border: 1px solid #64ffda;
                color: #64ffda;
            }
        """)
        
    def populate_tables(self):
        """Заполняет список таблиц"""
        try:
            if self.db_instance and self.db_instance.is_connected():
                tables = self.db_instance.get_tables()
                self.source_combo.addItems(tables)
        except Exception:
            pass
            
    def on_source_changed(self, table_name):
        """Обработчик изменения таблицы"""
        self.available_columns.clear()
        self.selected_columns.clear()
        
        try:
            if table_name and self.db_instance:
                columns = self.db_instance.get_table_columns(table_name)
                self.available_columns.addItems(columns)
        except Exception:
            pass
            
        self.updated.emit()
        
    def add_columns(self):
        """Добавляет выбранные столбцы"""
        selected_items = self.available_columns.selectedItems()
        for item in selected_items:
            if not self.selected_columns.findItems(item.text(), Qt.MatchExactly):
                self.selected_columns.addItem(item.text())
        self.updated.emit()
                
    def remove_columns(self):
        """Удаляет выбранные столбцы"""
        selected_items = self.selected_columns.selectedItems()
        for item in selected_items:
            self.selected_columns.takeItem(self.selected_columns.row(item))
        self.updated.emit()
            
    def update_number(self, number):
        """Обновляет номер блока"""
        self.number = number
        self.header_label.setText(f"CTE блок #{self.number}")
        
    def get_cte_name(self):
        """Возвращает имя CTE"""
        name = self.cte_name_input.text().strip()
        if not name:
            name = f"cte_{self.number}"
        return name
        
    def get_columns(self):
        """Возвращает список выбранных столбцов"""
        columns = []
        for i in range(self.selected_columns.count()):
            columns.append(self.selected_columns.item(i).text())
        return columns
        
    def build_cte_sql(self):
        """Строит SQL для этого CTE блока"""
        cte_name = self.get_cte_name()
        table_name = self.source_combo.currentText()
        
        if not table_name:
            return None
            
        # Собираем столбцы
        columns = []
        for i in range(self.selected_columns.count()):
            columns.append(f'"{self.selected_columns.item(i).text()}"')
        if not columns:
            columns = ["*"]
            
        select_clause = ", ".join(columns)
        
        sql = f'"{cte_name}" AS (SELECT {select_clause} FROM "{table_name}"'
        
        where = self.where_input.text().strip()
        if where:
            # Базовая валидация WHERE
            dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE',
                                  'EXEC', 'EXECUTE', '--', '/*', '*/', ';']
            upper_where = where.upper()
            for pattern in dangerous_patterns:
                if pattern in upper_where:
                    return None  # Не добавляем опасный WHERE
            sql += f" WHERE {where}"
            
        sql += ")"
        
        return sql
