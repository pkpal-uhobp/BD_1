from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QListWidget, QListWidgetItem,
    QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor


class NullFunctionsDialog(QDialog):
    """Диалог для работы с NULL значениями (COALESCE и NULLIF)"""
    
    def __init__(self, columns_list, parent=None):
        super().__init__(parent)
        self.columns_list = columns_list
        self.setWindowTitle("Функции работы с NULL")
        self.setModal(True)
        self.setMinimumSize(600, 450)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("ФУНКЦИИ РАБОТЫ С NULL")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Выбор функции
        function_group = QGroupBox("Выбор функции")
        function_group.setObjectName("functionGroup")
        function_layout = QVBoxLayout()
        function_group.setLayout(function_layout)
        
        self.function_combo = QComboBox()
        self.function_combo.setObjectName("functionCombo")
        self.function_combo.addItems([
            "COALESCE - Подстановка вместо NULL",
            "NULLIF - Замена значения на NULL"
        ])
        self.function_combo.currentTextChanged.connect(self.on_function_changed)
        function_layout.addWidget(self.function_combo)
        
        main_layout.addWidget(function_group)
        
        # Группа COALESCE
        self.coalesce_group = QGroupBox("COALESCE")
        self.coalesce_group.setObjectName("coalesceGroup")
        coalesce_layout = QFormLayout()
        self.coalesce_group.setLayout(coalesce_layout)
        
        # Столбец для проверки
        self.coalesce_column_combo = QComboBox()
        self.coalesce_column_combo.setObjectName("coalesceColumnCombo")
        for i in range(columns_list.count()):
            self.coalesce_column_combo.addItem(columns_list.item(i).text())
        coalesce_layout.addRow("Столбец:", self.coalesce_column_combo)
        
        # Значение по умолчанию (можно несколько через запятую)
        self.coalesce_values_input = QLineEdit()
        self.coalesce_values_input.setObjectName("coalesceValuesInput")
        self.coalesce_values_input.setPlaceholderText("Например: 'Нет данных', 0")
        coalesce_layout.addRow("Значения по умолчанию:", self.coalesce_values_input)
        
        # Информация
        coalesce_info = QLabel("COALESCE возвращает первое не-NULL значение из списка.\nНапример: COALESCE(column, 'default') вернёт 'default' если column = NULL")
        coalesce_info.setObjectName("infoLabel")
        coalesce_info.setWordWrap(True)
        coalesce_layout.addRow("", coalesce_info)
        
        main_layout.addWidget(self.coalesce_group)
        
        # Группа NULLIF
        self.nullif_group = QGroupBox("NULLIF")
        self.nullif_group.setObjectName("nullifGroup")
        nullif_layout = QFormLayout()
        self.nullif_group.setLayout(nullif_layout)
        
        # Столбец для проверки
        self.nullif_column_combo = QComboBox()
        self.nullif_column_combo.setObjectName("nullifColumnCombo")
        for i in range(columns_list.count()):
            self.nullif_column_combo.addItem(columns_list.item(i).text())
        nullif_layout.addRow("Столбец:", self.nullif_column_combo)
        
        # Значение для сравнения
        self.nullif_value_input = QLineEdit()
        self.nullif_value_input.setObjectName("nullifValueInput")
        self.nullif_value_input.setPlaceholderText("Например: '', 0, 'N/A'")
        nullif_layout.addRow("Значение для замены:", self.nullif_value_input)
        
        # Информация
        nullif_info = QLabel("NULLIF возвращает NULL если два значения равны, иначе первое значение.\nНапример: NULLIF(column, '') вернёт NULL если column = ''")
        nullif_info.setObjectName("infoLabel")
        nullif_info.setWordWrap(True)
        nullif_layout.addRow("", nullif_info)
        
        main_layout.addWidget(self.nullif_group)
        
        # Алиас
        alias_group = QGroupBox("Алиас столбца")
        alias_group.setObjectName("aliasGroup")
        alias_layout = QFormLayout()
        alias_group.setLayout(alias_layout)
        
        self.alias_input = QLineEdit()
        self.alias_input.setObjectName("aliasInput")
        self.alias_input.setPlaceholderText("Например: clean_value")
        alias_layout.addRow("AS:", self.alias_input)
        
        main_layout.addWidget(alias_group)
        
        # Предпросмотр
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
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.setObjectName("okButton")
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        main_layout.addLayout(buttons_layout)
        
        # Подключаем обновление предпросмотра
        self.coalesce_column_combo.currentTextChanged.connect(self.update_preview)
        self.coalesce_values_input.textChanged.connect(self.update_preview)
        self.nullif_column_combo.currentTextChanged.connect(self.update_preview)
        self.nullif_value_input.textChanged.connect(self.update_preview)
        self.alias_input.textChanged.connect(self.update_preview)
        
        # Показываем соответствующую группу
        self.on_function_changed(self.function_combo.currentText())
        
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
        
    def on_function_changed(self, function_text):
        """Обработчик изменения функции"""
        if "COALESCE" in function_text:
            self.coalesce_group.setVisible(True)
            self.nullif_group.setVisible(False)
        else:  # NULLIF
            self.coalesce_group.setVisible(False)
            self.nullif_group.setVisible(True)
        
        self.update_preview()
        
    def update_preview(self):
        """Обновляет предпросмотр SQL"""
        result = self.get_null_function()
        if result:
            self.preview_label.setText(result)
        else:
            self.preview_label.setText("Заполните необходимые поля")
            
    def get_null_function(self):
        """Возвращает сформированную функцию"""
        function_text = self.function_combo.currentText()
        alias = self.alias_input.text().strip()
        
        if "COALESCE" in function_text:
            column = self.coalesce_column_combo.currentText()
            values = self.coalesce_values_input.text().strip()
            
            if not column or not values:
                return None
            
            # Формируем COALESCE
            result = f'COALESCE("{column}", {values})'
            
        else:  # NULLIF
            column = self.nullif_column_combo.currentText()
            value = self.nullif_value_input.text().strip()
            
            if not column or not value:
                return None
            
            # Формируем NULLIF
            result = f'NULLIF("{column}", {value})'
        
        # Добавляем алиас если указан
        if alias:
            result += f' AS "{alias}"'
        
        return result
        
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
                font-size: 11px;
                color: #8892b0;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px;
                font-style: italic;
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
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #64ffda;
                width: 0;
                height: 0;
                margin-right: 10px;
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
        """)
