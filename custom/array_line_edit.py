# custom/array_line_edit.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QTextEdit, QLineEdit,
    QDateTimeEdit, QFrame, QSizePolicy, QToolTip
)
from PySide6.QtCore import QDate, QDateTime, Qt, Signal, QPoint
from PySide6.QtGui import QFont, QPalette, QColor, QCursor
from plyer import notification


class ArrayLineEdit(QLineEdit):
    """
    Кастомный QLineEdit для работы с массивами.
    Не редактируется напрямую, а открывает диалоговое окно для редактирования.
    """
    arrayChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.array_values = []
        self.delimiter = ":"
        self.item_constraints = {}

        # Стили такие же, как в AddRecordDialog
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }

            QLineEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }

            QLineEdit.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }
        """)

        self.setPlaceholderText("Нажмите для редактирования массива...")
        self.setToolTip("Нажмите, чтобы открыть редактор массива")

    def setItemConstraints(self, constraints: dict):
        """Сохраняет ограничения для элементов массива."""
        self.item_constraints = constraints or {}

    def mousePressEvent(self, event):
        """Открывает диалог при нажатии"""
        if event.button() == Qt.LeftButton:
            self.openArrayDialog()
        super().mousePressEvent(event)

    def setArray(self, values, delimiter=":"):
        """Обновляет отображение массива"""
        self.array_values = values or []
        self.delimiter = delimiter or ":"
        self.updateDisplay()

    def getArray(self):
        """Возвращает текущее значение массива"""
        return self.array_values

    def updateDisplay(self):
        """Обновляет текстовое представление массива"""
        if self.array_values:
            self.setText(self.delimiter.join(str(v) for v in self.array_values))
        else:
            self.setText("")

    def openArrayDialog(self):
        """Открывает диалог редактирования массива"""
        dialog = ArrayEditDialog(
            initial_values=self.array_values,
            delimiter=self.delimiter,
            parent=self,
            constraints=self.item_constraints
        )
        if dialog.exec() == QDialog.Accepted:
            self.array_values, self.delimiter = dialog.getArrayAndDelimiter()
            self.updateDisplay()
            self.arrayChanged.emit(self.array_values)


class ArrayEditDialog(QDialog):
    """
    Диалоговое окно для редактирования массива.
    """
    def __init__(self, initial_values=None, delimiter=":", parent=None, constraints=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование массива")
        self.setModal(True)
        self.resize(520, 420)
        self.last_error_messages = {}
        self.item_constraints = constraints or {}
        self.field_validity = {}
        self.processed_values = []
        self._is_fully_initialized = False

        self.set_dark_palette()
        self._init_ui(initial_values)
        self.apply_styles()
        self._set_initial_delimiter(delimiter)
        self._is_fully_initialized = True

    # ------------------------ UI ИНИЦИАЛИЗАЦИЯ -----------------------------

    def _init_ui(self, initial_values=None):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        title = QLabel("РЕДАКТИРОВАНИЕ МАССИВА")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 16, QFont.Bold))
        title.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title)

        # --- Разделитель ---
        delimiter_container = QWidget()
        delimiter_layout = QHBoxLayout(delimiter_container)
        delimiter_label = QLabel("Разделитель:")
        delimiter_label.setFont(QFont("Consolas", 11, QFont.Bold))
        delimiter_label.setStyleSheet("color: #8892b0;")

        self.delimiter_combo = QComboBox()
        self.delimiter_combo.setMinimumHeight(40)
        self.delimiters_display = [":", ",", ";", "|", "Пробел", "Табуляция"]
        self.delimiters_values = [":", ",", ";", "|", " ", "\t"]
        self.delimiter_combo.addItems(self.delimiters_display)

        self.delimiter_combo.currentIndexChanged.connect(self._show_delimiter_hint)

        delimiter_layout.addWidget(delimiter_label)
        delimiter_layout.addWidget(self.delimiter_combo)
        layout.addWidget(delimiter_container)

        # --- Поля массива ---
        fields_container = QWidget()
        fields_container.setObjectName("fieldsContainer")
        fields_container.setStyleSheet("""
            #fieldsContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.fields_layout = QVBoxLayout(fields_container)
        self.fields_layout.setContentsMargins(10, 10, 10, 10)
        self.fields_layout.setSpacing(8)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_container)
        scroll_area.setMinimumHeight(250)
        layout.addWidget(scroll_area)

        # --- Кнопки управления ---
        btns_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Добавить элемент")
        self.add_button.clicked.connect(lambda: self.addField(""))
        self.remove_button = QPushButton("➖ Удалить элемент")
        self.remove_button.clicked.connect(self.removeField)
        btns_layout.addWidget(self.add_button)
        btns_layout.addWidget(self.remove_button)
        layout.addLayout(btns_layout)

        # --- Кнопки сохранения ---
        bottom_layout = QHBoxLayout()
        self.save_button = QPushButton("✅ Сохранить")
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("❌ Отмена")
        self.cancel_button.clicked.connect(self.reject)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.cancel_button)
        layout.addLayout(bottom_layout)

        self.input_widgets = []
        self.error_labels = {}

        if initial_values:
            for v in initial_values:
                self.addField(str(v))
        else:
            self.addField()

    def _show_delimiter_hint(self):
        """Показывает всплывающую подсказку при выборе разделителя"""
        text = self.delimiter_combo.currentText()
        hints = {
            ":": "Двоеточие — удобно для простых структур, например: a:b:c",
            ",": "Запятая — стандартный разделитель CSV, напр.: 1,2,3",
            ";": "Точка с запятой — часто используется в Excel",
            "|": "Вертикальная черта — безопасна, если данные содержат запятые",
            "Пробел": "Пробел — удобно для коротких текстовых массивов",
            "Табуляция": "Табуляция — используется в TSV форматах"
        }
        hint = hints.get(text, "")
        if hint:
            pos = self.delimiter_combo.mapToGlobal(QPoint(0, self.delimiter_combo.height()))
            QToolTip.showText(pos, hint, self.delimiter_combo)

    def _set_initial_delimiter(self, delimiter):
        """Устанавливает выбранный разделитель"""
        try:
            idx = self.delimiters_values.index(delimiter)
            self.delimiter_combo.setCurrentIndex(idx)
        except ValueError:
            pass

    # ------------------------ ВАЛИДАЦИЯ -----------------------------

    def validate_single_field(self, widget):
        """Простая локальная валидация — не допускаем пустые элементы"""
        value = widget.text().strip()
        if not value:
            self.set_field_error(widget, "❌ Элемент не может быть пустым")
            self.field_validity[widget] = False
        else:
            self.clear_field_error(widget)
            self.field_validity[widget] = True

    def validate_and_accept(self):
        """Валидирует все поля перед сохранением"""
        all_valid = True
        self.processed_values = []

        for input_field, _ in self.input_widgets:  # <-- исправлено
            self.validate_single_field(input_field)
            if not self.field_validity.get(input_field, False):
                all_valid = False

        if not all_valid:
            return  # оставить окно открытым

        self.array_values = [
            input_field.text().strip()
            for input_field, _ in self.input_widgets
            if input_field.text().strip()
        ]
        self.delimiter = self.delimiters_values[self.delimiter_combo.currentIndex()]
        self.accept()

    # ------------------------ ЭЛЕМЕНТЫ -----------------------------

    def addField(self, value=""):
        """Добавляет новое поле ввода и метку ошибки в один контейнер."""
        # Вертикальный контейнер для поля, метки и ошибки
        field_wrapper = QWidget()
        wrapper_layout = QVBoxLayout(field_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(3)

        # Горизонтальный layout для метки и поля ввода
        input_row_layout = QHBoxLayout()
        label = QLabel(f"Элемент {len(self.input_widgets) + 1}:")
        label.setStyleSheet("color: #64ffda; font-family: Consolas;")
        input_field = QLineEdit()
        input_field.setText("" if value is None else str(value))
        input_field.textChanged.connect(lambda: self.validate_single_field(input_field))

        input_row_layout.addWidget(label)
        input_row_layout.addWidget(input_field)

        # Метка для ошибки (под полем)
        error_label = QLabel()
        error_label.setProperty("class", "error-label")
        error_label.setWordWrap(True)
        error_label.hide()

        # Добавляем всё в вертикальный layout
        wrapper_layout.addLayout(input_row_layout)
        wrapper_layout.addWidget(error_label)

        # Добавляем этот контейнер в основной layout полей
        self.fields_layout.addWidget(field_wrapper)

        # Сохраняем ссылки
        self.input_widgets.append((input_field, field_wrapper))
        self.error_labels[input_field] = error_label
        self.field_validity[input_field] = True # По умолчанию поле валидно

        # Активируем кнопку удаления, если больше одного поля
        self.remove_button.setEnabled(len(self.input_widgets) > 1)

    def removeField(self):
        """Удаляет последнее поле"""
        if len(self.input_widgets) <= 1:
            self.remove_button.setEnabled(False)
            return

        input_field, row_container = self.input_widgets.pop()
        self.fields_layout.removeWidget(row_container)
        row_container.deleteLater()
        self.error_labels.pop(input_field, None)
        self.field_validity.pop(input_field, None)

        # Перенумеровываем метки
        for i, (field, cont) in enumerate(self.input_widgets):
            label = cont.findChild(QLabel)
            if label:
                label.setText(f"Элемент {i + 1}:")

        self.remove_button.setEnabled(len(self.input_widgets) > 1)

    def set_field_error(self, widget, msg):
        """Подсвечивает только поле ввода, а не весь контейнер"""
        if widget in self.error_labels:
            lbl = self.error_labels[widget]
            lbl.setText(msg or "❌ Ошибка")
            lbl.show()

            # только само поле делаем красным
            widget.setStyleSheet("""
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #ff5555;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            """)

            # запоминаем последнее сообщение (чтобы не спамить уведомлениями)
            last_msg = self.last_error_messages.get(widget)
            if msg and msg != last_msg:
                try:
                    notification.notify(
                        title="Ошибка валидации",
                        message=msg,
                        app_name="Редактор массива",
                        timeout=3
                    )
                except Exception:
                    pass
                self.last_error_messages[widget] = msg

    def clear_field_error(self, widget):
        """Возвращает нормальный стиль поля после исправления"""
        if widget in self.error_labels:
            lbl = self.error_labels[widget]
            lbl.hide()
            lbl.setText("")

            # вернуть обычную серую рамку
            widget.setStyleSheet("""
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            """)

        self.last_error_messages[widget] = None

    def getArrayAndDelimiter(self):
        """Возвращает массив и разделитель"""
        return self.array_values, self.delimiter

    # ------------------------ СТИЛИ -----------------------------

    def set_dark_palette(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.ToolTipText, QColor(18, 18, 24))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(64, 255, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(18, 18, 24))
        self.setPalette(dark_palette)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #0a0a0f,
                                            stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
                border-radius: 12px;
            }

            QLabel {
                color: #8892b0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
            }

            QLineEdit {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }

            QLineEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit.error {
                border: 2px solid #ff5555 !important;
                background: rgba(75, 25, 35, 0.8) !important;
            }

            QLineEdit.success {
                border: 2px solid #50fa7b !important;
                background: rgba(25, 75, 35, 0.3) !important;
            }

            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda,
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 10px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 16px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-height: 26px;
            }

            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2,
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8,
                                          stop: 1 #00838f);
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

            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #64ffda;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #50e3c2;
            }
        """)
