from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFormLayout, QMessageBox, QWidget, QListWidget, QListWidgetItem,
    QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor


class WhenClauseWidget(QWidget):
    """Виджет для одного WHEN условия"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        # WHEN условие
        layout.addWidget(QLabel("WHEN"))
        self.when_input = QLineEdit()
        self.when_input.setObjectName("whenInput")
        self.when_input.setPlaceholderText("Например: age > 18")
        self.when_input.setMinimumWidth(200)
        layout.addWidget(self.when_input)
        
        # THEN значение
        layout.addWidget(QLabel("THEN"))
        self.then_input = QLineEdit()
        self.then_input.setObjectName("thenInput")
        self.then_input.setPlaceholderText("Например: 'Взрослый'")
        self.then_input.setMinimumWidth(150)
        layout.addWidget(self.then_input)
        
        # Кнопка удаления
        self.remove_btn = QPushButton("X")
        self.remove_btn.setObjectName("removeWhenBtn")
        self.remove_btn.setMaximumWidth(30)
        self.remove_btn.setMaximumHeight(30)
        layout.addWidget(self.remove_btn)
        
        # Подключаем сигнал удаления
        self.remove_btn.clicked.connect(self.remove_self)
        
    def remove_self(self):
        """Удаляет этот виджет"""
        # Находим главный диалог через цепочку родителей
        parent = self.parent()
        while parent and not hasattr(parent, 'remove_when_widget'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'remove_when_widget'):
            parent.remove_when_widget(self)
            
    def get_when_clause(self):
        """Возвращает SQL для WHEN...THEN"""
        when_condition = self.when_input.text().strip()
        then_value = self.then_input.text().strip()
        
        if when_condition and then_value:
            return f"WHEN {when_condition} THEN {then_value}"
        return None


class CaseExpressionDialog(QDialog):
    """Диалог для создания CASE выражения"""
    
    def __init__(self, columns_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конструктор CASE выражения")
        self.setModal(True)
        self.setMinimumSize(750, 600)
        self.resize(800, 650)
        
        # Устанавливаем темную палитру
        self.set_dark_palette()
        
        # Главный layout диалога
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(10, 10, 10, 10)
        dialog_layout.setSpacing(10)
        self.setLayout(dialog_layout)
        
        # Создаем скролл-область для основного контента
        main_scroll = QScrollArea()
        main_scroll.setObjectName("mainScrollArea")
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Создаем контент-виджет
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        content_widget.setLayout(main_layout)
        
        # Заголовок
        header_label = QLabel("КОНСТРУКТОР CASE ВЫРАЖЕНИЯ")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Информация
        info_label = QLabel("Создайте условное выражение WHEN ... THEN ... ELSE")
        info_label.setObjectName("infoLabel")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Группа WHEN clauses
        when_group = QGroupBox("WHEN условия")
        when_group.setObjectName("whenGroup")
        when_layout = QVBoxLayout()
        when_group.setLayout(when_layout)
        
        # Кнопка добавления WHEN
        add_when_btn = QPushButton("+ Добавить WHEN условие")
        add_when_btn.setObjectName("addWhenBtn")
        add_when_btn.clicked.connect(self.add_when_clause)
        when_layout.addWidget(add_when_btn)
        
        # Контейнер для WHEN виджетов
        self.when_widgets_container = QWidget()
        self.when_widgets_container.setObjectName("whenWidgetsContainer")
        self.when_widgets_layout = QVBoxLayout()
        self.when_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self.when_widgets_container.setLayout(self.when_widgets_layout)
        
        # Скролл для WHEN виджетов
        when_scroll = QScrollArea()
        when_scroll.setWidgetResizable(True)
        when_scroll.setWidget(self.when_widgets_container)
        when_scroll.setMinimumHeight(180)
        when_scroll.setMaximumHeight(250)
        when_layout.addWidget(when_scroll)
        
        main_layout.addWidget(when_group)
        
        # ELSE часть
        else_group = QGroupBox("ELSE (по умолчанию)")
        else_group.setObjectName("elseGroup")
        else_layout = QFormLayout()
        else_group.setLayout(else_layout)
        
        self.else_input = QLineEdit()
        self.else_input.setObjectName("elseInput")
        self.else_input.setPlaceholderText("Например: 'Нет данных' или NULL")
        else_layout.addRow("ELSE:", self.else_input)
        
        main_layout.addWidget(else_group)
        
        # Алиас
        alias_group = QGroupBox("Алиас столбца")
        alias_group.setObjectName("aliasGroup")
        alias_layout = QFormLayout()
        alias_group.setLayout(alias_layout)
        
        self.alias_input = QLineEdit()
        self.alias_input.setObjectName("aliasInput")
        self.alias_input.setPlaceholderText("Например: category")
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
        
        # Устанавливаем контент в скролл-область
        main_scroll.setWidget(content_widget)
        dialog_layout.addWidget(main_scroll, 1)
        
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
        
        # Добавляем первый WHEN по умолчанию
        self.add_when_clause()
        
        # Подключаем обновление предпросмотра
        self.else_input.textChanged.connect(self.update_preview)
        self.alias_input.textChanged.connect(self.update_preview)
        
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
        
    def add_when_clause(self):
        """Добавляет новый WHEN виджет"""
        when_widget = WhenClauseWidget(self)
        self.when_widgets_layout.addWidget(when_widget)
        
        # Подключаем обновление предпросмотра
        when_widget.when_input.textChanged.connect(self.update_preview)
        when_widget.then_input.textChanged.connect(self.update_preview)
        
        self.update_preview()
        
    def remove_when_widget(self, widget):
        """Удаляет WHEN виджет"""
        self.when_widgets_layout.removeWidget(widget)
        widget.deleteLater()
        self.update_preview()
        
    def update_preview(self):
        """Обновляет предпросмотр SQL"""
        case_expr = self.get_case_expression()
        if case_expr:
            self.preview_label.setText(case_expr)
        else:
            self.preview_label.setText("Добавьте хотя бы одно WHEN условие")
            
    def get_case_expression(self):
        """Возвращает сформированное CASE выражение"""
        when_clauses = []
        
        # Собираем все WHEN условия
        for i in range(self.when_widgets_layout.count()):
            widget = self.when_widgets_layout.itemAt(i).widget()
            if isinstance(widget, WhenClauseWidget):
                when_clause = widget.get_when_clause()
                if when_clause:
                    when_clauses.append(when_clause)
        
        if not when_clauses:
            return None
        
        # Формируем CASE выражение
        result = "CASE "
        result += " ".join(when_clauses)
        
        # Добавляем ELSE если указано
        else_value = self.else_input.text().strip()
        if else_value:
            result += f" ELSE {else_value}"
        
        result += " END"
        
        # Добавляем алиас если указан
        alias = self.alias_input.text().strip()
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
            
            #removeWhenBtn {
                max-width: 30px;
                max-height: 30px;
                padding: 5px;
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
            
            QScrollArea {
                border: 2px solid #44475a;
                border-radius: 8px;
                background: rgba(15, 15, 25, 0.5);
            }
            
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
