from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from tabs.modules.search_operations.window_function_dialog import WindowFunctionDialog


class AdvancedSelectDialog(QDialog):
    """Dialog for advanced SELECT operations with window functions support"""
    
    query_executed = Signal(str)  # Changed from pyqtSignal to Signal
    
    def __init__(self, db_instance, table_name, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.table_name = table_name
        self.setWindowTitle(f"Advanced SELECT - {table_name}")
        self.setMinimumSize(900, 700)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for query editor and results
        splitter = QSplitter(Qt.Vertical)
        
        # Top section - Query editor
        top_widget = self.create_query_editor_section()
        splitter.addWidget(top_widget)
        
        # Bottom section - Results table
        bottom_widget = self.create_results_section()
        splitter.addWidget(bottom_widget)
        
        # Set initial sizes (60% editor, 40% results)
        splitter.setSizes([420, 280])
        
        layout.addWidget(splitter)
        
        # Button layout at the bottom
        button_layout = QHBoxLayout()
        
        self.window_func_btn = QPushButton("Add Window Function")
        self.window_func_btn.clicked.connect(self.add_window_function)
        
        self.execute_btn = QPushButton("Execute Query")
        self.execute_btn.clicked.connect(self.execute_query)
        self.execute_btn.setDefault(True)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_query)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.window_func_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def create_query_editor_section(self):
        """Create the query editor section"""
        from PySide6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Label
        label = QLabel("Enter your SELECT query:")
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Query text editor
        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText(
            f"SELECT * FROM {self.table_name}\n"
            "-- Add your advanced SELECT query here\n"
            "-- You can use window functions, CTEs, subqueries, etc."
        )
        font = QFont("Courier New", 10)
        self.query_text.setFont(font)
        layout.addWidget(self.query_text)
        
        # Info label
        info_label = QLabel(
            "💡 Tip: Use the 'Add Window Function' button to insert window function templates"
        )
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        return widget
        
    def create_results_section(self):
        """Create the results display section"""
        from PySide6.QtWidgets import QWidget, QVBoxLayout
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results label
        self.results_label = QLabel("Query Results:")
        results_font = QFont()
        results_font.setBold(True)
        self.results_label.setFont(results_font)
        layout.addWidget(self.results_label)
        
        # Results table with sorting capability
        self.results_table = QTableWidget()
        self.results_table.setSortingEnabled(True)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.results_table)
        
        return widget
        
    def add_window_function(self):
        """Open dialog to add window function template"""
        dialog = WindowFunctionDialog(self.db_instance, self.table_name, self)
        if dialog.exec() == QDialog.Accepted:
            window_func_query = dialog.get_query()
            if window_func_query:
                # Insert the window function at cursor position
                cursor = self.query_text.textCursor()
                cursor.insertText(window_func_query)
                
    def execute_query(self):
        """Execute the query and display results"""
        query = self.query_text.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a query to execute.")
            return
            
        # Basic validation - query should start with SELECT
        if not query.upper().startswith('SELECT'):
            QMessageBox.warning(
                self, 
                "Invalid Query", 
                "Query must start with SELECT."
            )
            return
            
        try:
            # Execute query
            cursor = self.db_instance.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Display results in table
            self.display_results(results, column_names)
            
            # Update results label with row count
            self.results_label.setText(f"Query Results: ({len(results)} rows)")
            
            # Emit signal
            self.query_executed.emit(query)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Query executed successfully.\n{len(results)} rows returned."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Query Error", 
                f"Error executing query:\n{str(e)}"
            )
            
    def display_results(self, results, column_names):
        """Display query results in the table"""
        # Clear existing content
        self.results_table.clear()
        
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
            
        # Set up table dimensions
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(column_names))
        self.results_table.setHorizontalHeaderLabels(column_names)
        
        # Populate table
        for row_idx, row_data in enumerate(results):
            for col_idx, value in enumerate(row_data):
                # Convert value to string, handle None
                display_value = str(value) if value is not None else "NULL"
                item = QTableWidgetItem(display_value)
                
                # Center align for better readability
                item.setTextAlignment(Qt.AlignCenter)
                
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.results_table.resizeColumnsToContents()
        
        # Enable sorting after populating data
        self.results_table.setSortingEnabled(True)
        
    def clear_query(self):
        """Clear the query text"""
        self.query_text.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.results_label.setText("Query Results:")
        
    def get_query(self):
        """Get the current query text"""
        return self.query_text.toPlainText().strip()
