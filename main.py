import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout
)
from tabs.menu import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from plyer import notification
from db.Class_DB import DB


class DBConnectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Подключение к базе данных")
        self.setGeometry(300, 200, 400, 300)  # Уменьшил высоту, т.к. QTextEdit удалён
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        # Заголовок
        title_label = QLabel("Введите параметры подключения к PostgreSQL")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        # Форма ввода
        form_layout = QFormLayout()

        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("5432")
        self.dbname_input = QLineEdit("library_db")
        self.user_input = QLineEdit("postgres")
        self.password_input = QLineEdit("root")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Хост:", self.host_input)
        form_layout.addRow("Порт:", self.port_input)
        form_layout.addRow("Имя БД:", self.dbname_input)
        form_layout.addRow("Пользователь:", self.user_input)
        form_layout.addRow("Пароль:", self.password_input)

        layout.addLayout(form_layout)

        # Кнопка подключения
        self.connect_button = QPushButton("Подключиться")
        self.connect_button.clicked.connect(self.on_connect_clicked)
        layout.addWidget(self.connect_button)

        # Стиль
        self.setStyleSheet("""
            QLabel { font-size: 11pt; }
            QLineEdit { font-size: 11pt; padding: 5px; }
            QPushButton { font-size: 11pt; padding: 8px; }
        """)

    def on_connect_clicked(self):
        # Сбор параметров
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        dbname = self.dbname_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()

        # Валидация порта
        if not port.isdigit():
            notification.notify(
                title="Ошибка ввода",
                message="Порт должен быть числом!",
                timeout=5
            )
            return

        port = int(port)

        # Настройка логгера — пишем в файл (оставляем для отладки)
        logger = logging.getLogger("DB")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        file_handler = logging.FileHandler("db/db_app.log", encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)

        # Создание DB
        db = DB(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            log_file="db/db_app.log"
        )

        # Подключение
        connected = db.connect()

        # Показываем уведомление вместо логов
        if connected:
            notification.notify(
                title="✅ Успешное подключение",
                message=f"Подключено к базе: {dbname}@{host}:{port}",
                timeout=5
            )
              # ← ЗАМЕНИТЕ ИМЯ ФАЙЛА!
            self.main_window = MainWindow(db_instance=db)
            self.main_window.show()
            self.close()
        else:
            notification.notify(
                title="❌ Ошибка подключения",
                message="Не удалось подключиться к базе данных. Проверьте параметры.",
            )
        self.db_instance = db

    def closeEvent(self, event):
        if hasattr(self, 'db_instance') and self.db_instance:
            try:
                self.db_instance.disconnect()
                notification.notify(
                        title="Информация",
                        message="Отключение от базы данных выполнено.",
                        timeout=5
                    )
            except Exception as e:
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка при отключении от базы данных: {e}",
                    timeout=5
                )
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DBConnectionWindow()
    window.show()

    sys.exit(app.exec())