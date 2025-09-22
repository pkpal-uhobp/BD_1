from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QRadioButton,
    QButtonGroup, QPushButton, QWidget)
from plyer import notification
from typing import Tuple


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
        self.resize(500, 250)

        if not self.db_instance or not self.db_instance.is_connected():
            notification.notify(
                title="Ошибка",
                message="Нет подключения к базе данных!",
                timeout=3
            )
            self.reject()
            return

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Радиокнопки выбора режима
        self.radio_group = QButtonGroup(self)
        self.radio_single = QRadioButton("Обычная таблица")
        self.radio_join = QRadioButton("Сводная таблица (JOIN)")
        self.radio_single.setChecked(True)

        self.radio_group.addButton(self.radio_single)
        self.radio_group.addButton(self.radio_join)

        layout.addWidget(self.radio_single)
        layout.addWidget(self.radio_join)

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
        self.btn_ok = QPushButton("ОК")
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok.clicked.connect(self.on_ok_clicked)
        self.btn_cancel.clicked.connect(self.reject)

        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(self.btn_cancel)
        layout.addLayout(buttons_layout)

    def create_single_table_container(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        label = QLabel("Таблица:")
        self.single_combo = QComboBox()
        table_names = self.db_instance.get_table_names() or []
        self.single_combo.addItems(table_names)
        layout.addWidget(label)
        layout.addWidget(self.single_combo)
        container.setLayout(layout)
        return container

    def create_join_table_container(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        self.join_combo_left = QComboBox()
        self.join_combo_right = QComboBox()
        table_names = self.db_instance.get_table_names() or []
        self.join_combo_left.addItems(table_names)
        self.join_combo_right.addItems(table_names)
        layout.addWidget(QLabel("Левая:"))
        layout.addWidget(self.join_combo_left)
        layout.addWidget(QLabel("Правая:"))
        layout.addWidget(self.join_combo_right)
        container.setLayout(layout)
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

                # Например: если join_on = ("book_id", "id_book") → исключаем "t2.book_id"

                # Но у нас в all_columns — "t2.book_id" не будет, если book_id — из левой таблицы.

                # Правильно: исключаем t2.{join_on[1]} — потому что он дублирует t1.{join_on[0]}

                column_to_remove = f"t2.{join_on[1]}"  # Это дубликат — его убираем

                columns = [col for col in all_columns if col != column_to_remove]

                sort_columns = [self.get_default_sort_column()]

                self.result = {

                    "mode": "join",

                    "left_table": left_table,

                    "right_table": right_table,

                    "join_on": join_on,

                    "columns": columns,  # ✅ Все столбцы, кроме дубликата связующего поля

                    "sort_columns": sort_columns,

                }

            self.accept()

        except Exception as e:
            notification.notify(
                title="❌ Ошибка",
                message=f"Не удалось собрать параметры: {str(e)}",
                timeout=5
            )
