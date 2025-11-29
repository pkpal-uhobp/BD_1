from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QListWidget, QListWidgetItem,
    QGroupBox, QScrollArea, QTabWidget, QCheckBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification


class SubqueryFilterDialog(QDialog):
    """Диалог для создания фильтров с подзапросами (ANY, ALL, EXISTS)"""
    
    def __init__(self, db_instance, current_table, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.current_table = current_table
        self.setWindowTitle("Фильтры с подзапросами")
        self.setModal(True)
        self.setMinimumSize(800, 700)
        self.resize(850, 750)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Главный layout диалога
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(10, 10, 10, 10)
        dialog_layout.setSpacing(10)
        self.setLayout(dialog_layout)
        
        # Создаем скролл-область
        scroll_area = QScrollArea()
        scroll_area.setObjectName("mainScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Создаем контент-виджет для скролл-области
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        content_widget.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("ФИЛЬТРЫ С ПОДЗАПРОСАМИ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Информация
        info_label = QLabel("Создайте условие с подзапросом используя ANY, ALL или EXISTS")
        info_label.setObjectName("infoLabel")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Тип фильтра
        type_group = QGroupBox("Тип фильтра")
        type_group.setObjectName("typeGroup")
        type_layout = QVBoxLayout()
        type_group.setLayout(type_layout)
        
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.setObjectName("filterTypeCombo")
        self.filter_type_combo.addItems([
            "ANY - Хотя бы одно значение удовлетворяет условию",
            "ALL - Все значения удовлетворяют условию",
            "EXISTS - Подзапрос возвращает хотя бы одну строку",
            "NOT EXISTS - Подзапрос не возвращает строк",
            "IN - Значение содержится в результате подзапроса",
            "NOT IN - Значение не содержится в результате подзапроса"
        ])
        self.filter_type_combo.currentTextChanged.connect(self.on_filter_type_changed)
        type_layout.addWidget(self.filter_type_combo)
        
        main_layout.addWidget(type_group)
        
        # Группа условия для ANY/ALL/IN
        self.comparison_group = QGroupBox("Условие сравнения")
        self.comparison_group.setObjectName("comparisonGroup")
        comparison_layout = QFormLayout()
        self.comparison_group.setLayout(comparison_layout)
        
        # Столбец основной таблицы
        self.main_column_combo = QComboBox()
        self.main_column_combo.setObjectName("mainColumnCombo")
        if self.db_instance and self.db_instance.is_connected():
            columns = self.db_instance.get_table_columns(current_table)
            self.main_column_combo.addItems(columns)
        comparison_layout.addRow("Столбец:", self.main_column_combo)
        
        # Оператор сравнения (для ANY/ALL)
        self.operator_combo = QComboBox()
        self.operator_combo.setObjectName("operatorCombo")
        self.operator_combo.addItems(["=", "!=", "<", "<=", ">", ">="])
        comparison_layout.addRow("Оператор:", self.operator_combo)
        
        main_layout.addWidget(self.comparison_group)
        
        # Группа подзапроса
        subquery_group = QGroupBox("Подзапрос")
        subquery_group.setObjectName("subqueryGroup")
        subquery_layout = QFormLayout()
        subquery_group.setLayout(subquery_layout)
        
        # Таблица для подзапроса
        self.subquery_table_combo = QComboBox()
        self.subquery_table_combo.setObjectName("subqueryTableCombo")
        if self.db_instance and self.db_instance.is_connected():
            tables = self.db_instance.get_tables()
            self.subquery_table_combo.addItems(tables)
            self.subquery_table_combo.currentTextChanged.connect(self.on_subquery_table_changed)
        subquery_layout.addRow("Таблица:", self.subquery_table_combo)
        
        # Столбец для выбора в подзапросе
        self.subquery_column_combo = QComboBox()
        self.subquery_column_combo.setObjectName("subqueryColumnCombo")
        subquery_layout.addRow("Выбрать столбец:", self.subquery_column_combo)
        
        # WHERE условие для подзапроса
        self.subquery_where_input = QLineEdit()
        self.subquery_where_input.setObjectName("subqueryWhereInput")
        self.subquery_where_input.setPlaceholderText("Например: price > 100 (необязательно)")
        subquery_layout.addRow("WHERE условие:", self.subquery_where_input)
        
        main_layout.addWidget(subquery_group)
        
        # Группа корреляции (для коррелированных подзапросов)
        correlation_group = QGroupBox("Корреляция (для связи с основным запросом)")
        correlation_group.setObjectName("correlationGroup")
        correlation_layout = QFormLayout()
        correlation_group.setLayout(correlation_layout)
        
        self.correlation_checkbox = QCheckBox("Использовать коррелированный подзапрос")
        self.correlation_checkbox.setObjectName("correlationCheckbox")
        self.correlation_checkbox.stateChanged.connect(self.on_correlation_changed)
        correlation_layout.addRow("", self.correlation_checkbox)
        
        # Поле для корреляционного условия
        self.correlation_condition_input = QLineEdit()
        self.correlation_condition_input.setObjectName("correlationConditionInput")
        self.correlation_condition_input.setPlaceholderText(f"Например: {current_table}.id = subquery_table.main_id")
        self.correlation_condition_input.setEnabled(False)
        correlation_layout.addRow("Условие связи:", self.correlation_condition_input)
        
        main_layout.addWidget(correlation_group)
        
        # Предпросмотр SQL
        preview_group = QGroupBox("Предпросмотр SQL")
        preview_group.setObjectName("previewGroup")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)
        
        self.preview_label = QLabel("")
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_group)
        
        # Устанавливаем контент-виджет в скролл-область
        scroll_area.setWidget(content_widget)
        dialog_layout.addWidget(scroll_area, 1)
        
        # Кнопки (вне скролл-области)
        buttons_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.setObjectName("okButton")
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        dialog_layout.addLayout(buttons_layout)
        
        # Подключаем обновление предпросмотра
        self.main_column_combo.currentTextChanged.connect(self.update_preview)
        self.operator_combo.currentTextChanged.connect(self.update_preview)
        self.subquery_table_combo.currentTextChanged.connect(self.update_preview)
        self.subquery_column_combo.currentTextChanged.connect(self.update_preview)
        self.subquery_where_input.textChanged.connect(self.update_preview)
        self.correlation_condition_input.textChanged.connect(self.update_preview)
        
        # Инициализируем столбцы подзапроса
        if self.subquery_table_combo.count() > 0:
            self.on_subquery_table_changed(self.subquery_table_combo.currentText())
        
        # Инициализируем отображение
        self.on_filter_type_changed(self.filter_type_combo.currentText())
        
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
        
    def on_filter_type_changed(self, filter_type):
        """Обработчик изменения типа фильтра"""
        # Показываем/скрываем группы в зависимости от типа фильтра
        if "EXISTS" in filter_type:
            # Для EXISTS не нужно сравнение
            self.comparison_group.setVisible(False)
        else:
            self.comparison_group.setVisible(True)
            
            # Для IN/NOT IN не нужен оператор
            if "IN" in filter_type and "EXISTS" not in filter_type:
                self.operator_combo.setVisible(False)
            else:
                self.operator_combo.setVisible(True)
        
        self.update_preview()
        
    def on_subquery_table_changed(self, table_name):
        """Обработчик изменения таблицы подзапроса"""
        if not table_name or not self.db_instance or not self.db_instance.is_connected():
            return
        
        # Обновляем столбцы подзапроса
        columns = self.db_instance.get_table_columns(table_name)
        self.subquery_column_combo.clear()
        self.subquery_column_combo.addItems(columns)
        
        self.update_preview()
        
    def on_correlation_changed(self, state):
        """Обработчик изменения чекбокса корреляции"""
        self.correlation_condition_input.setEnabled(state == Qt.Checked)
        self.update_preview()
        
    def update_preview(self):
        """Обновляет предпросмотр SQL"""
        sql_condition = self.build_sql_condition()
        if sql_condition:
            self.preview_label.setText(sql_condition)
        else:
            self.preview_label.setText("Заполните необходимые поля")
            
    def build_sql_condition(self):
        """Строит SQL условие с подзапросом"""
        filter_type = self.filter_type_combo.currentText()
        
        # Извлекаем тип фильтра
        if "ANY" in filter_type:
            filter_keyword = "ANY"
        elif "ALL" in filter_type:
            filter_keyword = "ALL"
        elif "NOT EXISTS" in filter_type:
            filter_keyword = "NOT EXISTS"
        elif "EXISTS" in filter_type:
            filter_keyword = "EXISTS"
        elif "NOT IN" in filter_type:
            filter_keyword = "NOT IN"
        elif "IN" in filter_type:
            filter_keyword = "IN"
        else:
            return None
        
        # Строим подзапрос
        subquery_table = self.subquery_table_combo.currentText()
        subquery_column = self.subquery_column_combo.currentText()
        
        if not subquery_table or not subquery_column:
            return None
        
        # Строим SELECT часть подзапроса
        subquery = f'SELECT "{subquery_column}" FROM "{subquery_table}"'
        
        # Добавляем WHERE если есть
        where_condition = self.subquery_where_input.text().strip()
        if where_condition:
            subquery += f' WHERE {where_condition}'
        
        # Добавляем корреляцию если включена
        if self.correlation_checkbox.isChecked():
            correlation_condition = self.correlation_condition_input.text().strip()
            if correlation_condition:
                if where_condition:
                    subquery += f' AND {correlation_condition}'
                else:
                    subquery += f' WHERE {correlation_condition}'
        
        # Строим полное условие
        if filter_keyword in ["EXISTS", "NOT EXISTS"]:
            # Для EXISTS не нужно сравнение
            result = f'{filter_keyword} ({subquery})'
        elif filter_keyword in ["IN", "NOT IN"]:
            # Для IN нужен столбец но не оператор
            main_column = self.main_column_combo.currentText()
            if not main_column:
                return None
            result = f'"{main_column}" {filter_keyword} ({subquery})'
        else:
            # Для ANY/ALL нужен столбец и оператор
            main_column = self.main_column_combo.currentText()
            operator = self.operator_combo.currentText()
            if not main_column or not operator:
                return None
            result = f'"{main_column}" {operator} {filter_keyword} ({subquery})'
        
        return result
        
    def get_subquery_condition(self):
        """Возвращает SQL условие с подзапросом"""
        return self.build_sql_condition()
        
    def apply_styles(self):
        """Применяет стили"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 2px solid #44475a;
                border-radius: 10px;
            }
            
            #headerLabel {
                font-size: 18px;
                font-weight: bold;
                color: #64ffda;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
            }
            
            #infoLabel {
                font-size: 12px;
                color: #8892b0;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px;
            }
            
            QGroupBox {
                color: #64ffda;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: rgba(100, 255, 218, 0.1);
                border-radius: 4px;
            }
            
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            
            QLineEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QLineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QComboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }
            
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                spacing: 10px;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #44475a;
                border-radius: 4px;
                background: rgba(15, 15, 25, 0.8);
            }
            
            QCheckBox::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #44475a, 
                                          stop: 1 #2a2a3a);
                border: 2px solid #64ffda60;
                border-radius: 8px;
                color: #f8f8f2;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px 20px;
                min-height: 35px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #64ffda40,
                                          stop: 1 #44475a);
                border: 2px solid #64ffda;
                color: #64ffda;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
                color: #0a0a0f;
            }
            
            #previewLabel {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #64ffda;
                border-radius: 8px;
                padding: 15px;
                font-size: 12px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #64ffda;
            }
            
            /* Скролл-область */
            #mainScrollArea {
                border: none;
                background: transparent;
            }
            
            #contentWidget {
                background: transparent;
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
        """)
