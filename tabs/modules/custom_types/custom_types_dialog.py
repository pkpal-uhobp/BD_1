from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QListWidget, QListWidgetItem,
    QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from plyer import notification


class FieldWidget(QWidget):
    """Виджет для одного поля составного типа"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        # Имя поля
        layout.addWidget(QLabel("Поле:"))
        self.field_name_input = QLineEdit()
        self.field_name_input.setObjectName("fieldNameInput")
        self.field_name_input.setPlaceholderText("Например: street")
        self.field_name_input.setMinimumWidth(150)
        layout.addWidget(self.field_name_input)
        
        # Тип поля
        layout.addWidget(QLabel("Тип:"))
        self.field_type_combo = QComboBox()
        self.field_type_combo.setObjectName("fieldTypeCombo")
        self.field_type_combo.addItems([
            "TEXT", "VARCHAR(255)", "INTEGER", "BIGINT", "NUMERIC", "REAL", "DOUBLE PRECISION",
            "DATE", "TIMESTAMP", "BOOLEAN", "JSON", "JSONB"
        ])
        self.field_type_combo.setEditable(True)  # Позволяем вводить свой тип
        self.field_type_combo.setMinimumWidth(150)
        layout.addWidget(self.field_type_combo)
        
        # Кнопка удаления
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setObjectName("removeFieldBtn")
        self.remove_btn.setMaximumWidth(30)
        self.remove_btn.setMaximumHeight(30)
        layout.addWidget(self.remove_btn)
        
        # Подключаем сигнал удаления
        self.remove_btn.clicked.connect(self.remove_self)
        
    def remove_self(self):
        """Удаляет этот виджет"""
        parent = self.parent()
        while parent and not hasattr(parent, 'remove_field_widget'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'remove_field_widget'):
            parent.remove_field_widget(self)
            
    def get_field_definition(self):
        """Возвращает определение поля"""
        field_name = self.field_name_input.text().strip()
        field_type = self.field_type_combo.currentText().strip()
        
        if field_name and field_type:
            return {'name': field_name, 'type': field_type}
        return None


class CustomTypesDialog(QDialog):
    """Диалог для управления пользовательскими типами"""
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Управление пользовательскими типами")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЬСКИМИ ТИПАМИ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Вкладка просмотра типов
        view_tab = self.create_view_tab()
        tab_widget.addTab(view_tab, "Просмотр типов")
        
        # Вкладка создания ENUM
        enum_tab = self.create_enum_tab()
        tab_widget.addTab(enum_tab, "Создать ENUM")
        
        # Вкладка создания составного типа
        composite_tab = self.create_composite_tab()
        tab_widget.addTab(composite_tab, "Создать составной тип")
        
        main_layout.addWidget(tab_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("Закрыть")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        main_layout.addLayout(buttons_layout)
        
        # Загружаем типы
        self.refresh_types_list()
        
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
        
    def create_view_tab(self):
        """Создает вкладку просмотра типов"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(self.refresh_types_list)
        
        delete_btn = QPushButton("🗑️ Удалить выбранный")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self.delete_selected_type)
        
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица типов
        self.types_table = QTableWidget()
        self.types_table.setObjectName("typesTable")
        self.types_table.setColumnCount(3)
        self.types_table.setHorizontalHeaderLabels(["Имя типа", "Вид", "Определение"])
        self.types_table.horizontalHeader().setStretchLastSection(True)
        self.types_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.types_table.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addWidget(self.types_table)
        
        return tab
        
    def create_enum_tab(self):
        """Создает вкладку создания ENUM типа"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Имя типа
        name_group = QGroupBox("Имя ENUM типа")
        name_group.setObjectName("nameGroup")
        name_layout = QFormLayout()
        name_group.setLayout(name_layout)
        
        self.enum_name_input = QLineEdit()
        self.enum_name_input.setObjectName("enumNameInput")
        self.enum_name_input.setPlaceholderText("Например: status_type")
        name_layout.addRow("Имя:", self.enum_name_input)
        
        layout.addWidget(name_group)
        
        # Значения
        values_group = QGroupBox("Значения ENUM")
        values_group.setObjectName("valuesGroup")
        values_layout = QVBoxLayout()
        values_group.setLayout(values_layout)
        
        # Поле для ввода значений
        self.enum_values_text = QTextEdit()
        self.enum_values_text.setObjectName("enumValuesText")
        self.enum_values_text.setPlaceholderText("Введите значения, каждое на новой строке:\nactive\ninactive\npending")
        self.enum_values_text.setMaximumHeight(150)
        values_layout.addWidget(QLabel("Значения (каждое на новой строке):"))
        values_layout.addWidget(self.enum_values_text)
        
        layout.addWidget(values_group)
        
        # Кнопка создания
        create_btn = QPushButton("✅ Создать ENUM тип")
        create_btn.setObjectName("createEnumBtn")
        create_btn.clicked.connect(self.create_enum_type)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        
        return tab
        
    def create_composite_tab(self):
        """Создает вкладку создания составного типа"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Имя типа
        name_group = QGroupBox("Имя составного типа")
        name_group.setObjectName("nameGroup")
        name_layout = QFormLayout()
        name_group.setLayout(name_layout)
        
        self.composite_name_input = QLineEdit()
        self.composite_name_input.setObjectName("compositeNameInput")
        self.composite_name_input.setPlaceholderText("Например: address_type")
        name_layout.addRow("Имя:", self.composite_name_input)
        
        layout.addWidget(name_group)
        
        # Поля
        fields_group = QGroupBox("Поля типа")
        fields_group.setObjectName("fieldsGroup")
        fields_layout = QVBoxLayout()
        fields_group.setLayout(fields_layout)
        
        # Кнопка добавления поля
        add_field_btn = QPushButton("➕ Добавить поле")
        add_field_btn.setObjectName("addFieldBtn")
        add_field_btn.clicked.connect(self.add_field_widget)
        fields_layout.addWidget(add_field_btn)
        
        # Контейнер для полей
        self.fields_container = QWidget()
        self.fields_container.setObjectName("fieldsContainer")
        self.fields_layout = QVBoxLayout()
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_container.setLayout(self.fields_layout)
        
        fields_scroll = QScrollArea()
        fields_scroll.setWidgetResizable(True)
        fields_scroll.setWidget(self.fields_container)
        fields_scroll.setMinimumHeight(200)
        fields_layout.addWidget(fields_scroll)
        
        layout.addWidget(fields_group)
        
        # Кнопка создания
        create_btn = QPushButton("✅ Создать составной тип")
        create_btn.setObjectName("createCompositeBtn")
        create_btn.clicked.connect(self.create_composite_type)
        layout.addWidget(create_btn)
        
        # Добавляем первое поле по умолчанию
        self.add_field_widget()
        
        return tab
        
    def add_field_widget(self):
        """Добавляет виджет для поля"""
        field_widget = FieldWidget(self)
        self.fields_layout.addWidget(field_widget)
        
    def remove_field_widget(self, widget):
        """Удаляет виджет поля"""
        self.fields_layout.removeWidget(widget)
        widget.deleteLater()
        
    def refresh_types_list(self):
        """Обновляет список типов"""
        try:
            if not self.db_instance or not self.db_instance.is_connected():
                return
            
            types = self.db_instance.get_custom_types()
            
            self.types_table.setRowCount(0)
            
            for type_info in types:
                row = self.types_table.rowCount()
                self.types_table.insertRow(row)
                
                # Имя типа
                self.types_table.setItem(row, 0, QTableWidgetItem(type_info['type_name']))
                
                # Вид типа
                kind_display = {
                    'enum': 'ENUM',
                    'composite': 'Составной',
                    'domain': 'Домен',
                    'other': 'Другой'
                }.get(type_info['type_kind'], type_info['type_kind'])
                self.types_table.setItem(row, 1, QTableWidgetItem(kind_display))
                
                # Определение
                definition = ""
                if type_info['type_kind'] == 'enum' and 'values' in type_info:
                    definition = ", ".join(type_info['values'])
                elif type_info['type_kind'] == 'composite' and 'fields' in type_info:
                    fields_str = []
                    for field in type_info['fields']:
                        fields_str.append(f"{field['name']}: {field['type']}")
                    definition = "; ".join(fields_str)
                
                self.types_table.setItem(row, 2, QTableWidgetItem(definition))
            
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при обновлении списка типов: {e}",
                timeout=5
            )
            
    def delete_selected_type(self):
        """Удаляет выбранный тип"""
        try:
            current_row = self.types_table.currentRow()
            if current_row < 0:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Выберите тип для удаления",
                    timeout=3
                )
                return
            
            type_name = self.types_table.item(current_row, 0).text()
            
            # Подтверждение
            reply = QMessageBox.question(
                self, 
                'Подтверждение удаления',
                f'Удалить тип "{type_name}"?\n\nВнимание: все столбцы, использующие этот тип, также будут удалены (CASCADE).',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, error = self.db_instance.drop_custom_type(type_name, cascade=True)
                
                if success:
                    notification.notify(
                        title="✅ Успех",
                        message=f"Тип '{type_name}' успешно удалён",
                        timeout=3
                    )
                    self.refresh_types_list()
                else:
                    notification.notify(
                        title="❌ Ошибка",
                        message=f"Ошибка удаления: {error}",
                        timeout=5
                    )
                    
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при удалении типа: {e}",
                timeout=5
            )
            
    def create_enum_type(self):
        """Создает ENUM тип"""
        try:
            type_name = self.enum_name_input.text().strip()
            values_text = self.enum_values_text.toPlainText().strip()
            
            if not type_name:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Введите имя ENUM типа",
                    timeout=3
                )
                return
            
            if not values_text:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Введите хотя бы одно значение",
                    timeout=3
                )
                return
            
            # Разбиваем на строки и очищаем
            values = [v.strip() for v in values_text.split('\n') if v.strip()]
            
            if not values:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Введите хотя бы одно значение",
                    timeout=3
                )
                return
            
            # Создаем тип
            success, error = self.db_instance.create_enum_type(type_name, values)
            
            if success:
                notification.notify(
                    title="✅ Успех",
                    message=f"ENUM тип '{type_name}' успешно создан",
                    timeout=3
                )
                # Очищаем поля
                self.enum_name_input.clear()
                self.enum_values_text.clear()
                # Обновляем список
                self.refresh_types_list()
            else:
                notification.notify(
                    title="❌ Ошибка",
                    message=f"Ошибка создания: {error}",
                    timeout=5
                )
                
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при создании ENUM типа: {e}",
                timeout=5
            )
            
    def create_composite_type(self):
        """Создает составной тип"""
        try:
            type_name = self.composite_name_input.text().strip()
            
            if not type_name:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Введите имя составного типа",
                    timeout=3
                )
                return
            
            # Собираем поля
            fields = []
            for i in range(self.fields_layout.count()):
                widget = self.fields_layout.itemAt(i).widget()
                if isinstance(widget, FieldWidget):
                    field_def = widget.get_field_definition()
                    if field_def:
                        fields.append(field_def)
            
            if not fields:
                notification.notify(
                    title="⚠️ Предупреждение",
                    message="Добавьте хотя бы одно поле",
                    timeout=3
                )
                return
            
            # Создаем тип
            success, error = self.db_instance.create_composite_type(type_name, fields)
            
            if success:
                notification.notify(
                    title="✅ Успех",
                    message=f"Составной тип '{type_name}' успешно создан",
                    timeout=3
                )
                # Очищаем поля
                self.composite_name_input.clear()
                # Очищаем виджеты полей
                while self.fields_layout.count():
                    item = self.fields_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                # Добавляем одно пустое поле
                self.add_field_widget()
                # Обновляем список
                self.refresh_types_list()
            else:
                notification.notify(
                    title="❌ Ошибка",
                    message=f"Ошибка создания: {error}",
                    timeout=5
                )
                
        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Ошибка при создании составного типа: {e}",
                timeout=5
            )
            
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
            
            QLineEdit, QTextEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            
            QLineEdit:focus, QTextEdit:focus {
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
            
            #removeFieldBtn {
                max-width: 30px;
                max-height: 30px;
                padding: 5px;
            }
            
            QTableWidget {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                gridline-color: #44475a;
                color: #f8f8f2;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background: #64ffda40;
                color: #64ffda;
            }
            
            QHeaderView::section {
                background: #2a2a3a;
                color: #64ffda;
                padding: 8px;
                border: 1px solid #44475a;
                font-weight: bold;
            }
            
            QScrollArea {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.5);
            }
            
            QTabWidget::pane {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.5);
            }
            
            QTabBar::tab {
                background: rgba(25, 25, 35, 0.8);
                color: #8892b0;
                padding: 10px 20px;
                border: 2px solid #44475a;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: rgba(35, 35, 45, 0.9);
                color: #64ffda;
                border: 2px solid #64ffda;
                border-bottom: none;
            }
            
            QTabBar::tab:hover {
                background: rgba(30, 30, 40, 0.9);
                color: #64ffda;
            }
        """)
