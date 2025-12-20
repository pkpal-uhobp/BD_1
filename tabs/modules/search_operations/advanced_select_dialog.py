from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QCheckBox,
                             QComboBox, QListWidget, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from .window_functions_dialog import WindowFunctionDialog

class AdvancedSelectDialog(QDialog):
    def __init__(self, db_instance, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.connection = connection if connection else db_instance
        self.table_name = table_name
        self.setWindowTitle("Advanced SELECT Builder")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Table selection
        table_group = QGroupBox("FROM Clause")
        table_layout = QVBoxLayout()
        
        table_label = QLabel("Table:")
        table_layout.addWidget(table_label)
        self.table_combo = QComboBox()
        if table_name:
            self.table_combo.addItem(table_name)
            self.table_combo.setCurrentText(table_name)
        else:
            # Load tables from database
            if self.db_instance and hasattr(self.db_instance, 'get_tables'):
                try:
                    tables = self.db_instance.get_tables()
                    self.table_combo.addItems(tables)
                except Exception:
                    pass
        table_layout.addWidget(self.table_combo)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # SELECT clause
        select_group = QGroupBox("SELECT Clause")
        select_layout = QVBoxLayout()
        
        self.distinct_check = QCheckBox("DISTINCT")
        select_layout.addWidget(self.distinct_check)
        
        columns_label = QLabel("Columns (comma-separated, * for all):")
        select_layout.addWidget(columns_label)
        self.columns_input = QLineEdit()
        self.columns_input.setText("*")
        select_layout.addWidget(self.columns_input)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Группа дополнительных функций
        special_funcs_group = QGroupBox("Специальные функции")
        special_funcs_layout = QVBoxLayout()
        
        special_funcs_buttons_layout = QHBoxLayout()
        
        self.add_window_func_btn = QPushButton("+ Оконная функция")
        self.add_window_func_btn.setObjectName("addWindowFuncBtn")
        self.add_window_func_btn.clicked.connect(self.add_window_function)
        
        special_funcs_buttons_layout.addWidget(self.add_window_func_btn)
        special_funcs_layout.addLayout(special_funcs_buttons_layout)
        
        # List to display added special functions
        self.special_functions = QListWidget()
        self.special_functions.setObjectName("specialFunctions")
        special_funcs_layout.addWidget(self.special_functions)
        
        special_funcs_group.setLayout(special_funcs_layout)
        layout.addWidget(special_funcs_group)
        
        # Query preview
        preview_group = QGroupBox("Query Preview")
        preview_layout = QVBoxLayout()
        self.query_preview = QTextEdit()
        self.query_preview.setReadOnly(True)
        preview_layout.addWidget(self.query_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply styles
        self.apply_styles()
        
    def add_window_function(self):
        """Добавляет оконную функцию (RANK, LAG, LEAD, etc.)"""
        table_name = self.table_combo.currentText() if hasattr(self, 'table_combo') else self.table_name
        
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return
        
        # Create dialog for window function selection
        dialog = WindowFunctionDialog(self.db_instance if hasattr(self, 'db_instance') else self.connection, self)
        if dialog.exec():
            window_func_sql = dialog.get_window_function_expression()
            if window_func_sql:
                if hasattr(self, 'special_functions'):
                    self.special_functions.addItem(window_func_sql)
                else:
                    # Fallback: add to columns input
                    current_columns = self.columns_input.text()
                    if current_columns == "*":
                        self.columns_input.setText(window_func_sql)
                    else:
                        self.columns_input.setText(f"{current_columns}, {window_func_sql}")
                
                # Update preview if method exists
                if hasattr(self, 'update_preview'):
                    self.update_preview()
    
    def update_preview(self):
        query = self.get_query()
        self.query_preview.setPlainText(query)
    
    def get_query(self):
        distinct = "DISTINCT " if self.distinct_check.isChecked() else ""
        columns = self.columns_input.text() or "*"
        
        # Add special functions to columns
        if hasattr(self, 'special_functions') and self.special_functions.count() > 0:
            special_funcs = []
            for i in range(self.special_functions.count()):
                special_funcs.append(self.special_functions.item(i).text())
            
            if columns == "*":
                columns = f"*, {', '.join(special_funcs)}"
            else:
                columns = f"{columns}, {', '.join(special_funcs)}"
        
        table_name = self.table_combo.currentText() if hasattr(self, 'table_combo') else self.table_name
        if not table_name:
            table_name = "your_table"
        
        query = f"SELECT {distinct}{columns}\nFROM {table_name}"
        
        return query
    
    def apply_styles(self):
        """Применяет стили к диалогу"""
        self.setStyleSheet("""
            #addWindowFuncBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #667eea, 
                                          stop: 1 #764ba2);
                border: none;
                border-radius: 6px;
                color: #f8f8f2;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 15px;
            }
            
            #addWindowFuncBtn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #764ba2, 
                                          stop: 1 #667eea);
                border: 2px solid #64ffda;
            }
        """)
