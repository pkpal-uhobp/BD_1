from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QFormLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor


class DropColumnDialog(QDialog):
    """Диалог удаления столбца с подтверждением и красивым тёмным UI."""

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.setWindowTitle("🗑 УДАЛЕНИЕ СТОЛБЦА")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self._set_dark_palette()

        self._init_ui()
        self._apply_styles()

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

    def _apply_styles(self):
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
            QComboBox QAbstractItemView { background: rgba(15, 15, 25, 0.95); border: 2px solid #64ffda; border-radius: 8px; color: #f8f8f2; selection-background-color: #64ffda; selection-color: #0a0a0f; outline: none; }
            #warningBox { border:2px solid #ffb86c; border-radius:12px; padding:16px; background: rgba(255, 184, 108, 0.08); }
            #warningTitle { color:#ffb86c; font-weight:bold; }
            #dangerText { color:#ff5555; font-weight:bold; }
            #primaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #64ffda, stop:1 #00bcd4); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 24px; }
            #primaryButton:hover { border:2px solid #64ffda; background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #50e3c2, stop:1 #00acc1); }
            #secondaryButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff6b6b, stop:1 #ff5252); border:none; border-radius:10px; color:#0a0a0f; font-weight:bold; padding:12px 20px; }
        """)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        header = QGroupBox()
        header.setObjectName("dialogHeader")
        header_l = QVBoxLayout(header)
        title = QLabel("УДАЛЕНИЕ СТОЛБЦА")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Выберите таблицу и столбец.\nЕсли найдены зависимости — CASCADE применится автоматически.")
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        header_l.addWidget(title)
        header_l.addWidget(subtitle)
        root.addWidget(header)

        box_select = QGroupBox("📋 ВЫБОР ТАБЛИЦЫ И СТОЛБЦА")
        box_select.setObjectName("settingsGroup")
        form = QFormLayout(box_select)
        form.setLabelAlignment(Qt.AlignRight)

        self.table_combo = QComboBox()
        self.table_combo.addItems(self.db_instance.get_table_names() or [])
        self.column_combo = QComboBox()
        self._fill_columns(self.table_combo.currentText())
        self.table_combo.currentTextChanged.connect(self._fill_columns)
        # обновляем сведения о зависимостях при смене столбца
        self.column_combo.currentTextChanged.connect(self._on_column_changed)
        form.addRow(self._label("Таблица:"), self.table_combo)
        form.addRow(self._label("Столбец:"), self.column_combo)
        root.addWidget(box_select)

        # Блок предупреждения убран по требованию — удаление необратимо, CASCADE определяется автоматически

        btn_row = QWidget()
        btn_l = QHBoxLayout(btn_row)
        btn_l.setContentsMargins(0, 0, 0, 0)
        btn_l.addStretch()
        self.btn_ok = QPushButton("🗑 УДАЛИТЬ")
        self.btn_ok.setObjectName("primaryButton")
        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._on_delete)
        btn_l.addWidget(self.btn_ok)
        btn_l.addWidget(self.btn_cancel)
        root.addWidget(btn_row)

    def _label(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setObjectName("fieldLabel")
        return l

    def _fill_columns(self, table_name: str):
        self.column_combo.clear()
        if not table_name:
            return
        self.column_combo.addItems(self.db_instance.get_column_names(table_name) or [])
        # после заполнения столбцов обновим состояние зависимостей
        self._on_column_changed(self.column_combo.currentText())

    def _on_column_changed(self, column_name: str):
        """Показывает зависимости и при их наличии принудительно включает CASCADE."""
        table = self.table_combo.currentText().strip()
        if not table or not column_name:
            return
        deps = self.db_instance.get_column_dependencies(table, column_name) or {}
        total = sum(len(v) for v in deps.values())
        # Информационный блок убран — поведение CASCADE остаётся автоматическим без доп. UI

    def _on_delete(self):
        table = self.table_combo.currentText().strip()
        column = self.column_combo.currentText().strip()
        # определяем необходимость CASCADE автоматически по зависимостям
        deps = self.db_instance.get_column_dependencies(table, column) or {}
        total = sum(len(v) for v in deps.values())
        cascade = total > 0

        if not table or not column:
            QMessageBox.warning(self, "Ошибка", "Укажите таблицу и столбец для удаления")
            return

        message = (
            f"Удалить столбец '{column}' из таблицы '{table}'" +
            (" с зависимостями (CASCADE)" if cascade else "") +
            "?\nЭто действие необратимо."
        )
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            ok = self.db_instance.drop_column_safe(table, column, force=cascade)
            # если обнаружили зависимые объекты уже на этапе БД — повторяем с CASCADE
            if not ok and not cascade:
                ok = self.db_instance.drop_column_safe(table, column, force=True)
            if ok:
                QMessageBox.information(self, "Успех", f"Столбец '{column}' удалён из '{table}'.")
                parent = self.parent()
                if parent and hasattr(parent, 'COLUMN_HEADERS_MAP'):
                    headers = getattr(parent, 'COLUMN_HEADERS_MAP')
                    if column in headers:
                        headers.pop(column)
                    if hasattr(parent, 'REVERSE_COLUMN_HEADERS_MAP'):
                        parent.REVERSE_COLUMN_HEADERS_MAP = {v: k for k, v in headers.items()}
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить столбец. См. логи.")
        except Exception as e:
            # На случай исключений драйвера: попытаться повторить с CASCADE один раз
            if not cascade:
                try:
                    ok_retry = self.db_instance.drop_column_safe(table, column, force=True)
                    if ok_retry:
                        QMessageBox.information(self, "Успех", f"Столбец '{column}' удалён из '{table}' (CASCADE).")
                        parent = self.parent()
                        if parent and hasattr(parent, 'COLUMN_HEADERS_MAP'):
                            headers = getattr(parent, 'COLUMN_HEADERS_MAP')
                            if column in headers:
                                headers.pop(column)
                            if hasattr(parent, 'REVERSE_COLUMN_HEADERS_MAP'):
                                parent.REVERSE_COLUMN_HEADERS_MAP = {v: k for k, v in headers.items()}
                        self.accept()
                        return
                except Exception:
                    pass
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при удалении столбца: {str(e)}")


