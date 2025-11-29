from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDateEdit, QPushButton, QScrollArea, QWidget, QLineEdit)
from PySide6.QtCore import QDate
from sqlalchemy import Enum as SQLEnum, ARRAY, Boolean, Date, Numeric, Integer, String
from plyer import notification
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
from custom.array_line_edit import ArrayLineEdit

class DeleteRecordDialog(QDialog):
    """Модальное окно для удаления записей из выбранной таблицы."""

    def __init__(self, db_instance, COLUMN_HEADERS_MAP, REVERSE_COLUMN_HEADERS_MAP, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.COLUMN_HEADERS_MAP = COLUMN_HEADERS_MAP
        self.REVERSE_COLUMN_HEADERS_MAP = REVERSE_COLUMN_HEADERS_MAP
        self.condition_widgets = {}  # {col_name: widget}
        
        # Словари для валидации
        self.input_widgets = {}  # {col_name: widget}
        self.error_labels = {}  # {col_name: error_label}
        self.field_validity = {}  # {col_name: bool}

        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.setWindowTitle("Удаление данных")
        self.setModal(True)
        self.resize(600, 700)

        # Устанавливаем тёмную палитру
        self.set_dark_palette()
        self.init_ui()
        self.apply_styles()

    def set_dark_palette(self):
        """Устанавливает тёмную цветовую палитру"""
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
        """Применяет CSS стили"""
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

            QComboBox {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 20px;
            }

            QComboBox:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QComboBox:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64ffda;
                width: 0px;
                height: 0px;
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

            QLineEdit, QDateEdit {
                background: rgba(15, 15, 25, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
            }

            QLineEdit:hover, QDateEdit:hover {
                border: 2px solid #6272a4;
                background: rgba(30, 30, 40, 0.9);
            }

            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #64ffda;
                background: rgba(35, 35, 45, 0.9);
            }

            QLineEdit::placeholder, QDateEdit::placeholder {
                color: #6272a4;
                font-style: italic;
            }
            
            /* Стили валидации */
            .error-label {
                color: #ff6b6b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(255, 107, 107, 0.1);
                border-radius: 4px;
                border-left: 3px solid #ff6b6b;
            }
            
            .success-label {
                color: #50fa7b !important;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                margin-top: 5px;
                padding: 5px 8px;
                background: rgba(80, 250, 123, 0.1);
                border-radius: 4px;
                border-left: 3px solid #50fa7b;
            }
            
            QLineEdit.error, QDateEdit.error {
                border: 2px solid #ff6b6b !important;
                background: rgba(255, 107, 107, 0.15) !important;
            }
            
            QLineEdit.success, QDateEdit.success {
                border: 2px solid #50fa7b !important;
                background: rgba(80, 250, 123, 0.15) !important;
            }
            
            QComboBox.error {
                border: 2px solid #ff6b6b !important;
                background: rgba(255, 107, 107, 0.15) !important;
            }
            
            QComboBox.success {
                border: 2px solid #50fa7b !important;
                background: rgba(80, 250, 123, 0.15) !important;
            }

            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
                border: none;
                border-radius: 10px;
                color: #0a0a0f;
                font-size: 16px;
                font-weight: bold;
                padding: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-height: 30px;
            }

            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff5252, 
                                          stop: 1 #ff3838);
                border: 2px solid #ff6b6b;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff3838, 
                                          stop: 1 #ff1e1e);
            }

            QPushButton:disabled {
                background: #44475a;
                color: #6272a4;
                border: 1px solid #6272a4;
            }

            QScrollArea {
                border: none;
                background: transparent;
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

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Заголовок
        title_label = QLabel("УДАЛЕНИЕ ДАННЫХ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title_label)

        # Контейнер для выбора таблицы
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_container.setStyleSheet("""
            #tableContainer {
                background: rgba(15, 15, 25, 0.6);

                padding: 15px;
                border: none;
            }
        """)
        table_layout = QVBoxLayout(table_container)

        table_label = QLabel("Выберите таблицу:")
        table_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.table_combo = QComboBox()
        self.table_combo.setMinimumHeight(40)

        table_names = self.db_instance.get_table_names()
        if not table_names:
            notification.notify(
                title="Ошибка",
                message="Не удалось получить список таблиц.",
                timeout=3
            )
            self.reject()
            return

        self.table_combo.addItems(table_names)
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_combo)
        layout.addWidget(table_container)

        # Контейнер для полей условий
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

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(fields_container)
        scroll_area.setMinimumHeight(400)
        layout.addWidget(scroll_area)

        # Загружаем поля для первой таблицы
        self.load_table_fields(self.table_combo.currentText())

        # Обновляем поля при смене таблицы
        self.table_combo.currentTextChanged.connect(self.load_table_fields)

        # Кнопка удаления
        self.btn_delete = QPushButton("УДАЛИТЬ ЗАПИСИ")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def clear_fields(self):
        """Полностью очищает все поля ввода."""
        self._clear_layout(self.fields_layout)
        self.condition_widgets.clear()
        self.input_widgets.clear()
        self.error_labels.clear()
        self.field_validity.clear()

    def create_field_row(self, label_text, widget, col_name):
        """Создает строку с меткой и виджетом ввода"""
        row_widget = QWidget()
        row_widget.setObjectName("fieldRow")
        row_widget.setStyleSheet("""
            #fieldRow {
                background: rgba(25, 25, 35, 0.3);
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)

        # Создаем контейнер для виджета и метки ошибки
        widget_container = QWidget()
        widget_layout = QVBoxLayout(widget_container)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(5)
        
        widget_layout.addWidget(widget)
        
        # Создаем метку ошибки
        error_label = QLabel()
        error_label.setProperty("class", "error-label")
        error_label.hide()
        widget_layout.addWidget(error_label)
        
        # Регистрируем виджеты для валидации
        self.input_widgets[col_name] = widget
        self.error_labels[col_name] = error_label
        self.field_validity[col_name] = True

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Consolas", 11, QFont.Bold))
        label.setStyleSheet("color: #64ffda;")

        row_layout.addWidget(label)
        row_layout.addWidget(widget_container, 1)

        return row_widget

    def load_table_fields(self, table_name: str):
        """Загружает и отображает поля условий для выбранной таблицы."""
        self.clear_fields()

        if table_name not in self.db_instance.tables:
            from plyer import notification
            notification.notify(
                title="Ошибка",
                message=f"Метаданные для таблицы '{table_name}' не загружены.",
                timeout=3
            )
            return

        table = self.db_instance.tables[table_name]

        for column in table.columns:
            display_name = self.COLUMN_HEADERS_MAP.get(column.name, column.name)
            widget = None

            # ENUM
            if isinstance(column.type, SQLEnum):
                widget = QComboBox()
                widget.addItem("")  # пустой элемент = не задано
                widget.addItems(column.type.enums)

            # ARRAY — теперь используем кастомный ArrayLineEdit
            elif isinstance(column.type, ARRAY):
                widget = ArrayLineEdit()
                widget.setToolTip("Нажмите, чтобы открыть редактор массива")

                # Определяем тип элементов массива для валидации
                if isinstance(column.type.item_type, String):
                    widget.setItemConstraints({"type": "string"})
                elif isinstance(column.type.item_type, Integer):
                    widget.setItemConstraints({"type": "int"})
                elif isinstance(column.type.item_type, Numeric):
                    widget.setItemConstraints({"type": "float"})
                else:
                    widget.setItemConstraints({"type": "string"})

            # BOOLEAN
            elif isinstance(column.type, Boolean):
                widget = QComboBox()
                widget.addItem("")  # не задано
                widget.addItem("Да", True)
                widget.addItem("Нет", False)

            # DATE
            elif isinstance(column.type, Date):
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setSpecialValueText("Не задано")
                widget.setDate(QDate(2000, 1, 1))  # маркер "не задано"

            # INTEGER / NUMERIC
            elif isinstance(column.type, (Integer, Numeric)):
                widget = QLineEdit()
                widget.setPlaceholderText("Число или оставьте пустым")

            # STRING
            elif isinstance(column.type, String):
                widget = QLineEdit()
                widget.setPlaceholderText("Текст или оставьте пустым")

            # Другие типы
            else:
                widget = QLineEdit()
                widget.setPlaceholderText("Значение или оставьте пустым")

            # Добавляем строку в layout
            field_row = self.create_field_row(f"{display_name}:", widget, column.name)
            self.fields_layout.addWidget(field_row)
            self.condition_widgets[column.name] = widget

        # Добавляем растягивающий элемент для выравнивания
        self.fields_layout.addStretch()
        
        # Подключаем валидацию для каждого поля
        self._connect_validation()

    def _connect_validation(self):
        """Подключает валидацию для всех полей"""
        for col_name, widget in self.input_widgets.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda text, name=col_name: self._validate_field(name))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda text, name=col_name: self._validate_field(name))
            elif isinstance(widget, QDateEdit):
                widget.dateChanged.connect(lambda date, name=col_name: self._validate_field(name))
            elif hasattr(widget, 'textChanged'):  # Для ArrayLineEdit
                widget.textChanged.connect(lambda text, name=col_name: self._validate_field(name))

    def _validate_field(self, col_name):
        """Валидация конкретного поля"""
        if col_name not in self.input_widgets:
            return True
            
        widget = self.input_widgets[col_name]
        table_name = self.table_combo.currentText()
        
        if table_name not in self.db_instance.tables:
            return True
            
        table = self.db_instance.tables[table_name]
        column = getattr(table.c, col_name)
        
        # Получаем значение в зависимости от типа виджета
        value = None
        if isinstance(widget, QLineEdit):
            value = widget.text().strip()
        elif isinstance(widget, QComboBox):
            value = widget.currentText()
        elif isinstance(widget, QDateEdit):
            if widget.date().isValid() and widget.date().year() != 2000:
                value = widget.date().toString("yyyy-MM-dd")
        elif hasattr(widget, 'getArray'):  # ArrayLineEdit
            try:
                value = widget.getArray()
            except:
                value = None
        
        # Если поле пустое - это нормально для условий удаления
        if not value:
            self.clear_field_error(col_name)
            return True
        
        # Валидация в зависимости от типа данных
        if isinstance(column.type, Integer):
            if not str(value).isdigit():
                self.set_field_error(col_name, "Должно быть целым числом")
                return False
            else:
                self.set_field_success(col_name, " Корректное целое число")
                
        elif isinstance(column.type, Numeric):
            try:
                float(value)
                self.set_field_success(col_name, " Корректное число")
            except ValueError:
                self.set_field_error(col_name, "Должно быть числом")
                return False
                
        elif isinstance(column.type, String):
            if len(str(value)) > 255:  # Предполагаем максимальную длину строки
                self.set_field_error(col_name, "Слишком длинная строка (максимум 255 символов)")
                return False
            else:
                self.set_field_success(col_name, " Корректная строка")
                
        elif isinstance(column.type, Date):
            # Для QDateEdit валидация уже встроена
            self.set_field_success(col_name, " Корректная дата")
            
        elif isinstance(column.type, Boolean):
            # Для QComboBox с булевыми значениями валидация не нужна
            self.set_field_success(col_name, " Корректное булево значение")
            
        elif isinstance(column.type, SQLEnum):
            # Для ENUM валидация не нужна - значения берутся из списка
            self.set_field_success(col_name, " Корректное значение ENUM")
            
        elif isinstance(column.type, ARRAY):
            # Для массивов валидация происходит в ArrayLineEdit
            self.set_field_success(col_name, " Корректный массив")
            
        return True

    def set_field_error(self, field_name, error_message):
        """Устанавливает ошибку для поля"""
        if field_name in self.error_labels:
            if error_message:
                self.error_labels[field_name].setText(error_message)
                self.error_labels[field_name].setStyleSheet("""
                    QLabel {
                        color: #ff6b6b;
                        font-size: 12px;
                        font-weight: bold;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        margin-top: 5px;
                        padding: 5px 8px;
                        background: rgba(255, 107, 107, 0.1);
                        border-radius: 4px;
                        border-left: 3px solid #ff6b6b;
                    }
                """)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = False
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "error")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def set_field_success(self, field_name, success_message):
        """Устанавливает успешное состояние для поля"""
        if field_name in self.error_labels:
            if success_message:
                self.error_labels[field_name].setText(success_message)
                self.error_labels[field_name].setStyleSheet("""
                    QLabel {
                        color: #50fa7b;
                        font-size: 12px;
                        font-weight: bold;
                        font-family: 'Consolas', 'Fira Code', monospace;
                        margin-top: 5px;
                        padding: 5px 8px;
                        background: rgba(80, 250, 123, 0.1);
                        border-radius: 4px;
                        border-left: 3px solid #50fa7b;
                    }
                """)
                self.error_labels[field_name].show()
                self.field_validity[field_name] = True
                widget = self.input_widgets[field_name]
                widget.setProperty("class", "success")
                widget.setStyleSheet(self.styleSheet())
            else:
                self.clear_field_error(field_name)
    
    def clear_field_error(self, field_name):
        """Очищает ошибку для поля"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()
            self.error_labels[field_name].setStyleSheet("")
            self.field_validity[field_name] = True
            widget = self.input_widgets[field_name]
            widget.setProperty("class", "")
            widget.setStyleSheet(self.styleSheet())

    def on_delete_clicked(self):
        """Обработка нажатия на кнопку удаления записей."""
        table_name = self.table_combo.currentText()
        if not table_name:
            notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
            return

        # Проверяем валидность всех полей
        all_valid = True
        for col_name in self.input_widgets.keys():
            if not self._validate_field(col_name):
                all_valid = False
        
        if not all_valid:
            notification.notify(
                title="Ошибка валидации", 
                message="Исправьте ошибки в полях перед удалением!", 
                timeout=3
            )
            return

        condition = {}
        table = self.db_instance.tables[table_name]

        for col_name, widget in self.condition_widgets.items():
            column = getattr(table.c, col_name)

            # ENUM
            if isinstance(widget, QComboBox) and isinstance(column.type, SQLEnum):
                value = widget.currentText()
                if value:
                    condition[col_name] = value

            # ARRAY — используем кастомный виджет
            elif isinstance(widget, ArrayLineEdit) and isinstance(column.type, ARRAY):
                values = widget.getArray()
                if values:
                    condition[col_name] = values

            # BOOLEAN
            elif isinstance(widget, QComboBox) and isinstance(column.type, Boolean):
                index = widget.currentIndex()
                if index > 0:  # пропускаем "не задано"
                    condition[col_name] = widget.currentData()

            # DATE
            elif isinstance(widget, QDateEdit):
                if widget.date().isValid() and widget.date().year() != 2000:
                    condition[col_name] = widget.date().toString("yyyy-MM-dd")

            # NUMERIC / STRING / INT
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    if isinstance(column.type, Integer):
                        if not text.isdigit():
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{col_name}' должно быть целым числом.",
                                timeout=3
                            )
                            return
                        condition[col_name] = int(text)
                    elif isinstance(column.type, Numeric):
                        try:
                            condition[col_name] = float(text)
                        except ValueError:
                            notification.notify(
                                title="Ошибка",
                                message=f"Поле '{col_name}' должно быть числом.",
                                timeout=3
                            )
                            return
                    else:
                        condition[col_name] = text

        # Если условий нет — предупреждаем
        if not condition:
            reply = QMessageBox.warning(
                self,
                "Подтверждение",
                f"Вы не указали ни одного условия. Это удалит ВСЕ записи из таблицы '{table_name}'.\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Подсчёт количества записей для удаления
        try:
            count = self.db_instance.count_records_filtered(table_name, condition)
            if count == 0:
                notification.notify(
                    title="Информация",
                    message="Нет записей, удовлетворяющих условию.",
                    timeout=3
                )
                return

            # Подтверждение удаления
            reply = QMessageBox.warning(
                self,
                "Подтверждение удаления",
                f"Будет удалено {count} записей из таблицы '{table_name}'.\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.db_instance.delete_data(table_name, condition)
                if success:
                    notification.notify(
                        title=" Успех",
                        message=f"Удалено {count} записей из таблицы '{table_name}'.",
                        timeout=5
                    )
                    self.accept()
                else:
                    notification.notify(
                        title=" Ошибка",
                        message="Не удалось выполнить удаление. Проверьте логи.",
                        timeout=5
                    )

        except Exception as e:
            notification.notify(
                title=" Ошибка",
                message=f"Ошибка при проверке записей: {str(e)}",
                timeout=5
            )
