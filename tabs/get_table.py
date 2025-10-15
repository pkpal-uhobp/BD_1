# get_table.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QRadioButton,
    QButtonGroup, QPushButton, QWidget, QListWidget, QListWidgetItem)
from plyer import notification
from typing import Tuple, List
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt


class ShowTableDialog(QDialog):
    """Модальное окно для выбора параметров запроса."""

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.result = None

        self.setWindowTitle("Параметры запроса")
        self.setModal(True)
        self.resize(700, 850)  # Увеличил размер для удобства

        self.set_dark_palette()

        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.init_ui()
        self.apply_styles()

    # ... (остальные методы класса без изменений: set_dark_palette, apply_styles, init_ui и т.д.) ...
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
                color: #64ffda;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                padding: 5px 0;
            }
            QRadioButton {
                color: #8892b0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Fira Code', monospace;
                spacing: 10px;
                padding: 8px 0;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #44475a;
                border-radius: 10px;
                background: rgba(25, 25, 35, 0.8);
            }
            QRadioButton::indicator:hover { border: 2px solid #6272a4; }
            QRadioButton::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
            }
            QRadioButton::indicator:checked:hover { background: #50e3c2; }
            QComboBox {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
                min-height: 20px;
            }
            QComboBox:hover { border: 2px solid #6272a4; }
            QComboBox:focus { border: 2px solid #64ffda; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64ffda;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background: rgba(25, 25, 35, 0.95);
                border: 2px solid #64ffda;
                border-radius: 8px;
                color: #f8f8f2;
                selection-background-color: #64ffda;
                selection-color: #0a0a0f;
                outline: none;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, stop: 1 #00bcd4);
                border: none;
                border-radius: 10px;
                color: #0a0a0f;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: 'Consolas', 'Fira Code', monospace;
                min-height: 30px;
                min-width: 50px;
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
            QListWidget {
                background: rgba(25, 25, 35, 0.8);
                border: 2px solid #44475a;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                font-family: 'Consolas', 'Fira Code', monospace;
                color: #f8f8f2;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #44475a40;
            }
            QListWidget::item:selected {
                background-color: #64ffda40;
                color: #64ffda;
                border: 1px solid #64ffda;
            }
            QListWidget::item:hover { background-color: #6272a440; }
            #tableContainer, #joinContainer {
                background: rgba(15, 15, 25, 0.6);
                border: none;
                padding: 15px;
                margin: 5px 0;
            }
            #radioContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
            #btn_cancel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #ff6b6b, stop: 1 #ff5252);
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("ПАРАМЕТРЫ ЗАПРОСА")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(title_label)

        # Радиокнопки
        radio_container = QWidget()
        radio_container.setObjectName("radioContainer")
        radio_layout = QVBoxLayout(radio_container)
        self.radio_group = QButtonGroup(self)
        self.radio_single = QRadioButton("Обычная таблица")
        self.radio_join = QRadioButton("Сводная таблица (JOIN)")
        self.radio_single.setChecked(True)
        self.radio_group.addButton(self.radio_single)
        self.radio_group.addButton(self.radio_join)
        radio_layout.addWidget(self.radio_single)
        radio_layout.addWidget(self.radio_join)
        layout.addWidget(radio_container)

        # Контейнеры таблиц
        self.single_container = self.create_single_table_container()
        self.join_container = self.create_join_table_container()
        layout.addWidget(self.single_container)
        layout.addWidget(self.join_container)

        # Переключение видимости
        self.radio_single.toggled.connect(self.toggle_mode)
        self.radio_join.toggled.connect(self.toggle_mode)
        self.toggle_mode()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btn_ok = QPushButton("ОК")
        self.btn_cancel = QPushButton("ОТМЕНА")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_ok.clicked.connect(self.on_ok_clicked)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)
        layout.addLayout(buttons_layout)

    def create_single_table_container(self):
        container = QWidget()
        container.setObjectName("tableContainer")
        layout = QHBoxLayout(container)
        label = QLabel("Таблица:")
        label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.single_combo = QComboBox()
        self.single_combo.setMinimumHeight(35)
        self.single_combo.addItems(self.db_instance.get_table_names() or [])
        layout.addWidget(label)
        layout.addWidget(self.single_combo, 1)
        return container

    def create_join_table_container(self):
        container = QWidget()
        container.setObjectName("joinContainer")
        layout = QVBoxLayout(container)

        # Строка 1: Выбор таблиц
        row1_layout = QHBoxLayout()
        self.join_combo_left = QComboBox()
        self.join_combo_left.setMinimumHeight(35)
        self.join_combo_right = QComboBox()
        self.join_combo_right.setMinimumHeight(35)
        table_names = self.db_instance.get_table_names() or []
        self.join_combo_left.addItems(table_names)
        self.join_combo_right.addItems(table_names)
        self.join_combo_left.currentTextChanged.connect(self.update_join_fields)
        self.join_combo_right.currentTextChanged.connect(self.update_join_fields)
        row1_layout.addWidget(QLabel("Левая таблица:"))
        row1_layout.addWidget(self.join_combo_left, 1)
        row1_layout.addWidget(QLabel("Правая таблица:"))
        row1_layout.addWidget(self.join_combo_right, 1)
        layout.addLayout(row1_layout)

        # Строка 2: Тип соединения
        row2_layout = QHBoxLayout()
        self.join_type_combo = QComboBox()
        self.join_type_combo.setMinimumHeight(35)
        self.join_type_combo.addItems(["INNER", "LEFT", "RIGHT", "FULL"])
        row2_layout.addWidget(QLabel("Тип соединения:"))
        row2_layout.addWidget(self.join_type_combo, 1)
        layout.addLayout(row2_layout)

        # Строка 3: Поля для отображения
        row3_layout = QHBoxLayout()
        self.display_columns_list = QListWidget()
        self.display_columns_list.setMaximumHeight(150)
        self.display_columns_list.setSelectionMode(QListWidget.MultiSelection)
        row3_layout.addWidget(QLabel("Поля для отображения:"))
        row3_layout.addWidget(self.display_columns_list, 1)
        layout.addLayout(row3_layout)

        # Кнопки управления выбором
        btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("Выбрать все")
        btn_deselect_all = QPushButton("Снять выбор")
        btn_select_all.clicked.connect(self.select_all_columns)
        btn_deselect_all.clicked.connect(self.deselect_all_columns)
        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(btn_deselect_all)
        layout.addLayout(btn_layout)

        return container

    def toggle_mode(self):
        is_join = self.radio_join.isChecked()
        self.single_container.setVisible(not is_join)
        self.join_container.setVisible(is_join)

    def update_join_fields(self):
        """Обновляет список полей для отображения при смене таблиц."""
        left_table = self.join_combo_left.currentText()
        right_table = self.join_combo_right.currentText()
        if not left_table or not right_table:
            return

        self.display_columns_list.clear()
        left_columns = self.db_instance.get_column_names(left_table) or []
        right_columns = self.db_instance.get_column_names(right_table) or []

        # Добавляем столбцы левой таблицы
        for col in left_columns:
            item = QListWidgetItem(f"{left_table}.{col}")
            # Сохраняем кортеж (имя_таблицы, имя_столбца) для последующего извлечения
            item.setData(Qt.UserRole, (left_table, col))
            self.display_columns_list.addItem(item)
            item.setSelected(True)  # По умолчанию все выбраны

        # Добавляем столбцы правой таблицы
        for col in right_columns:
            item = QListWidgetItem(f"{right_table}.{col}")
            item.setData(Qt.UserRole, (right_table, col))
            self.display_columns_list.addItem(item)
            item.setSelected(True)  # По умолчанию все выбраны

    def select_all_columns(self):
        for i in range(self.display_columns_list.count()):
            self.display_columns_list.item(i).setSelected(True)

    def deselect_all_columns(self):
        for i in range(self.display_columns_list.count()):
            self.display_columns_list.item(i).setSelected(False)

    def get_selected_display_columns(self) -> List[Tuple[str, str]]:
        """Возвращает список выбранных полей в формате [(table, column), ...]"""
        selected_items = self.display_columns_list.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items]

    def get_default_sort_column(self) -> Tuple[str, bool]:
        """Возвращает кортеж (имя_столбца, по_возрастанию) для сортировки."""
        if self.radio_single.isChecked():
            table_name = self.single_combo.currentText()
            columns = self.db_instance.get_column_names(table_name) or []
            return (columns[0] if columns else "id", True)
        else:
            # Для JOIN - берем первый столбец из левой таблицы
            left_table = self.join_combo_left.currentText()
            columns = self.db_instance.get_column_names(left_table) or []
            return (columns[0] if columns else "id", True)

    def on_ok_clicked(self):
        """Собирает параметры и закрывает диалог."""
        try:
            if self.radio_single.isChecked():
                table_name = self.single_combo.currentText()
                if not table_name:
                    notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                    return
                self.result = {
                    "mode": "single",
                    "table_name": table_name,
                    "sort_columns": [self.get_default_sort_column()],
                }
            else:  # JOIN
                left_table = self.join_combo_left.currentText()
                right_table = self.join_combo_right.currentText()
                if not left_table or not right_table or left_table == right_table:
                    notification.notify(title="Ошибка", message="Выберите две разные таблицы!", timeout=3)
                    return

                # 1. Определяем условие для JOIN с помощью метода из класса DB
                # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
                predefined_joins = self.db_instance.get_predefined_joins()
                join_on = predefined_joins.get((left_table, right_table))

                if not join_on:
                    # Если связь не найдена, пробуем найти общие поля как запасной вариант
                    left_cols = set(self.db_instance.get_column_names(left_table) or [])
                    right_cols = set(self.db_instance.get_column_names(right_table) or [])
                    common_cols = list(left_cols & right_cols)
                    if not common_cols:
                        notification.notify(title="Ошибка", message="Не найдено предопределенных связей или общих полей для JOIN.", timeout=3)
                        return
                    join_on = (common_cols[0], common_cols[0])

                # 2. Получаем выбранные пользователем столбцы
                selected_tuples = self.get_selected_display_columns()
                if not selected_tuples:
                    notification.notify(title="Ошибка", message="Выберите хотя бы одно поле для отображения.",
                                        timeout=3)
                    return

                # 3. Формируем список столбцов в формате ['t1.col', 't2.col']
                columns_for_db = []
                for table_name, col_name in selected_tuples:
                    prefix = "t1" if table_name == left_table else "t2"
                    columns_for_db.append(f"{prefix}.{col_name}")

                # 4. Собираем все параметры
                self.result = {
                    "mode": "join",
                    "left_table": left_table,
                    "right_table": right_table,
                    "join_on": join_on,
                    "columns": columns_for_db,
                    "sort_columns": [self.get_default_sort_column()],
                    "join_type": self.join_type_combo.currentText(),
                }
            self.accept()

        except Exception as e:
            notification.notify(title="❌ Ошибка", message=f"Не удалось собрать параметры: {str(e)}", timeout=5)
