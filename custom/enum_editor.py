from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QListWidget, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor


class EnumEditor(QWidget):
    """Виджет для редактирования ENUM значений, похожий на ArrayLineEdit."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Введите значение ENUM")
        self.input_edit.setObjectName("enumInput")
        self.input_edit.returnPressed.connect(self.add_value)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("enumAddBtn")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.clicked.connect(self.add_value)
        
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.add_btn)
        layout.addLayout(input_layout)
        
        # Список значений
        self.values_list = QListWidget()
        self.values_list.setObjectName("enumList")
        self.values_list.setMaximumHeight(120)
        layout.addWidget(self.values_list)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Удалить")
        self.remove_btn.setObjectName("enumRemoveBtn")
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("enumClearBtn")
        
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn.clicked.connect(self.clear_all)
        
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
    
    def apply_styles(self):
        self.setStyleSheet("""
            #enumInput {
                background: rgba(25,25,35,.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 8px;
                color: #f8f8f2;
            }
            #enumInput:focus {
                border: 2px solid #64ffda;
            }
            #enumAddBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-weight: bold;
                font-size: 14px;
            }
            #enumAddBtn:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #50e3c2, stop:1 #00acc1);
            }
            #enumList {
                background: rgba(25,25,35,.6);
                border: 2px solid #44475a;
                border-radius: 8px;
                color: #f8f8f2;
                font-family: 'Consolas', 'Fira Code', monospace;
            }
            #enumList::item {
                padding: 6px;
                border-bottom: 1px solid #44475a;
            }
            #enumList::item:selected {
                background: #64ffda;
                color: #0a0a0f;
            }
            #enumRemoveBtn, #enumClearBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252);
                border: none;
                border-radius: 6px;
                color: #0a0a0f;
                font-weight: bold;
                padding: 6px 12px;
            }
            #enumRemoveBtn:hover, #enumClearBtn:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff5555, stop:1 #ff4444);
            }
        """)
    
    def add_value(self):
        """Добавить значение в список."""
        value = self.input_edit.text().strip()
        if value and value not in self.get_values():
            self.values_list.addItem(value)
            self.input_edit.clear()
    
    def remove_selected(self):
        """Удалить выбранное значение."""
        current_row = self.values_list.currentRow()
        if current_row >= 0:
            self.values_list.takeItem(current_row)
    
    def clear_all(self):
        """Очистить все значения."""
        self.values_list.clear()
    
    def get_values(self):
        """Получить список всех значений."""
        return [self.values_list.item(i).text() for i in range(self.values_list.count())]
    
    def set_values(self, values):
        """Установить список значений."""
        self.clear_all()
        for value in values:
            self.values_list.addItem(value)