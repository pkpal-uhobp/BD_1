from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QWidget, QComboBox, QLineEdit, QMessageBox,
    QGroupBox, QFormLayout, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import QRegularExpression


class RenameDialog(QDialog):
    """Диалог выбора: переименовать таблицу или столбец."""

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("Переименование: таблица или столбец")
        self.setModal(True)
        self.setFixedSize(650, 650)  # Фиксированный размер

        self.set_dark_palette()
        self.init_ui()
        self.apply_styles()

    def set_dark_palette(self):
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
        # Стиль максимально приближен к get_table.apply_styles
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f,
                                          stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
                border-radius: 12px;
            }
            #title {
                color: #64ffda;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 10px;
            }
            QLabel {
                color: #64ffda;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px 0;
            }
            #fieldLabel { color: #50fa7b; }
            QRadioButton {
                color: #8892b0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                spacing: 10px;
                padding: 8px 0;
            }
            QRadioButton::indicator {
                width: 20px; height: 20px; border: 2px solid #44475a; border-radius: 10px;
                background: rgba(15, 15, 25, 0.8);
            }
            QRadioButton::indicator:hover { border: 2px solid #6272a4; }
            QRadioButton::indicator:checked { background: #64ffda; border: 2px solid #64ffda; }

            QGroupBox#tableContainer {
                background: rgba(15, 15, 25, 0.6);
                border: none;
                padding: 15px;
                margin: 5px 0;
            }

            QComboBox, QLineEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 20px;
            }
            QComboBox:hover { border: 2px solid #6272a4; }
            QComboBox:focus, QLineEdit:focus { border: 2px solid #64ffda; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64ffda;
                width: 0px; height: 0px;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 15, 25, 0.95);
                border: 2px solid #64ffda;
                border-radius: 8px;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                outline: none;
            }
            #errorLabel {
                color: #ff5555;
                font-size: 11px;
                font-weight: bold;
                padding: 3px 5px;
                background: rgba(255, 85, 85, 0.1);
                border-radius: 4px;
                border-left: 3px solid #ff5555;
                margin-top: 2px;
                min-height: 18px;
            }
            #successLabel {
                color: #50fa7b;
                font-size: 11px;
                font-weight: bold;
                padding: 3px 5px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                border-left: 3px solid #50fa7b;
                margin-top: 2px;
                min-height: 18px;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, stop: 1 #00bcd4);
                border: none; border-radius: 10px; color: #0a0a0f; font-size: 14px;
                font-weight: bold; padding: 12px; text-transform: uppercase; letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace; min-height: 30px; min-width: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, stop: 1 #00838f);
            }
            #btn_cancel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, stop: 1 #ff5252);
                color: #0a0a0f;
            }

            QCheckBox { color: #f8f8f2; font-family: 'Consolas', 'Fira Code', monospace; spacing: 8px; font-size: 14px; }
            QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid #44475a; border-radius: 4px; background: rgba(25,25,35,0.8); }
            QCheckBox::indicator:hover { border: 2px solid #6272a4; }
            QCheckBox::indicator:checked { background: #64ffda; border: 2px solid #64ffda; }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        title = QLabel("ПАРАМЕТРЫ ПЕРЕИМЕНОВАНИЯ")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 16, QFont.Bold))
        title.setObjectName("title")
        layout.addWidget(title)

        # Выбор режима
        mode_widget = QWidget()
        mode_layout = QHBoxLayout(mode_widget)
        self.rb_table = QRadioButton("Таблицу")
        self.rb_column = QRadioButton("Столбец")
        self.rb_table.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.rb_table)
        self.mode_group.addButton(self.rb_column)
        mode_layout.addWidget(QLabel("Переименовать:"))
        mode_layout.addWidget(self.rb_table)
        mode_layout.addWidget(self.rb_column)
        mode_layout.addStretch()
        layout.addWidget(mode_widget)

        # Блок переименования таблицы
        self.table_group = QGroupBox()
        self.table_group.setObjectName("tableContainer")
        table_form = QFormLayout(self.table_group)
        table_form.setLabelAlignment(Qt.AlignRight)
        self.table_combo = QComboBox()
        self.table_combo.addItems(self.db_instance.get_table_names() or [])
        self.table_new_name = QLineEdit()
        self.table_new_name.setPlaceholderText("Новое имя таблицы")
        # Регекc для проверки, но ввод не ограничиваем
        self._name_regex = QRegularExpression(r"^[A-Za-z_][A-Za-z0-9_]*$")
        self.table_error = QLabel("")
        self.table_error.setObjectName("errorLabel")
        self.table_error.setVisible(False)
        self.table_success = QLabel("")
        self.table_success.setObjectName("successLabel")
        self.table_success.setVisible(False)
        table_form.addRow(self._label("Таблица:"), self.table_combo)
        table_form.addRow(self._label("Новое имя:"), self.table_new_name)
        table_form.addRow("", self.table_error)
        table_form.addRow("", self.table_success)
        layout.addWidget(self.table_group)

        # Блок переименования столбца
        self.column_group = QGroupBox()
        self.column_group.setObjectName("tableContainer")
        col_form = QFormLayout(self.column_group)
        col_form.setLabelAlignment(Qt.AlignRight)
        self.col_table_combo = QComboBox()
        self.col_table_combo.addItems(self.db_instance.get_table_names() or [])
        self.col_column_combo = QComboBox()
        self.col_column_combo.setMaxVisibleItems(8)
        self.col_new_name = QLineEdit()
        self.col_new_name.setPlaceholderText("Новое имя столбца")
        self.col_display_name = QLineEdit()
        self.col_display_name.setPlaceholderText("Отображаемое имя (RU)")
        self.only_display_check = QCheckBox("Менять только отображаемое имя (RU)")
        self.only_display_check.toggled.connect(self.on_only_display_toggled)
        self.col_error_name = QLabel("")
        self.col_error_name.setObjectName("errorLabel")
        self.col_error_name.setVisible(False)
        self.col_error_ru = QLabel("")
        self.col_error_ru.setObjectName("errorLabel")
        self.col_error_ru.setVisible(False)
        self.col_success_name = QLabel("")
        self.col_success_name.setObjectName("successLabel")
        self.col_success_name.setVisible(False)
        self.col_success_ru = QLabel("")
        self.col_success_ru.setObjectName("successLabel")
        self.col_success_ru.setVisible(False)
        col_form.addRow(self._label("Таблица:"), self.col_table_combo)
        col_form.addRow(self._label("Столбец:"), self.col_column_combo)
        col_form.addRow(self._label("Новое имя:"), self.col_new_name)
        col_form.addRow("", self.col_error_name)
        col_form.addRow("", self.col_success_name)
        col_form.addRow(self._label("Отображаемое имя (RU):"), self.col_display_name)
        col_form.addRow("", self.col_error_ru)
        col_form.addRow("", self.col_success_ru)
        col_form.addRow(QWidget(), self.only_display_check)
        layout.addWidget(self.column_group)

        # Первичное заполнение столбцов и обработчик смены таблицы
        self.update_columns_for_table(self.col_table_combo.currentText())
        self.col_table_combo.currentTextChanged.connect(self.update_columns_for_table)
        self.col_column_combo.currentTextChanged.connect(self.on_column_changed)

        # realtime-валидация
        self.table_new_name.textChanged.connect(self.validate_table_section)
        self.col_new_name.textChanged.connect(self.validate_column_section)
        self.col_display_name.textChanged.connect(self.validate_column_section)
        self.only_display_check.toggled.connect(self.validate_column_section)
        # Не вызываем валидацию сразу - только при изменении текста

        # Кнопки
        buttons = QHBoxLayout()
        buttons.addStretch()
        self.btn_ok = QPushButton("ОК")
        self.btn_ok.setEnabled(False)  # Изначально неактивна
        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)

        # Переключение режимов
        self.rb_table.toggled.connect(self.update_mode)
        self.rb_column.toggled.connect(self.update_mode)
        self.update_mode()

    def update_mode(self):
        is_table = self.rb_table.isChecked()
        self.table_group.setVisible(is_table)
        self.column_group.setVisible(not is_table)

    def on_ok(self):
        if self.rb_table.isChecked():
            old_name = self.table_combo.currentText().strip()
            new_name = self.table_new_name.text().strip()
            self._clear_table_error()
            if not old_name or not new_name:
                self._set_table_error("Укажите таблицу и новое имя")
                return
            if old_name == new_name:
                self._set_table_error("Новое имя совпадает со старым")
                return
            ok = self.db_instance.rename_table(old_name, new_name)
            if ok:
                self.accept()
            else:
                self._set_table_error("Не удалось переименовать таблицу. См. логи.")
        else:
            # Переименование столбца или смена RU-имени
            table_name = self.col_table_combo.currentText().strip()
            old_col = self.col_column_combo.currentText().strip()
            new_col = self.col_new_name.text().strip()
            self._clear_column_errors()
            if not table_name or not old_col or not new_col:
                if not self.only_display_check.isChecked():
                    self._set_col_name_error("Укажите таблицу, столбец и новое имя")
                    return
            # Только смена RU-имени
            if self.only_display_check.isChecked():
                ru_val = self.col_display_name.text().strip()
                if not ru_val:
                    self._set_col_ru_error("Укажите отображаемое имя (RU)")
                    return
                parent = self.parent()
                if parent and hasattr(parent, 'COLUMN_HEADERS_MAP'):
                    headers = getattr(parent, 'COLUMN_HEADERS_MAP')
                    # если ключ уже переименован ранее, используем существующий
                    headers[old_col] = ru_val
                    if hasattr(parent, 'REVERSE_COLUMN_HEADERS_MAP'):
                        parent.REVERSE_COLUMN_HEADERS_MAP = {v: k for k, v in headers.items()}
                self.accept()
                return
            if old_col == new_col:
                self._set_col_name_error("Новое имя совпадает со старым")
                return
            # Предварительная проверка на конфликт имен
            columns = self.db_instance.get_column_names(table_name) or []
            if new_col in columns:
                self._set_col_name_error("Столбец с таким именем уже существует")
                return
            ok = self.db_instance.rename_column(table_name, old_col, new_col)
            if ok:
                # Обновляем COLUMN_HEADERS_MAP у главного окна (если есть)
                parent = self.parent()
                if parent and hasattr(parent, 'COLUMN_HEADERS_MAP'):
                    headers = getattr(parent, 'COLUMN_HEADERS_MAP')
                    ru_name = self.col_display_name.text().strip() or headers.get(old_col) or new_col
                    if old_col in headers:
                        headers.pop(old_col)
                    headers[new_col] = ru_name
                    if hasattr(parent, 'REVERSE_COLUMN_HEADERS_MAP'):
                        parent.REVERSE_COLUMN_HEADERS_MAP = {v: k for k, v in headers.items()}
                self.accept()
            else:
                self._set_col_name_error("Не удалось переименовать столбец. См. логи.")

    def update_columns_for_table(self, table_name: str):
        self.col_column_combo.clear()
        if not table_name:
            return
        columns = self.db_instance.get_column_names(table_name) or []
        self.col_column_combo.addItems(columns)
        # авто-подстановка текущего имени в поле нового имени
        if columns:
            self.col_new_name.setText(columns[0])
            # а также подставим RU имя из COLUMN_HEADERS_MAP
            self.on_column_changed(columns[0])

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def on_column_changed(self, column_name: str):
        if column_name:
            self.col_new_name.setText(column_name)
            # Подставляем текущее русское имя из родителя, если есть
            parent = self.parent()
            if parent and hasattr(parent, 'COLUMN_HEADERS_MAP'):
                ru = parent.COLUMN_HEADERS_MAP.get(column_name, column_name)
                self.col_display_name.setText(ru)

    def on_only_display_toggled(self, checked: bool):
        # Если меняем только RU-имя — блокируем поле нового технического имени, чтобы не путать
        self.col_new_name.setEnabled(not checked)

    # --- Helpers for inline errors (как в main.py) ---
    def _set_table_error(self, text: str):
        self.table_error.setText(text)
        self.table_error.setVisible(True)
        self._set_field_error_style(self.table_new_name, True)
        self.table_success.setVisible(False)

    def _clear_table_error(self):
        self.table_error.setVisible(False)
        self.table_error.setText("")
        self._set_field_error_style(self.table_new_name, False)
        self.table_success.setVisible(False)

    def _set_table_success(self, text: str):
        self.table_success.setText(text)
        self.table_success.setVisible(True)
        self._set_field_success_style(self.table_new_name, True)

    def _set_col_name_error(self, text: str):
        self.col_error_name.setText(text)
        self.col_error_name.setVisible(True)
        self._set_field_error_style(self.col_new_name, True)
        self.col_success_name.setVisible(False)

    def _set_col_ru_error(self, text: str):
        self.col_error_ru.setText(text)
        self.col_error_ru.setVisible(True)
        self._set_field_error_style(self.col_display_name, True)
        self.col_success_ru.setVisible(False)

    def _clear_column_errors(self):
        self.col_error_name.setVisible(False)
        self.col_error_name.setText("")
        self.col_error_ru.setVisible(False)
        self.col_error_ru.setText("")
        self._set_field_error_style(self.col_new_name, False)
        self._set_field_error_style(self.col_display_name, False)
        self.col_success_name.setVisible(False)
        self.col_success_ru.setVisible(False)

    def _set_field_error_style(self, field, has_error):
        if has_error:
            field.setStyleSheet("""
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #ff5555;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #ff5555;
                selection-color: #0a0a0f;
            """)
        else:
            field.setStyleSheet("")

    def _set_field_success_style(self, field, on: bool):
        if on:
            field.setStyleSheet("""
                background: rgba(25, 35, 30, 0.8);
                border: 2px solid #50fa7b;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            """)
        else:
            field.setStyleSheet("")

    # --- Validation helpers ---
    def _find_forbidden(self, text: str):
        forbidden = ['"', "'", '`', ';', '--', '/*', '*/']
        used = [sym for sym in forbidden if sym in text] if text else []
        return used

    def validate_table_section(self):
        self._clear_table_error()
        new_name = self.table_new_name.text().strip()
        if not new_name:
            self._set_table_error("Укажите новое имя таблицы")
            return False
        # regex already attached; show friendly messages
        if not self._name_regex.match(new_name).hasMatch():
            self._set_table_error("Имя: только A-z, 0-9, _, начинаться с буквы/_.")
            return False
        used = self._find_forbidden(new_name)
        if used:
            self._set_table_error(f"Запрещённые символы: {', '.join(used)}")
            return False
        self._clear_table_error()
        self._set_table_success("Имя корректно")
        self._update_ok_state()
        return True

    def validate_column_section(self):
        self._clear_column_errors()
        # RU field validation first
        ru = self.col_display_name.text().strip()
        used_ru = self._find_forbidden(ru)
        if used_ru:
            self._set_col_ru_error(f"Запрещённые символы: {', '.join(used_ru)}")
        if not self.only_display_check.isChecked():
            new_col = self.col_new_name.text().strip()
            if not new_col:
                self._set_col_name_error("Укажите новое имя столбца")
                return False
            if not self._name_regex.match(new_col).hasMatch():
                self._set_col_name_error("Имя: только A-z, 0-9, _, начинаться с буквы/_.")
                return False
            used = self._find_forbidden(new_col)
            if used:
                self._set_col_name_error(f"Запрещённые символы: {', '.join(used)}")
                return False
            self.col_success_name.setText("Имя корректно")
            self.col_success_name.setVisible(True)
            self._set_field_success_style(self.col_new_name, True)
        if ru and not used_ru:
            self.col_success_ru.setText("Отображаемое имя корректно")
            self.col_success_ru.setVisible(True)
            self._set_field_success_style(self.col_display_name, True)
        self._update_ok_state()
        return True

    def _update_ok_state(self):
        # Проверяем валидность без показа ошибок
        if self.rb_table.isChecked():
            new_name = self.table_new_name.text().strip()
            valid_table = bool(new_name and self._name_regex.match(new_name).hasMatch() and not self._find_forbidden(new_name))
        else:
            valid_table = True
            
        if self.rb_column.isChecked():
            if self.only_display_check.isChecked():
                valid_col = bool(self.col_display_name.text().strip())
            else:
                new_col = self.col_new_name.text().strip()
                valid_col = bool(new_col and self._name_regex.match(new_col).hasMatch() and not self._find_forbidden(new_col))
        else:
            valid_col = True
            
        if hasattr(self, 'btn_ok'):
            self.btn_ok.setEnabled(valid_table and valid_col)


