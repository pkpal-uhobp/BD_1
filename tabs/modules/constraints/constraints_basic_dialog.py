from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QFormLayout, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from sqlalchemy import text
import re


class ConstraintsBasicDialog(QDialog):
    """Диалог наложения базовых ограничений (без PK/FK)."""

    def __init__(self, db_instance, parent=None, table_name=None, column_name=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.table_name = table_name
        self.column_name = column_name
        self.setWindowTitle("🔒 ОГРАНИЧЕНИЯ (без PK/FK)")
        self.setModal(True)
        self.setFixedSize(800, 500)
        self._set_dark_palette()
        self._init_ui()
        self._apply_styles()
        
        # Инициализируем валидацию
        self._init_validation()
        
        # Загружаем текущие ограничения, если указаны таблица и столбец
        if table_name and column_name:
            self._load_current_constraints()

    def _set_dark_palette(self):
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(18, 18, 24))
        pal.setColor(QPalette.WindowText, QColor(240, 240, 240))
        pal.setColor(QPalette.Base, QColor(25, 25, 35))
        pal.setColor(QPalette.Button, QColor(40, 40, 50))
        pal.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        pal.setColor(QPalette.Highlight, QColor(64, 255, 218))
        pal.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(pal)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0a0a0f, stop:1 #1a1a2e); color:#ffffff; }
            #dialogHeader { background: rgba(10,10,15,.7); border:2px solid #64ffda; border-radius:12px; padding:18px; }
            #dialogTitle { font-size:20px; font-weight:bold; color:#64ffda; letter-spacing:2px; }
            #settingsGroup { border:2px solid #44475a; border-radius:12px; padding:16px; background:rgba(15,15,25,.6); }
            #settingsGroup::title { left:18px; padding:0 8px; color:#64ffda; font-weight:bold; }
            #fieldLabel { color:#50fa7b; font-weight:bold; }
            QLineEdit { 
                background: rgba(15, 15, 25, 0.8); 
                border:2px solid #44475a; 
                border-radius:8px; 
                padding:12px 16px; 
                color:#ffffff; 
                font-size: 13px;
            }
            QLineEdit:focus { border:2px solid #64ffda; }
            
            /* Валидация состояний */
            QLineEdit.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }
            
            QLineEdit.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }
            
            .error-label {
                color: #ff5555;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #ff5555;
            }
            
            .success-label {
                color: #50fa7b;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #50fa7b;
            }
            QCheckBox { color:#ffffff; font-weight:bold; }
            QCheckBox::indicator { width:18px; height:18px; }
            QCheckBox::indicator:unchecked { border:2px solid #44475a; background:rgba(25,25,35,.8); border-radius:4px; }
            QCheckBox::indicator:checked { border:2px solid #64ffda; background:#64ffda; border-radius:4px; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
        """)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.setSpacing(20)

        header = QGroupBox()
        header.setObjectName("dialogHeader")
        hl = QVBoxLayout(header)
        t = QLabel("НАСТРОЙКА ОГРАНИЧЕНИЙ")
        t.setObjectName("dialogTitle")
        t.setAlignment(Qt.AlignCenter)
        hl.addWidget(t)
        root.addWidget(header)

        box = QGroupBox("⚙️ ОГРАНИЧЕНИЯ")
        box.setObjectName("settingsGroup")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(15)
        form.setContentsMargins(20, 20, 20, 20)
        
        # Настройка растяжения полей
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setColumnStretch(1, 1)  # Растягиваем колонку с полями ввода

        self.unique_check = QCheckBox("UNIQUE")
        self.not_null_check = QCheckBox("NOT NULL")
        self.null_check = QCheckBox("NULL")
        self.not_null_check.toggled.connect(lambda v: self.null_check.setChecked(False) if v else None)
        self.null_check.toggled.connect(lambda v: self.not_null_check.setChecked(False) if v else None)
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("Значение по умолчанию (пусто — без изменений)")
        self.check_edit = QLineEdit()
        self.check_edit.setPlaceholderText("CHECK выражение, пусто — без изменений, '' — DROP CHECK")

        form.addRow(QLabel("Уникальность:"), self.unique_check)
        form.addRow(QLabel("Обязательность:"), self.not_null_check)
        form.addRow(QLabel("Разрешить NULL:"), self.null_check)
        form.addRow(QLabel("DEFAULT:"), self.default_edit)
        
        # Метка ошибки для DEFAULT
        self.default_error = QLabel()
        self.default_error.setProperty("class", "error-label")
        self.default_error.hide()
        self.default_error.setWordWrap(True)
        form.addRow("", self.default_error)
        
        form.addRow(QLabel("CHECK:"), self.check_edit)
        
        # Метка ошибки для CHECK
        self.check_error = QLabel()
        self.check_error.setProperty("class", "error-label")
        self.check_error.hide()
        self.check_error.setWordWrap(True)
        form.addRow("", self.check_error)
        
        root.addWidget(box)

        btn_row = QWidget()
        bl = QHBoxLayout(btn_row)
        bl.addStretch()
        ok = QPushButton("✅ ПРИМЕНИТЬ")
        ok.setObjectName("primaryButton")
        cancel = QPushButton("✖ ОТМЕНА")
        cancel.setObjectName("secondaryButton")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        bl.addWidget(ok)
        bl.addWidget(cancel)
        root.addWidget(btn_row)

    def _load_current_constraints(self):
        """Загружает текущие ограничения столбца из базы данных"""
        if not self.db_instance or not self.table_name or not self.column_name:
            return
            
        try:
            with self.db_instance.engine.connect() as conn:
                # Получаем информацию о столбце
                column_info = conn.execute(text("""
                    SELECT is_nullable, column_default, data_type
                    FROM information_schema.columns 
                    WHERE table_name = :tbl AND column_name = :col
                """), {"tbl": self.table_name, "col": self.column_name}).first()
                
                if column_info:
                    is_nullable = column_info[0] == 'YES'
                    default_value = column_info[1]
                    data_type = column_info[2]
                    
                    # Устанавливаем NULL/NOT NULL
                    if is_nullable:
                        self.null_check.setChecked(True)
                    else:
                        self.not_null_check.setChecked(True)
                    
                    # Устанавливаем DEFAULT
                    if default_value:
                        self.default_edit.setText(str(default_value))
                
                # Проверяем UNIQUE ограничение
                unique_check = conn.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'UNIQUE' AND tc.table_name = :tbl AND kcu.column_name = :col
                """), {"tbl": self.table_name, "col": self.column_name}).first()
                
                if unique_check:
                    self.unique_check.setChecked(True)
                
                # Проверяем CHECK ограничение
                check_constraint = conn.execute(text("""
                    SELECT cc.check_clause FROM information_schema.table_constraints tc
                    JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
                    WHERE tc.constraint_type = 'CHECK' AND tc.table_name = :tbl
                    AND cc.check_clause LIKE '%' || :col || '%'
                """), {"tbl": self.table_name, "col": self.column_name}).first()
                
                if check_constraint:
                    self.check_edit.setText(check_constraint[0])
                    
        except Exception as e:
            print(f"Ошибка загрузки ограничений: {e}")

    def get_constraints(self):
        return {
            'unique': self.unique_check.isChecked(),
            'nullable': None if (self.not_null_check.isChecked() == self.null_check.isChecked()) else (not self.not_null_check.isChecked()),
            'default': (self.default_edit.text().strip() if self.default_edit.text().strip() != '' else None),
            'check': (self.check_edit.text().strip() if self.check_edit.text().strip() != '' else None)
        }

    def _init_validation(self):
        """Инициализирует валидацию полей"""
        # Подключаем валидацию в реальном времени
        self.default_edit.textChanged.connect(self._validate_default)
        self.check_edit.textChanged.connect(self._validate_check)

    def _has_dangerous_sql(self, text: str) -> bool:
        """Проверяет на наличие опасных SQL конструкций"""
        dangerous_patterns = [
            r'--',  # Комментарии
            r'/\*.*?\*/',  # Блочные комментарии
            r';',  # Точка с запятой
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in dangerous_patterns)

    def _validate_default(self):
        """Валидация поля DEFAULT"""
        text = self.default_edit.text().strip()
        if not text:
            self._clear_field_error('default')
            return True
        if self._has_dangerous_sql(text):
            self._set_field_error('default', "✕ Недопустимы комментарии и ';'")
            return False
        self._set_field_success('default', "✓ Ок")
        return True

    def _validate_check(self):
        """Валидация поля CHECK"""
        text = self.check_edit.text().strip()
        if not text:
            self._clear_field_error('check')
            return True
        if self._has_dangerous_sql(text):
            self._set_field_error('check', "✕ Недопустимы комментарии и ';'")
            return False
        # Простейшая проверка наличия оператора сравнения
        if not re.search(r"[<>=]", text):
            self._set_field_error('check', "✕ Ожидается условие сравнения")
            return False
        self._set_field_success('check', "✓ Ок")
        return True

    def _set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name == 'default':
            self.default_error.setText(error_message)
            self.default_error.setProperty("class", "error-label")
            self.default_error.setStyleSheet(self.styleSheet())
            self.default_error.show()
            self.default_edit.setProperty("class", "error")
            self.default_edit.setStyleSheet(self.styleSheet())
        elif field_name == 'check':
            self.check_error.setText(error_message)
            self.check_error.setProperty("class", "error-label")
            self.check_error.setStyleSheet(self.styleSheet())
            self.check_error.show()
            self.check_edit.setProperty("class", "error")
            self.check_edit.setStyleSheet(self.styleSheet())

    def _set_field_success(self, field_name, success_message):
        """Устанавливает сообщение об успехе для поля"""
        if field_name == 'default':
            self.default_error.setText(success_message)
            self.default_error.setProperty("class", "success-label")
            self.default_error.setStyleSheet(self.styleSheet())
            self.default_error.show()
            self.default_edit.setProperty("class", "success")
            self.default_edit.setStyleSheet(self.styleSheet())
        elif field_name == 'check':
            self.check_error.setText(success_message)
            self.check_error.setProperty("class", "success-label")
            self.check_error.setStyleSheet(self.styleSheet())
            self.check_error.show()
            self.check_edit.setProperty("class", "success")
            self.check_edit.setStyleSheet(self.styleSheet())

    def _clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name == 'default':
            self.default_error.hide()
            self.default_error.setText("")
            self.default_error.setProperty("class", "error-label")
            self.default_error.setStyleSheet(self.styleSheet())
            self.default_edit.setProperty("class", "")
            self.default_edit.setStyleSheet(self.styleSheet())
        elif field_name == 'check':
            self.check_error.hide()
            self.check_error.setText("")
            self.check_error.setProperty("class", "error-label")
            self.check_error.setStyleSheet(self.styleSheet())
            self.check_edit.setProperty("class", "")
            self.check_edit.setStyleSheet(self.styleSheet())


