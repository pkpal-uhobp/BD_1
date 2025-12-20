from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QCheckBox,
                             QComboBox, QListWidget, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from tabs.modules.search_operations.join_dialog import JoinDialog
from .window_functions_dialog import WindowFunctionDialog

class AdvancedSelectDialog(QDialog):
    def __init__(self, parent=None, connection=None, table_name=None):
        super().__init__(parent)
        self.connection = connection
        self.table_name = table_name
        self.setWindowTitle("Advanced SELECT Builder")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
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
        
        # Additional features buttons
        features_layout = QHBoxLayout()
        self.join_button = QPushButton("Add JOIN")
        self.join_button.clicked.connect(self.add_join)
        features_layout.addWidget(self.join_button)
        
        self.window_func_button = QPushButton("Add Window Function")
        self.window_func_button.clicked.connect(self.add_window_function)
        features_layout.addWidget(self.window_func_button)
        
        layout.addLayout(features_layout)
        
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
        
    def add_window_function(self):
        dialog = WindowFunctionDialog(self, self.connection, self.table_name)
        if dialog.exec():
            window_func_query = dialog.get_window_function_sql()
            current_columns = self.columns_input.text()
            if current_columns == "*":
                self.columns_input.setText(window_func_query)
            else:
                self.columns_input.setText(f"{current_columns}, {window_func_query}")
            self.update_preview()
    
    def add_join(self):
        dialog = JoinDialog(self, self.connection, self.table_name)
        if dialog.exec():
            join_clause = dialog.get_join_clause()
            # Update preview with join clause
            self.update_preview()
    
    def update_preview(self):
        query = self.get_query()
        self.query_preview.setPlainText(query)
    
    def get_query(self):
        distinct = "DISTINCT " if self.distinct_check.isChecked() else ""
        columns = self.columns_input.text() or "*"
        
        query = f"SELECT {distinct}{columns}\nFROM {self.table_name}"
        
        return query
