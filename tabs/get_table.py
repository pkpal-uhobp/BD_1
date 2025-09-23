from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QRadioButton,
    QButtonGroup, QPushButton, QWidget)
from plyer import notification
from typing import Tuple
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt


class ShowTableDialog(QDialog):
    """Модальное окно для выбора параметров запроса.
    Для обычной таблицы — возвращает все столбцы через get_sorted_data.
    Для JOIN — возвращает ВСЕ столбцы автоматически.
    Сортировка всегда по первому столбцу по возрастанию.
    """

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db_instance = db_instance
        self.result = None

        self.setWindowTitle("Параметры запроса")
        self.setModal(True)
        self.resize(500, 600)

        # Устанавливаем тёмную палитру
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

            QRadioButton::indicator:hover {
                border: 2px solid #6272a4;
            }

            QRadioButton::indicator:checked {
                background: #64ffda;
                border: 2px solid #64ffda;
            }

            QRadioButton::indicator:checked:hover {
                background: #50e3c2;
                border: 2px solid #50e3c2;
            }

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
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
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
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
            }

            QPushButton:disabled {
                background: #44475a;
                color: #6272a4;
                border: 1px solid #6272a4;
            }

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
                                          stop: 0 #ff6b6b, 
                                          stop: 1 #ff5252);
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

        # Контейнер для радиокнопок
        radio_container = QWidget()
        radio_container.setObjectName("radioContainer")
        radio_layout = QVBoxLayout(radio_container)

        # Радиокнопки выбора режима
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
        table_names = self.db_instance.get_table_names() or []
        self.single_combo.addItems(table_names)

        layout.addWidget(label)
        layout.addWidget(self.single_combo, 1)
        return container

    def create_join_table_container(self):
        container = QWidget()
        container.setObjectName("joinContainer")
        layout = QVBoxLayout(container)

        # Первая строка - левая таблица
        row1_layout = QHBoxLayout()
        label1 = QLabel("Левая таблица:")
        label1.setFont(QFont("Consolas", 12, QFont.Bold))
        self.join_combo_left = QComboBox()
        self.join_combo_left.setMinimumHeight(35)
        self.join_combo_left.setFixedWidth(300)
        table_names = self.db_instance.get_table_names() or []
        self.join_combo_left.addItems(table_names)

        row1_layout.addWidget(label1)
        row1_layout.addWidget(self.join_combo_left, 1)

        # Вторая строка - правая таблица
        row2_layout = QHBoxLayout()
        label2 = QLabel("Правая таблица:")
        label2.setFont(QFont("Consolas", 12, QFont.Bold))
        self.join_combo_right = QComboBox()
        self.join_combo_right.setMinimumHeight(35)
        self.join_combo_left.setFixedWidth(300)
        self.join_combo_right.addItems(table_names)

        row2_layout.addWidget(label2)
        row2_layout.addWidget(self.join_combo_right, 1)

        layout.addLayout(row1_layout)
        layout.addLayout(row2_layout)
        return container

    def toggle_mode(self):
        is_join = self.radio_join.isChecked()
        self.single_container.setVisible(not is_join)
        self.join_container.setVisible(is_join)

    def get_default_sort_column(self) -> Tuple[str, bool]:
        """Возвращает кортеж (первый_столбец, True) для сортировки по возрастанию."""
        if self.radio_single.isChecked():
            table_name = self.single_combo.currentText()
            if not table_name:
                return ("id", True)
            columns = self.db_instance.get_column_names(table_name) or []
            first_col = columns[0] if columns else "id"
            return (first_col, True)
        else:
            left_table = self.join_combo_left.currentText()
            if not left_table:
                return ("t1.id", True)
            columns = self.db_instance.get_column_names(left_table) or []
            first_col = columns[0] if columns else "id"
            return (f"t1.{first_col}", True)

    def on_ok_clicked(self):
        """Собирает параметры и закрывает диалог."""
        try:
            if self.radio_single.isChecked():
                table_name = self.single_combo.currentText()
                if not table_name:
                    notification.notify(title="Ошибка", message="Выберите таблицу!", timeout=3)
                    return

                sort_columns = [self.get_default_sort_column()]

                self.result = {
                    "mode": "single",
                    "table_name": table_name,
                    "sort_columns": sort_columns,
                }

            else:  # JOIN
                left_table = self.join_combo_left.currentText()
                right_table = self.join_combo_right.currentText()

                if not left_table or not right_table:
                    notification.notify(title="Ошибка", message="Выберите обе таблицы!", timeout=3)
                    return

                if left_table == right_table:
                    notification.notify(title="Ошибка", message="Таблицы должны быть разными!", timeout=3)
                    return

                predefined_joins = {
                    ("Issued_Books", "Books"): ("book_id", "id_book"),
                    ("Issued_Books", "Readers"): ("reader_id", "reader_id"),
                    ("Books", "Issued_Books"): ("id_book", "book_id"),
                    ("Readers", "Issued_Books"): ("reader_id", "reader_id"),
                }

                join_on = predefined_joins.get((left_table, right_table))
                if join_on is None:
                    join_on = predefined_joins.get((right_table, left_table))
                    if join_on:
                        join_on = (join_on[1], join_on[0])

                if join_on is None:
                    left_cols = set(self.db_instance.get_column_names(left_table) or [])
                    right_cols = set(self.db_instance.get_column_names(right_table) or [])
                    common_cols = list(left_cols & right_cols)
                    if not common_cols:
                        notification.notify(
                            title="Ошибка",
                            message=f"Не найдено общих колонок для JOIN между '{left_table}' и '{right_table}'.",
                            timeout=3
                        )
                        return
                    join_key = common_cols[0]
                    join_on = (join_key, join_key)

                # ✅ Собираем ВСЕ столбцы
                left_cols = self.db_instance.get_column_names(left_table) or []
                right_cols = self.db_instance.get_column_names(right_table) or []
                all_columns = [f"t1.{col}" for col in left_cols] + [f"t2.{col}" for col in right_cols]

                # ✅ Удаляем дубликат связующего поля из правой таблицы
                column_to_remove = f"t2.{join_on[1]}"
                columns = [col for col in all_columns if col != column_to_remove]

                sort_columns = [self.get_default_sort_column()]

                self.result = {
                    "mode": "join",
                    "left_table": left_table,
                    "right_table": right_table,
                    "join_on": join_on,
                    "columns": columns,
                    "sort_columns": sort_columns,
                }

            self.accept()

        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Не удалось собрать параметры: {str(e)}",
                timeout=5
            )