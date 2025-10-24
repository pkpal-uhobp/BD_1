from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QFormLayout, QComboBox, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from custom.array_line_edit import ArrayLineEdit
from custom.enum_editor import EnumEditor
import re
import logging


class ConstraintsDialog(QDialog):
    """Отдельный диалог для настройки ограничений столбца."""
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("ОГРАНИЧЕНИЯ СТОЛБЦА")
        self.setModal(True)
        self.resize(500, 400)
        self._set_dark_palette()
        
        # Словари для валидации
        self.input_widgets = {}
        self.error_labels = {}
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        header = QGroupBox()
        header.setObjectName("dialogHeader")
        header_l = QVBoxLayout(header)
        title = QLabel("НАСТРОЙКА ОГРАНИЧЕНИЙ")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Выберите ограничения для столбца")
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        header_l.addWidget(title)
        header_l.addWidget(subtitle)
        layout.addWidget(header)
        
        # Ограничения
        box_constraints = QGroupBox("ОГРАНИЧЕНИЯ И КЛЮЧИ")
        box_constraints.setObjectName("settingsGroup")
        form_cons = QFormLayout(box_constraints)
        form_cons.setLabelAlignment(Qt.AlignRight)
        
        self.pk_check = QCheckBox("PRIMARY KEY")
        self.ai_check = QCheckBox("AUTOINCREMENT")
        # Поведение при выборе PK: автоматически ставим NOT NULL, блокируем переключатели, 
        # разрешаем выбрать AUTOINCREMENT (по желанию)
        self.pk_check.toggled.connect(self._on_pk_toggled)
        # Взаимоисключение NOT NULL / NULL остаётся ниже
        self.unique_check = QCheckBox("UNIQUE")
        self.not_null_check = QCheckBox("NOT NULL")
        self.null_check = QCheckBox("NULL")
        self.not_null_check.toggled.connect(lambda v: self.null_check.setChecked(False) if v else None)
        self.null_check.toggled.connect(lambda v: self.not_null_check.setChecked(False) if v else None)
        
        form_cons.addRow(self._label("Первичный ключ:"), self.pk_check)
        form_cons.addRow(self._label("Автоинкремент:"), self.ai_check)
        form_cons.addRow(self._label("Уникальность:"), self.unique_check)
        form_cons.addRow(self._label("Обязательность:"), self.not_null_check)
        form_cons.addRow(self._label("Разрешить NULL:"), self.null_check)
        
        # FK
        self.fk_check = QCheckBox("FOREIGN KEY")
        self.fk_check.toggled.connect(self.on_fk_toggled)
        form_cons.addRow(self._label("Внешний ключ:"), self.fk_check)
        fk_row = QWidget()
        fk_l = QHBoxLayout(fk_row)
        fk_l.setContentsMargins(0, 0, 0, 0)
        self.ref_table = QComboBox()
        self.ref_table.setEnabled(False)
        self.ref_column = QComboBox()
        self.ref_column.setEnabled(False)
        self.ref_table.addItems(self.db_instance.get_table_names() or [])
        self.ref_table.currentTextChanged.connect(self._fill_ref_columns)
        self._fill_ref_columns(self.ref_table.currentText())
        fk_l.addWidget(self.ref_table)
        fk_l.addWidget(self.ref_column)
        form_cons.addRow(self._label("Таблица/столбец:"), fk_row)
        layout.addWidget(box_constraints)
        
        # Доп. параметры
        box_extra = QGroupBox("ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ")
        box_extra.setObjectName("settingsGroup")
        form_extra = QFormLayout(box_extra)
        form_extra.setLabelAlignment(Qt.AlignRight)
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("Оставьте пустым, если нет")
        self.check_edit = QLineEdit()
        self.check_edit.setPlaceholderText("Например: value > 0")
        # Создаем контейнеры для каждого поля с валидацией
        default_container = QWidget()
        default_layout = QVBoxLayout(default_container)
        default_layout.setContentsMargins(0, 0, 0, 0)
        default_layout.setSpacing(5)
        default_layout.addWidget(self.default_edit)
        self.default_error = QLabel()
        self.default_error.setProperty("class", "error-label")
        self.default_error.hide()
        default_layout.addWidget(self.default_error)
        
        check_container = QWidget()
        check_layout = QVBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setSpacing(5)
        check_layout.addWidget(self.check_edit)
        self.check_error = QLabel()
        self.check_error.setProperty("class", "error-label")
        self.check_error.hide()
        check_layout.addWidget(self.check_error)
        
        form_extra.addRow(self._label("Значение по умолчанию:"), default_container)
        form_extra.addRow(self._label("CHECK ограничение:"), check_container)
        
        # Регистрируем виджеты для валидации
        self.input_widgets['default'] = self.default_edit
        self.error_labels['default'] = self.default_error
        self.input_widgets['check'] = self.check_edit
        self.error_labels['check'] = self.check_error
        
        layout.addWidget(box_extra)
        
        # Кнопки
        btn_row = QWidget()
        btn_l = QHBoxLayout(btn_row)
        btn_l.setContentsMargins(16, 10, 16, 10)
        self.btn_ok = QPushButton("ПРИМЕНИТЬ")
        self.btn_ok.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._on_accept)
        btn_l.addWidget(self.btn_ok)
        btn_l.addWidget(self.btn_cancel)
        layout.addWidget(btn_row)

        # Реалтайм-валидация
        self.default_edit.textChanged.connect(self._validate_default)
        self.check_edit.textChanged.connect(self._validate_check)
    
    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].show()
                self.error_labels[field_name].setProperty("class", "error-label")
                self.error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка ошибки
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def set_field_success(self, field_name, success_message):
        """Устанавливает сообщение об успехе для поля"""
        if field_name in self.error_labels:
            if success_message:
                self.error_labels[field_name].setText(success_message)
                self.error_labels[field_name].show()
                self.error_labels[field_name].setProperty("class", "success-label")
                self.error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка успеха
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setText("")
            self.error_labels[field_name].setProperty("class", "error-label")
            self.error_labels[field_name].setStyleSheet(self.styleSheet())
            # Убираем подсветку
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    def _on_pk_toggled(self, checked: bool):
        # Автоматическое применение зависимых ограничений для PK
        # 1) NOT NULL включается и блокируется
        self.not_null_check.setChecked(True if checked else self.not_null_check.isChecked())
        self.not_null_check.setEnabled(not checked)
        # 2) NULL выключается, блокируется при PK
        if checked:
            self.null_check.setChecked(False)
        self.null_check.setEnabled(not checked)
        # 3) UNIQUE можно не показывать при PK — он подразумевается, выключим и заблокируем
        self.unique_check.setChecked(False)
        self.unique_check.setEnabled(not checked)
        # 4) AUTOINCREMENT доступен только при PK (пользователь может включить по желанию)
        self.ai_check.setEnabled(checked)
        if not checked:
            self.ai_check.setChecked(False)
    
    def _label(self, text):
        l = QLabel(text)
        l.setObjectName("fieldLabel")
        return l
    
    def _set_dark_palette(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0a0a0f, stop:1 #1a1a2e); color:#ffffff; }
            #dialogHeader { background: rgba(10,10,15,.7); border:2px solid #64ffda; border-radius:12px; padding:18px; }
            #dialogTitle { font-size:20px; font-weight:bold; color:#64ffda; letter-spacing:2px; }
            #dialogSubtitle { color:#50fa7b; font-size:12px; }
            #settingsGroup { border:2px solid #44475a; border-radius:12px; padding:16px; background:rgba(15,15,25,.6); }
            #settingsGroup::title { left:18px; padding:0 8px; color:#64ffda; font-weight:bold; }
            #fieldLabel { color:#ffffff; font-weight:bold; }
            QLineEdit, QComboBox { background: rgba(15, 15, 25, 0.8); border:2px solid #44475a; border-radius:8px; padding:10px; color:#ffffff; }
            QLineEdit:focus, QComboBox:focus { border:2px solid #64ffda; }
            QComboBox QAbstractItemView { background: rgba(15, 15, 25, 0.95); border:2px solid #64ffda; border-radius:8px; color:#ffffff; selection-background-color: #64ffda; selection-color: #0a0a0f; }
            QComboBox::drop-down { border: none; background: rgba(15, 15, 25, 0.8); }
            QComboBox::down-arrow { border: none; }
            QCheckBox { color:#ffffff; font-weight:bold; }
            QCheckBox::indicator { width:18px; height:18px; }
            QCheckBox::indicator:unchecked { border:2px solid #44475a; background:rgba(25,25,35,.8); border-radius:4px; }
            QCheckBox::indicator:checked { border:2px solid #64ffda; background:#64ffda; border-radius:4px; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #primaryButton:hover { border:2px solid #64ffda; background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #50e3c2, stop:1 #00acc1); }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
+            
+            /* Валидация состояний */
+            QLineEdit.error, QComboBox.error, QTextEdit.error, QSpinBox.error, QDoubleSpinBox.error {
+                border: 2px solid #ff5555 !important;
+                background: rgba(75, 25, 35, 0.8) !important;
+            }
+            
+            QLineEdit.success, QComboBox.success, QTextEdit.success, QSpinBox.success, QDoubleSpinBox.success {
+                border: 2px solid #50fa7b !important;
+                background: rgba(25, 75, 35, 0.3) !important;
+            }
+            
+            QLabel[class="error-label"] {
+                color: #ff5555 !important;
+                font-size: 11px;
+                font-family: 'Consolas', 'Fira Code', monospace;
+                padding: 2px 5px;
+                background: rgba(255, 85, 85, 0.1);
+                border-radius: 4px;
+                margin-top: 2px;
+                border-left: 3px solid #ff5555;
+            }
+            
+            QLabel[class="success-label"] {
+                color: #50fa7b !important;
+                font-size: 11px;
+                font-family: 'Consolas', 'Fira Code', monospace;
+                padding: 2px 5px;
+                background: rgba(80, 250, 123, 0.1);
+                border-radius: 4px;
+                margin-top: 2px;
+                border-left: 3px solid #50fa7b;
+            }
            
            /* Валидация состояний */
            QLineEdit.error, QComboBox.error, QTextEdit.error, QSpinBox.error, QDoubleSpinBox.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }
            
            QLineEdit.success, QComboBox.success, QTextEdit.success, QSpinBox.success, QDoubleSpinBox.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }
            
            QLabel[class="error-label"] {
                color: #ff5555 !important;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #ff5555;
            }
            
            QLabel[class="success-label"] {
                color: #50fa7b !important;
                font-size: 11px;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 2px 5px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                margin-top: 2px;
                border-left: 3px solid #50fa7b;
            }
        """)
    
    def on_fk_toggled(self, checked: bool):
        self.ref_table.setEnabled(checked)
        self.ref_column.setEnabled(checked)
    
    def _fill_ref_columns(self, table_name: str):
        self.ref_column.clear()
        if table_name:
            self.ref_column.addItems(self.db_instance.get_column_names(table_name) or [])
    
    def get_constraints(self):
        """Получить настройки ограничений."""
        return {
            'primary_key': self.pk_check.isChecked(),
            'autoincrement': self.ai_check.isChecked(),
            'unique': self.unique_check.isChecked(),
            'nullable': not self.not_null_check.isChecked() if self.not_null_check.isChecked() else (self.null_check.isChecked() if self.null_check.isChecked() else True),
            'default': self.default_edit.text().strip() or None,
            'check': self.check_edit.text().strip() or None,
            'foreign_key': f"{self.ref_table.currentText()}.{self.ref_column.currentText()}" if self.fk_check.isChecked() and self.ref_table.currentText() and self.ref_column.currentText() else None
        }

    # -------- Валидация в ConstraintsDialog --------
    @staticmethod
    def _has_dangerous_sql(text: str) -> bool:
        if not text:
            return False
        patterns = [r"--", r"/\\*", r"\\*/", r";\\s*$"]
        import re as _re
        return any(_re.search(p, text, _re.IGNORECASE) for p in patterns)

    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].show()
                # Подсветка ошибки
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def set_field_success(self, field_name, success_message):
        """Устанавливает сообщение об успехе для поля"""
        if field_name in self.error_labels:
            if success_message:
                self.error_labels[field_name].setText(success_message)
                self.error_labels[field_name].show()
                self.error_labels[field_name].setProperty("class", "success-label")
                self.error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка успеха
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setText("")
            self.error_labels[field_name].setProperty("class", "error-label")
            self.error_labels[field_name].setStyleSheet(self.styleSheet())
            # Убираем подсветку
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    def _validate_default(self):
        text = self.default_edit.text().strip()
        if not text:
            self.clear_field_error('default')
            return True
        if self._has_dangerous_sql(text):
            self.set_field_error('default', "✕ Недопустимы комментарии и ';'")
            return False
        self.set_field_success('default', "✓ Ок")
        return True

    def _validate_check(self):
        text = self.check_edit.text().strip()
        if not text:
            self.clear_field_error('check')
            return True
        if self._has_dangerous_sql(text):
            self.set_field_error('check', "✕ Недопустимы комментарии и ';'")
            return False
        # Простейшая проверка наличия оператора сравнения
        import re as _re
        if not _re.search(r"[<>=]", text):
            self.set_field_error('check', "✕ Ожидается условие сравнения")
            return False
        self.set_field_success('check', "✓ Ок")
        return True

    def _on_accept(self):
        # Валидация перед закрытием
        ok = self._validate_default() and self._validate_check()
        if self.fk_check.isChecked() and (not self.ref_table.currentText() or not self.ref_column.currentText()):
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу и столбец для FOREIGN KEY")
            return
        if ok:
            self.accept()


class AddColumnDialog(QDialog):
    """Диалог добавления столбца с поддержкой ARRAY/ENUM, компактный размер."""

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("➕ ДОБАВЛЕНИЕ СТОЛБЦА")
        self.setModal(True)
        self.resize(600, 500)  # Уменьшенный размер
        self._set_dark_palette()
        self._setup_logging()
        # Храним выбранные ранее ограничения, чтобы сохранялись между открытиями окна
        self.constraints: dict = {}
        
        # Словари для валидации
        self.input_widgets = {}
        self.error_labels = {}
        
        self.init_ui()
        self.apply_styles()

    # --- UI ---
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Заголовок
        header = QGroupBox()
        header.setObjectName("dialogHeader")
        header_l = QVBoxLayout(header)
        title = QLabel("ДОБАВЛЕНИЕ НОВОГО СТОЛБЦА")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Выберите параметры для нового столбца")
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        header_l.addWidget(title)
        header_l.addWidget(subtitle)
        layout.addWidget(header)

        # 1) Таблица
        box_table = QGroupBox("ВЫБОР ТАБЛИЦЫ")
        box_table.setObjectName("settingsGroup")
        form_table = QFormLayout(box_table)
        form_table.setLabelAlignment(Qt.AlignRight)
        self.table_combo = QComboBox()
        self.table_combo.setObjectName("fieldCombo")
        self.table_combo.addItems(self.db_instance.get_table_names() or [])
        form_table.addRow(self._label("Таблица для изменения:"), self.table_combo)
        layout.addWidget(box_table)

        # 2) Параметры
        box_params = QGroupBox("ПАРАМЕТРЫ СТОЛБЦА")
        box_params.setObjectName("settingsGroup")
        self.form_params = QFormLayout(box_params)
        self.form_params.setLabelAlignment(Qt.AlignRight)

        # Создаем контейнер для поля "Имя столбца" с валидацией
        name_container = QWidget()
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(5)
        
        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("fieldEdit")
        self.name_edit.setPlaceholderText("Например: publication_year")
        name_layout.addWidget(self.name_edit)
        
        # Метка ошибок для имени столбца
        self.name_error = QLabel()
        self.name_error.setProperty("class", "error-label")
        self.name_error.hide()
        name_layout.addWidget(self.name_error)
        
        self.form_params.addRow(self._label("Имя столбца:"), name_container)
        
        # Регистрируем виджеты для валидации
        self.input_widgets['name'] = self.name_edit
        self.error_labels['name'] = self.name_error
        
        # Валидация в реальном времени
        self.name_edit.textChanged.connect(self._validate_name_live)

        # Создаем контейнер для поля "Тип данных" с валидацией
        type_container = QWidget()
        type_layout = QVBoxLayout(type_container)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(5)
        
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("fieldCombo")
        self.type_combo.addItems([
            "String(255)", "Text", "Integer", "SmallInteger", "BigInteger",
            "Numeric(10, 2)", "Boolean", "Date", "ARRAY", "ENUM"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        # Метка ошибок для типа данных
        self.type_error = QLabel()
        self.type_error.setProperty("class", "error-label")
        self.type_error.hide()
        type_layout.addWidget(self.type_error)
        
        self.form_params.addRow(self._label("Тип данных:"), type_container)
        
        # Регистрируем виджеты для валидации
        self.input_widgets['type'] = self.type_combo
        self.error_labels['type'] = self.type_error
        
        # Валидация в реальном времени
        self.type_combo.currentTextChanged.connect(self._validate_type_live)

        # контейнер для специфики типов
        self.type_extra = QWidget()
        self.type_extra_layout = QFormLayout(self.type_extra)
        self.type_extra_layout.setContentsMargins(0, 0, 0, 0)
        self.form_params.addRow("", self.type_extra)

        # виджеты для ARRAY и ENUM
        self.array_item_combo = QComboBox()
        self.array_item_combo.addItems(["String(255)", "Integer", "Numeric(10, 2)"])
        self.array_values = ArrayLineEdit()
        self.array_values.setArray([], delimiter=":")

        self.enum_editor = EnumEditor()

        # Регистрируем дополнительные виджеты для валидации
        self.input_widgets['array_values'] = self.array_values
        self.input_widgets['enum_values'] = self.enum_editor
        
        # Создаем метки ошибок для ARRAY и ENUM
        self.array_error = QLabel()
        self.array_error.setProperty("class", "error-label")
        self.array_error.hide()
        self.error_labels['array_values'] = self.array_error
        
        self.enum_error = QLabel()
        self.enum_error.setProperty("class", "error-label")
        self.enum_error.hide()
        self.error_labels['enum_values'] = self.enum_error

        self.on_type_changed(self.type_combo.currentText())
        layout.addWidget(box_params)

        # Кнопки
        btn_row = QWidget()
        btn_l = QHBoxLayout(btn_row)
        btn_l.setContentsMargins(16, 10, 16, 10)
        self.btn_constraints = QPushButton("НАСТРОИТЬ ОГРАНИЧЕНИЯ")
        self.btn_constraints.setObjectName("secondaryButton")
        self.btn_ok = QPushButton("ДОБАВИТЬ СТОЛБЕЦ")
        self.btn_ok.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_constraints.clicked.connect(self.open_constraints)
        btn_l.addWidget(self.btn_constraints)
        btn_l.addWidget(self.btn_ok)
        btn_l.addWidget(self.btn_cancel)
        layout.addWidget(btn_row)

    def _label(self, text):
        l = QLabel(text)
        l.setObjectName("fieldLabel")
        return l

    def _setup_logging(self):
        """Настройка логирования в db/db_app.log"""
        self.logger = logging.getLogger('AddColumnDialog')
        self.logger.setLevel(logging.INFO)
        
        # Проверяем, есть ли уже обработчик
        if not self.logger.handlers:
            handler = logging.FileHandler('db/db_app.log', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def validate_column_name(self, name: str) -> tuple[bool, str]:
        """Валидация имени столбца"""
        if not name:
            return False, "Имя столбца не может быть пустым"
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            return False, "Имя столбца может содержать только буквы, цифры и подчеркивания, начинаться с буквы или _"
        
        if len(name) > 63:
            return False, "Имя столбца не может быть длиннее 63 символов"
        
        # Проверка зарезервированных слов
        reserved_words = {
            'select', 'from', 'where', 'insert', 'update', 'delete', 'create', 'drop',
            'alter', 'table', 'database', 'index', 'view', 'procedure', 'function',
            'trigger', 'constraint', 'primary', 'foreign', 'key', 'unique', 'check',
            'default', 'null', 'not', 'and', 'or', 'in', 'like', 'between', 'is'
        }
        
        if name.lower() in reserved_words:
            return False, f"'{name}' является зарезервированным словом SQL"
        
        return True, ""
    
    def validate_table_name(self, name: str) -> tuple[bool, str]:
        """Валидация имени таблицы"""
        if not name:
            return False, "Не выбрана таблица"
        
        # Проверяем, существует ли таблица
        if name not in (self.db_instance.get_table_names() or []):
            return False, f"Таблица '{name}' не существует"
        
        return True, ""

    def _set_dark_palette(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0a0a0f, stop:1 #1a1a2e); color:#ffffff; }
            #dialogHeader { background: rgba(10,10,15,.7); border:2px solid #64ffda; border-radius:12px; padding:18px; }
            #dialogTitle { font-size:20px; font-weight:bold; color:#64ffda; letter-spacing:2px; }
            #dialogSubtitle { color:#50fa7b; font-size:12px; }
            #settingsGroup { border:2px solid #44475a; border-radius:12px; padding:16px; background:rgba(15,15,25,.6); }
            #settingsGroup::title { left:18px; padding:0 8px; color:#64ffda; font-weight:bold; }
            #fieldLabel { color:#ffffff; font-weight:bold; }
            QLineEdit, QComboBox { background: rgba(15, 15, 25, 0.8); border:2px solid #44475a; border-radius:8px; padding:10px; color:#ffffff; }
            QLineEdit:focus, QComboBox:focus { border:2px solid #64ffda; }
            QComboBox QAbstractItemView { background: rgba(15, 15, 25, 0.95); border:2px solid #64ffda; border-radius:8px; color:#ffffff; selection-background-color: #64ffda; selection-color: #0a0a0f; }
            QComboBox::drop-down { border: none; background: rgba(15, 15, 25, 0.8); }
            QComboBox::down-arrow { border: none; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #primaryButton:hover { border:2px solid #64ffda; background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #50e3c2, stop:1 #00acc1); }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
+            
+            /* Стили для ArrayLineEdit и EnumEditor */
+            ArrayLineEdit.error, EnumEditor.error {
+                border: 2px solid #ff5555 !important;
+                background: rgba(75, 25, 35, 0.8) !important;
+            }
+            
+            ArrayLineEdit.success, EnumEditor.success {
+                border: 2px solid #50fa7b !important;
+                background: rgba(25, 75, 35, 0.3) !important;
+            }
+        """)

    # --- Dynamic type UI ---
    def on_type_changed(self, text: str):
        # clear
        while self.type_extra_layout.rowCount():
            self.type_extra_layout.removeRow(0)
        if text == "ARRAY":
            self.type_extra_layout.addRow(self._label("Тип элемента:"), self.array_item_combo)
            self.type_extra_layout.addRow(self._label("Пример значений:"), self.array_values)
            # Добавляем метку ошибки для ARRAY
            self.type_extra_layout.addRow("", self.array_error)
            # Подключаем валидацию
            self.array_values.textChanged.connect(self._validate_array_values)
        elif text == "ENUM":
            self.type_extra_layout.addRow(self._label("Значения ENUM:"), self.enum_editor)
            # Добавляем метку ошибки для ENUM
            self.type_extra_layout.addRow("", self.enum_error)
            # Подключаем валидацию
            self.enum_editor.valuesChanged.connect(self._validate_enum_values)

    def open_constraints(self):
        """Открыть диалог ограничений."""
        dialog = ConstraintsDialog(self.db_instance, self)
        # Если ранее пользователь уже выбирал ограничения — применим их к форме
        if self.constraints:
            try:
                dialog.pk_check.setChecked(bool(self.constraints.get('primary_key')))
                dialog.ai_check.setChecked(bool(self.constraints.get('autoincrement')))
                dialog.unique_check.setChecked(bool(self.constraints.get('unique')))
                # nullable инвертируется через not_null_check/null_check
                nullable = self.constraints.get('nullable')
                if nullable is not None:
                    dialog.not_null_check.setChecked(not nullable)
                    dialog.null_check.setChecked(bool(nullable))
                dialog.default_edit.setText(str(self.constraints.get('default') or ""))
                dialog.check_edit.setText(str(self.constraints.get('check') or ""))
                fk = self.constraints.get('foreign_key')
                if fk:
                    ref_table, ref_col = fk.split('.', 1)
                    dialog.fk_check.setChecked(True)
                    # Установим значения таблицы/столбца, если доступны
                    idx = dialog.ref_table.findText(ref_table)
                    if idx >= 0:
                        dialog.ref_table.setCurrentIndex(idx)
                        dialog._fill_ref_columns(ref_table)
                        cidx = dialog.ref_column.findText(ref_col)
                        if cidx >= 0:
                            dialog.ref_column.setCurrentIndex(cidx)
            except Exception:
                pass
        if dialog.exec() == QDialog.Accepted:
            self.constraints = dialog.get_constraints()
        else:
            self.constraints = {}

    # --- Submit ---
    def on_ok(self):
        table_name = self.table_combo.currentText().strip()
        column_name = self.name_edit.text().strip()
        dtype = self.type_combo.currentText()
        
        # Валидация всех полей
        self._validate_name_live()
        self._validate_type_live()
        
        # Валидация специфичных полей в зависимости от типа
        if dtype == "ARRAY":
            if not self._validate_array_values():
                return
        elif dtype == "ENUM":
            if not self._validate_enum_values():
                return
        
        is_valid_table, table_error = self.validate_table_name(table_name)
        if not is_valid_table:
            QMessageBox.warning(self, "Ошибка валидации", table_error)
            self.logger.warning(f"Ошибка валидации таблицы: {table_error}")
            return
        
        is_valid_column, column_error = self.validate_column_name(column_name)
        if not is_valid_column:
            QMessageBox.warning(self, "Ошибка валидации", column_error)
            self.logger.warning(f"Ошибка валидации столбца: {column_error}")
            return

        # Тип
        from sqlalchemy import String, Text, Integer, SmallInteger, BigInteger, Numeric, Boolean, Date
        from sqlalchemy import Enum as SQLEnum
        from sqlalchemy import ARRAY as SA_ARRAY

        # Используем ИНСТАНСЫ типов, иначе компиляция приведёт к ошибке TypeEngine.compile()
        base_map = {
            "String(255)": String(255),
            "Text": Text(),
            "Integer": Integer(),
            "SmallInteger": SmallInteger(),
            "BigInteger": BigInteger(),
            "Numeric(10, 2)": Numeric(10, 2),
            "Boolean": Boolean(),
            "Date": Date(),
        }
        
        try:
            if dtype == "ARRAY":
                base = base_map.get(self.array_item_combo.currentText(), String(255))
                column_type = SA_ARRAY(base)
            elif dtype == "ENUM":
                values = self.enum_editor.get_values()
                if not values:
                    QMessageBox.warning(self, "Ошибка", "Для ENUM необходимо указать хотя бы одно значение.")
                    self.logger.warning("Попытка создать ENUM без значений")
                    return
                column_type = SQLEnum(*values, name=f"enum_{column_name}")
            else:
                column_type = base_map.get(dtype, String(255))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка типа данных", f"Ошибка при создании типа данных: {str(e)}")
            self.logger.error(f"Ошибка создания типа данных: {str(e)}")
            return

        # Ограничения (по умолчанию или из диалога)
        kwargs = {}
        if hasattr(self, 'constraints'):
            constraints = self.constraints
            if constraints.get('primary_key'):
                kwargs["primary_key"] = True
            if constraints.get('autoincrement'):
                kwargs["autoincrement"] = True
            if constraints.get('unique'):
                kwargs["unique"] = True
            if constraints.get('nullable') is not None:
                kwargs["nullable"] = constraints['nullable']
            if constraints.get('default'):
                kwargs["default"] = constraints['default']
            if constraints.get('check'):
                kwargs["check"] = constraints['check']
            if constraints.get('foreign_key'):
                kwargs["foreign_key"] = constraints['foreign_key']

        # Приведение ограничений к согласованному виду
        def is_integer_dtype(t: str) -> bool:
            return t in {"Integer", "SmallInteger", "BigInteger"}

        def table_row_count(tbl: str) -> int:
            try:
                from sqlalchemy import text as _sql_text
                with self.db_instance.engine.connect() as _conn:
                    return _conn.execute(_sql_text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar() or 0
            except Exception:
                return 0

        # Если выбран PK или AUTOINCREMENT – приводим тип к целочисленному при необходимости
        if kwargs.get("primary_key") or kwargs.get("autoincrement"):
            if not is_integer_dtype(dtype):
                rc = table_row_count(table_name)
                if rc > 0:
                    QMessageBox.information(self, "Изменён тип",
                                            "Для первичного ключа в непустой таблице выбран целочисленный тип Integer.")
                    self.type_combo.setCurrentText("Integer")
                    dtype = "Integer"
                else:
                    # Пустую таблицу можно оставить как есть, но AUTOINCREMENT только для integer
                    if kwargs.get("autoincrement"):
                        self.type_combo.setCurrentText("Integer")
                        dtype = "Integer"
        if kwargs.get("primary_key"):
            # PK всегда подразумевает NOT NULL и не требует UNIQUE
            kwargs["nullable"] = False
            kwargs.pop("unique", None)

        # AUTOINCREMENT: только для целочисленных и несовместим с FK
        if kwargs.get("autoincrement"):
            if not is_integer_dtype(dtype):
                QMessageBox.warning(self, "Ошибка валидации", "AUTOINCREMENT возможен только для целочисленных типов.")
                self.logger.warning("Попытка AUTOINCREMENT для нецелочисленного типа")
                return
            if kwargs.get("foreign_key"):
                QMessageBox.warning(self, "Ошибка валидации", "AUTOINCREMENT несовместим с FOREIGN KEY.")
                return

        # Взаимные правила: AUTOINCREMENT допустим только для целочисленных типов
        if kwargs.get("autoincrement"):
            if dtype not in {"Integer", "SmallInteger", "BigInteger"}:
                QMessageBox.warning(self, "Ошибка валидации", "AUTOINCREMENT возможен только для целочисленных типов.")
                self.logger.warning("Попытка AUTOINCREMENT для нецелочисленного типа")
                return

        # Если таблица непуста и NOT NULL без DEFAULT — ослабляем до NULL, чтобы избежать NotNullViolation
        try:
            from sqlalchemy import text as _sql_text
            # Ослабляем NOT NULL только когда это не PK-сценарий — при PK мы заполним значения сами
            if kwargs.get("nullable") is False and not kwargs.get("default") and not kwargs.get("primary_key"):
                with self.db_instance.engine.connect() as _conn:
                    rc = _conn.execute(_sql_text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar() or 0
                if rc > 0:
                    self.logger.warning("Таблица непуста — NOT NULL без DEFAULT понижен до NULL")
                    QMessageBox.warning(self, "Предупреждение",
                                        "Таблица содержит данные. NOT NULL без значения по умолчанию недопустим.\n"
                                        "Ограничение будет временно ослаблено до NULL.")
                    kwargs["nullable"] = True
        except Exception:
            pass

        # Логирование попытки добавления
        self.logger.info(f"Попытка добавления столбца '{column_name}' в таблицу '{table_name}' с типом '{dtype}'")
        
        try:
            success = self.db_instance.add_column(table_name, column_name, column_type, **kwargs)
            if success:
                QMessageBox.information(self, "Успех", f"Столбец '{column_name}' успешно добавлен в таблицу '{table_name}'.")
                self.logger.info(f"Столбец '{column_name}' успешно добавлен в таблицу '{table_name}'")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить столбец. Проверьте параметры.")
                self.logger.error(f"Не удалось добавить столбец '{column_name}' в таблицу '{table_name}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при добавлении столбца: {str(e)}")
            self.logger.error(f"Ошибка БД при добавлении столбца '{column_name}': {str(e)}")


    def set_field_error(self, field_name, error_message):
        """Устанавливает сообщение об ошибке для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].show()
                self.error_labels[field_name].setProperty("class", "error-label")
                self.error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка ошибки
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def set_field_success(self, field_name, success_message):
        """Устанавливает сообщение об успехе для поля"""
        if field_name in self.error_labels:
            if success_message:
                self.error_labels[field_name].setText(success_message)
                self.error_labels[field_name].show()
                self.error_labels[field_name].setProperty("class", "success-label")
                self.error_labels[field_name].setStyleSheet(self.styleSheet())
                # Подсветка успеха
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)

    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setText("")
            self.error_labels[field_name].setProperty("class", "error-label")
            self.error_labels[field_name].setStyleSheet(self.styleSheet())
            # Убираем подсветку
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    # --- Realtime name validation ---
    def _validate_name_live(self):
        name = self.name_edit.text().strip()
        ok, msg = self.validate_column_name(name)
        if ok:
            self.set_field_success('name', "✓ Валидное имя столбца")
        else:
            self.set_field_error('name', f"✕ {msg}")
    
    def _validate_type_live(self):
        """Валидация типа данных в реальном времени"""
        type_text = self.type_combo.currentText()
        
        # Проверяем, что выбран валидный тип
        valid_types = [
            "String(255)", "Text", "Integer", "SmallInteger", "BigInteger",
            "Numeric(10, 2)", "Boolean", "Date", "ARRAY", "ENUM"
        ]
        
        if type_text in valid_types:
            # Дополнительные проверки для специфичных типов
            if type_text == "ARRAY":
                self.set_field_success('type', "✓ Массив - укажите тип элементов")
            elif type_text == "ENUM":
                self.set_field_success('type', "✓ Перечисление - укажите значения")
            elif type_text == "Numeric(10, 2)":
                self.set_field_success('type', "✓ Число с точностью (10,2)")
            elif type_text == "String(255)":
                self.set_field_success('type', "✓ Строка до 255 символов")
            else:
                self.set_field_success('type', f"✓ {type_text}")
        else:
            self.set_field_error('type', "✕ Выберите валидный тип данных")
    
    def _validate_array_values(self):
        """Валидация значений ARRAY"""
        try:
            values = self.array_values.getArray()
            if not values:
                self.set_field_success('array_values', "✓ Пустой массив (допустимо)")
                return True
            
            # Проверяем тип элементов
            item_type = self.array_item_combo.currentText()
            validated_items = []
            
            for i, item in enumerate(values):
                if item_type == "Integer":
                    if not str(item).isdigit() and not (str(item).startswith('-') and str(item)[1:].isdigit()):
                        self.set_field_error('array_values', f"✕ Элемент {i+1} должен быть целым числом")
                        return False
                    validated_items.append(int(item))
                elif item_type == "Numeric(10, 2)":
                    try:
                        float(item)
                    except ValueError:
                        self.set_field_error('array_values', f"✕ Элемент {i+1} должен быть числом")
                        return False
                    validated_items.append(float(item))
                else:  # String
                    if len(str(item)) > 255:
                        self.set_field_error('array_values', f"✕ Элемент {i+1} слишком длинный (макс. 255 символов)")
                        return False
                    validated_items.append(str(item))
            
            self.set_field_success('array_values', f"✓ {len(validated_items)} элементов")
            return True
            
        except Exception as e:
            self.set_field_error('array_values', f"✕ Ошибка валидации: {str(e)}")
            return False
    
    def _validate_enum_values(self):
        """Валидация значений ENUM"""
        try:
            values = self.enum_editor.get_values()
            if not values:
                self.set_field_error('enum_values', "✕ ENUM должен содержать хотя бы одно значение")
                return False
            
            # Проверяем на дубликаты
            if len(values) != len(set(values)):
                self.set_field_error('enum_values', "✕ ENUM не может содержать дубликаты")
                return False
            
            # Проверяем длину значений
            for i, value in enumerate(values):
                if len(str(value)) > 255:
                    self.set_field_error('enum_values', f"✕ Значение {i+1} слишком длинное (макс. 255 символов)")
                    return False
                if not str(value).strip():
                    self.set_field_error('enum_values', f"✕ Значение {i+1} не может быть пустым")
                    return False
            
            self.set_field_success('enum_values', f"✓ {len(values)} значений")
            return True
            
        except Exception as e:
            self.set_field_error('enum_values', f"✕ Ошибка валидации: {str(e)}")
            return False
