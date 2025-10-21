from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QFormLayout, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from sqlalchemy import text


class ConstraintsBasicDialog(QDialog):
    """Диалог наложения базовых ограничений (без PK/FK)."""

    def __init__(self, db_instance, parent=None, table_name=None, column_name=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.table_name = table_name
        self.column_name = column_name
        self.setWindowTitle("🔒 ОГРАНИЧЕНИЯ (без PK/FK)")
        self.setModal(True)
        self.setFixedSize(600, 420)
        self._set_dark_palette()
        self._init_ui()
        self._apply_styles()
        
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
            QLineEdit { background: rgba(15, 15, 25, 0.8); border:2px solid #44475a; border-radius:8px; padding:10px; color:#ffffff; }
            QLineEdit:focus { border:2px solid #64ffda; }
            QCheckBox { color:#ffffff; font-weight:bold; }
            QCheckBox::indicator { width:18px; height:18px; }
            QCheckBox::indicator:unchecked { border:2px solid #44475a; background:rgba(25,25,35,.8); border-radius:4px; }
            QCheckBox::indicator:checked { border:2px solid #64ffda; background:#64ffda; border-radius:4px; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
        """)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

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
        form.addRow(QLabel("CHECK:"), self.check_edit)
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


