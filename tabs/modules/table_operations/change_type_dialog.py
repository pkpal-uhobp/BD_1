from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QFormLayout, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from .add_column import ConstraintsDialog


class ChangeTypeDialog(QDialog):
    """Диалог изменения типа столбца с поддержкой USING выражения."""

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("ИЗМЕНЕНИЕ ТИПА СТОЛБЦА")
        self.setModal(True)
        self.setFixedSize(600, 600)
        self._set_dark_palette()
        self._init_ui()
        self._apply_styles()

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
            #fieldLabel { color:#ffffff; font-weight:bold; }
            #settingsGroup QLabel { color:#50fa7b; font-weight:bold; }
            QLineEdit, QComboBox { background: rgba(15, 15, 25, 0.8); border:2px solid #44475a; border-radius:8px; padding:10px; color:#ffffff; }
            QLineEdit:focus, QComboBox:focus { border:2px solid #64ffda; }
            QComboBox QAbstractItemView { background: rgba(15, 15, 25, 0.95); border:2px solid #64ffda; border-radius:8px; color:#ffffff; selection-background-color: #64ffda; selection-color: #0a0a0f; outline: none; }
            QComboBox::drop-down { border: none; background: rgba(15, 15, 25, 0.8); }
            QComboBox::down-arrow { border: none; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
        """)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        header = QGroupBox()
        header.setObjectName("dialogHeader")
        hl = QVBoxLayout(header)
        t = QLabel("ИЗМЕНЕНИЕ ТИПА СТОЛБЦА")
        t.setObjectName("dialogTitle")
        t.setAlignment(Qt.AlignCenter)
        hl.addWidget(t)
        root.addWidget(header)

        box = QGroupBox("НАСТРОЙКА")
        box.setObjectName("settingsGroup")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)

        self.table_combo = QComboBox()
        self.table_combo.addItems(self.db_instance.get_table_names() or [])
        self.column_combo = QComboBox()
        self._fill_columns(self.table_combo.currentText())
        self.table_combo.currentTextChanged.connect(self._fill_columns)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "String(255)", "TEXT", "INTEGER", "SMALLINT", "BIGINT", "NUMERIC(10,2)", "DATE", "BOOLEAN",
            "ARRAY", "ENUM"
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)

        # Доп. параметры для ARRAY/ENUM
        self.array_base_combo = QComboBox()
        self.array_base_combo.addItems(["String(255)", "TEXT", "INTEGER", "NUMERIC(10,2)"])
        self.array_base_combo.setVisible(False)

        # Кнопка: дополнительные ограничения
        self.btn_constraints = QPushButton("ОГРАНИЧЕНИЯ")
        self.btn_constraints.setObjectName("secondaryButton")
        self.btn_constraints.clicked.connect(self._open_constraints_window)

        form.addRow(QLabel("Таблица:"), self.table_combo)
        form.addRow(QLabel("Столбец:"), self.column_combo)
        form.addRow(QLabel("Новый тип:"), self.type_combo)
        self.array_label = QLabel("Элемент ARRAY:")
        # Поле имени ENUM убираем — тип создаётся автоматически
        self.array_label.setVisible(False)
        form.addRow(self.array_label, self.array_base_combo)

        # Убираем управление ограничениями из этого окна — оставляем только смену типа и USING
        root.addWidget(box)
        root.addWidget(self.btn_constraints)

        btn_row = QWidget()
        bl = QHBoxLayout(btn_row)
        bl.addStretch()
        ok = QPushButton("ИЗМЕНИТЬ")
        ok.setObjectName("primaryButton")
        cancel = QPushButton("✖ ОТМЕНА")
        cancel.setObjectName("secondaryButton")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self._on_ok)
        bl.addWidget(ok)
        bl.addWidget(cancel)
        root.addWidget(btn_row)

    def _fill_columns(self, table_name: str):
        self.column_combo.clear()
        if not table_name:
            return
        self.column_combo.addItems(self.db_instance.get_column_names(table_name) or [])

    def _on_type_changed(self, text: str):
        """Изменяет видимость дополнительных полей при выборе ARRAY или ENUM."""
        is_array = text.strip().upper() == "ARRAY"
        is_enum = text.strip().upper() == "ENUM"

        # Показываем выбор базового типа только для ARRAY
        self.array_base_combo.setVisible(is_array)
        self.array_label.setVisible(is_array)
        # Для ENUM ничего не показываем
    def _on_ok(self):
        table = self.table_combo.currentText().strip()
        column = self.column_combo.currentText().strip()
        sel = self.type_combo.currentText().strip()

        # Проверяем, является ли исходный столбец массивом
        source_is_array = False
        try:
            from sqlalchemy import inspect
            inspector = inspect(self.db_instance.engine)
            for c in inspector.get_columns(table):
                if c.get("name", "").lower() == column.lower():
                    t_str = str(c.get("type", "")).lower()
                    if "[]" in t_str or "array" in t_str:
                        source_is_array = True
                    break
        except Exception:
            pass

        # Сформируем фактический тип SQL
        if sel == "ARRAY":
            base = self.array_base_combo.currentText().strip() or "TEXT"
            base_sql = "VARCHAR(255)" if base == "String(255)" else base
            new_type = f"{base_sql}[]"
        elif sel == "ENUM":
            new_type = "__AUTO_ENUM__"
        else:
            new_type = "VARCHAR(255)" if sel == "String(255)" else sel

        # Блокируем изменение массива
        if source_is_array:
            QMessageBox.warning(
                self,
                "Ограничение",
                f"Столбец '{column}' является массивом.\n"
                f"Изменение типа массивов не поддерживается."
            )
            return

        if not table or not column or not new_type:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу, столбец и новый тип")
            return

        # Меняем тип
        if new_type:
            ok = self.db_instance.alter_column_type(table, column, new_type, None)
            if ok is True:
                QMessageBox.information(self, "Успех", f"Тип '{table}.{column}' изменён на {new_type}")
                self.accept()
            elif isinstance(ok, str):
                # Если метод вернул текст причины отказа
                QMessageBox.warning(
                    self,
                    "Изменение недоступно",
                    f"Столбец '{column}' нельзя изменить:\n\n{ok}"
                )
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось изменить тип столбца. См. логи.")

    def _open_constraints_window(self):
        table_name = self.table_combo.currentText().strip()
        column_name = self.column_combo.currentText().strip()
        
        if not table_name or not column_name:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу и столбец")
            return
            
        try:
            dlg = ConstraintsDialog(self.db_instance, self)
            dlg.show()  # Показываем диалог
            if dlg.exec() == QDialog.Accepted:
                cons = dlg.get_constraints()
                # Применим изменения к столбцу: NOT NULL, DEFAULT, UNIQUE, CHECK
                set_nn = None if cons.get('nullable') is None else (not cons['nullable'])
                default_value = ...
                if cons.get('default') is not None:
                    default_value = cons['default']
                unique = cons.get('unique') if 'unique' in cons else None
                check_expr = cons.get('check') if 'check' in cons else None
                ok = self.db_instance.alter_column_constraints(
                    self.table_combo.currentText().strip(),
                    self.column_combo.currentText().strip(),
                    nullable=set_nn,
                    default=default_value,
                    check_condition=check_expr
                )
                if ok:
                    QMessageBox.information(self, "Успех", "Ограничения применены")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось применить ограничения")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог ограничений: {str(e)}")



