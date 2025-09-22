import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFormLayout
)
from tabs.menu import MainWindow
from db.Class_DB import DB
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from plyer import notification


class DBConnectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Подключение к базе данных")

        # Устанавливаем тёмную палитру для всего приложения
        self.set_dark_palette()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName("mainWidget")

        # Устанавливаем фиксированный размер окна
        self.setFixedSize(500, 650)

        # Главный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)
        central_widget.setLayout(main_layout)

        # Заголовок с иконкой базы данных
        title_container = QWidget()
        title_container.setObjectName("titleContainer")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_container.setLayout(title_layout)

        db_icon = QLabel("🕮")
        db_icon.setFont(QFont("Arial", 28, QFont.Bold))
        db_icon.setAlignment(Qt.AlignCenter)
        db_icon.setStyleSheet("color: #64ffda;")

        title_label = QLabel("LIBRARY CONNECTION")
        title_label.setFont(QFont("Consolas", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #64ffda; letter-spacing: 2px; padding-right: 50px;")

        title_layout.addWidget(db_icon)
        title_layout.addWidget(title_label)

        # Контейнер для формы
        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(10)
        form_container.setLayout(form_layout)

        # Создаем поля ввода и метки ошибок
        self.host_input = QLineEdit("localhost")
        self.host_error = QLabel("")
        self.host_error.setObjectName("errorLabel")
        self.host_error.setVisible(False)  # Скрываем ошибку изначально

        self.port_input = QLineEdit("5432")
        self.port_error = QLabel("")
        self.port_error.setObjectName("errorLabel")
        self.port_error.setVisible(False)

        self.dbname_input = QLineEdit("library_db")
        self.dbname_error = QLabel("")
        self.dbname_error.setObjectName("errorLabel")
        self.dbname_error.setVisible(False)

        self.user_input = QLineEdit("postgres")
        self.user_error = QLabel("")
        self.user_error.setObjectName("errorLabel")
        self.user_error.setVisible(False)

        self.password_input = QLineEdit("password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_error = QLabel("")
        self.password_error.setObjectName("errorLabel")
        self.password_error.setVisible(False)

        # Настройка полей ввода
        input_fields = [self.host_input, self.port_input, self.dbname_input, self.user_input, self.password_input]
        placeholders = ["server host", "5432", "database name", "username", "password"]

        for field, placeholder in zip(input_fields, placeholders):
            field.setPlaceholderText(placeholder)
            field.setMinimumHeight(42)
            field.setObjectName("inputField")
            # Подключаем валидацию при изменении текста с задержкой
            field.textChanged.connect(self.schedule_validation)

        # Добавляем поля и ошибки в форму
        form_layout.addRow(self.create_label("HOST:"), self.host_input)
        form_layout.addRow("", self.host_error)

        form_layout.addRow(self.create_label("PORT:"), self.port_input)
        form_layout.addRow("", self.port_error)

        form_layout.addRow(self.create_label("DATABASE:"), self.dbname_input)
        form_layout.addRow("", self.dbname_error)

        form_layout.addRow(self.create_label("USER:"), self.user_input)
        form_layout.addRow("", self.user_error)

        form_layout.addRow(self.create_label("PASSWORD:"), self.password_input)
        form_layout.addRow("", self.password_error)

        # Кнопка подключения
        self.connect_button = QPushButton("ПОДКЛЮЧИТЬСЯ")
        self.connect_button.setMinimumHeight(55)
        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.connect_button.setObjectName("connectButton")

        # Добавляем элементы в основной layout
        main_layout.addWidget(title_container)
        main_layout.addSpacing(20)
        main_layout.addWidget(form_container)
        main_layout.addSpacing(25)
        main_layout.addWidget(self.connect_button)
        main_layout.addStretch()

        # Таймер для отложенной валидации
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_all_fields_realtime)

        # Применяем стили
        self.apply_styles()

        # Инициализация переменных
        self.last_table_name = None
        self.last_join_params = None
        self.db_instance = None
        self.main_window = None

        # Валидируем начальные значения
        QTimer.singleShot(100, self.validate_all_fields_realtime)

    def create_label(self, text):
        """Создает стилизованную метку"""
        label = QLabel(text)
        label.setObjectName("formLabel")
        return label

    def schedule_validation(self):
        """Запускает отложенную валидацию"""
        self.validation_timer.start(300)  # 300ms задержка

    def validate_all_fields_realtime(self):
        """Валидация всех полей в реальном времени"""
        is_valid = True

        # Хост
        host = self.host_input.text().strip()
        host_error = self.get_host_error(host)
        if host_error:
            is_valid = False
            self.host_error.setText(host_error)
            self.host_error.setVisible(True)
            self.set_field_error_style(self.host_input, True)
        else:
            self.host_error.setVisible(False)
            self.set_field_error_style(self.host_input, False)

        # Порт
        port = self.port_input.text().strip()
        port_error = self.get_port_error(port)
        if port_error:
            is_valid = False
            self.port_error.setText(port_error)
            self.port_error.setVisible(True)
            self.set_field_error_style(self.port_input, True)
        else:
            self.port_error.setVisible(False)
            self.set_field_error_style(self.port_input, False)

        # Имя базы данных
        dbname = self.dbname_input.text().strip()
        dbname_error = self.get_dbname_error(dbname)
        if dbname_error:
            is_valid = False
            self.dbname_error.setText(dbname_error)
            self.dbname_error.setVisible(True)
            self.set_field_error_style(self.dbname_input, True)
        else:
            self.dbname_error.setVisible(False)
            self.set_field_error_style(self.dbname_input, False)

        # Пользователь
        user = self.user_input.text().strip()
        user_error = self.get_user_error(user)
        if user_error:
            is_valid = False
            self.user_error.setText(user_error)
            self.user_error.setVisible(True)
            self.set_field_error_style(self.user_input, True)
        else:
            self.user_error.setVisible(False)
            self.set_field_error_style(self.user_input, False)

        # Пароль
        password = self.password_input.text()
        password_error = self.get_password_error(password)
        if password_error:
            is_valid = False
            self.password_error.setText(password_error)
            self.password_error.setVisible(True)
            self.set_field_error_style(self.password_input, True)
        else:
            self.password_error.setVisible(False)
            self.set_field_error_style(self.password_input, False)

        # Активируем/деактивируем кнопку
        self.connect_button.setEnabled(is_valid)

    def set_field_error_style(self, field, has_error):
        """Устанавливает стиль поля в зависимости от наличия ошибки"""
        if has_error:
            field.setStyleSheet("""
                #inputField {
                    background: rgba(25, 25, 35, 0.8);
                    border: 2px solid #ff5555;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    color: #f8f8f2;
                }
                #inputField:focus {
                    background: rgba(35, 35, 45, 0.9);
                    border: 2px solid #ff5555;
                    border-radius: 8px;
                }
            """)
        else:
            field.setStyleSheet("""
                #inputField {
                    background: rgba(25, 25, 35, 0.8);
                    border: 2px solid #44475a;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    color: #f8f8f2;
                }
                #inputField:hover {
                    border: 2px solid #6272a4;
                    background: rgba(30, 30, 40, 0.9);
                }
                #inputField:focus {
                    background: rgba(35, 35, 45, 0.9);
                    border: 2px solid #64ffda;
                    border-radius: 8px;
                }
            """)

    def get_host_error(self, host):
        """Валидация хоста"""
        if not host:
            return "Хост не может быть пустым"
        elif len(host) > 255:
            return "Хост слишком длинный (макс. 255 символов)"
        elif not all(c.isalnum() or c in '.-_' for c in host):
            return "Хост содержит недопустимые символы"
        return ""

    def get_port_error(self, port):
        """Валидация порта"""
        if not port:
            return "Порт не может быть пустым"
        elif not port.isdigit():
            return "Порт должен быть числом"
        else:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return "Порт должен быть в диапазоне 1-65535"
        return ""

    def get_dbname_error(self, dbname):
        """Валидация имени базы данных"""
        if not dbname:
            return "Имя базы данных не может быть пустым"
        elif len(dbname) > 63:
            return "Имя базы данных слишком длинное (макс. 63 символа)"
        elif not dbname[0].isalpha():
            return "Имя базы данных должно начинаться с буквы"
        elif not all(c.isalnum() or c == '_' for c in dbname):
            return "Имя базы данных может содержать только буквы, цифры и подчеркивания"
        return ""

    def get_user_error(self, user):
        """Валидация пользователя"""
        if not user:
            return "Имя пользователя не может быть пустым"
        elif len(user) > 63:
            return "Имя пользователя слишком длинное (макс. 63 символа)"
        elif not all(c.isalnum() or c in '_-' for c in user):
            return "Имя пользователя содержит недопустимые символы"
        return ""

    def get_password_error(self, password):
        """Валидация пароля"""
        if len(password) > 100:
            return "Пароль слишком длинный (макс. 100 символов)"
        return ""

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
            /* Основной виджет */
            #mainWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0a0a0f, 
                                          stop: 1 #1a1a2e);
                border: 1px solid #2a2a3a;
            }

            /* Контейнер заголовка */
            #titleContainer {
                background: rgba(10, 10, 15, 0.7);
                border-radius: 12px;
                border: 1px solid #64ffda;
                padding: 15px;
            }

            /* Метки формы */
            #formLabel {
                font-size: 20px;
                font-weight: bold;
                color: #8892b0;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 5px 0;
                background: transparent;
                border: none;
            }

            /* Метки ошибок */
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

            /* Контейнер формы */
            #formContainer {
                background: rgba(15, 15, 25, 0.6);
                border-radius: 15px;
                padding: 25px;
            }

            /* Кнопка подключения */
            #connectButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #64ffda, 
                                          stop: 1 #00bcd4);
                border: none;
                border-radius: 10px;
                color: #0a0a0f;
                font-size: 18px;
                font-weight: bold;
                padding: 16px;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-family: 'Consolas', 'Fira Code', monospace;
            }

            #connectButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #50e3c2, 
                                          stop: 1 #00acc1);
                border: 2px solid #64ffda;
            }

            #connectButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3bc1a8, 
                                          stop: 1 #00838f);
                padding: 15px;
            }

            #connectButton:disabled {
                background: #44475a;
                color: #6272a4;
                border: 1px solid #6272a4;
            }

            /* Скроллбары */
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

    def on_connect_clicked(self):
        """Обработчик клика по кнопке подключения"""
        # Финальная проверка перед подключением
        self.validate_all_fields_realtime()

        # Проверяем, есть ли ошибки
        has_errors = any([
            self.host_error.text(),
            self.port_error.text(),
            self.dbname_error.text(),
            self.user_error.text(),
            self.password_error.text()
        ])

        if has_errors:
            notification.notify(
                title="Ошибки ввода",
                message="Пожалуйста, исправьте ошибки в форме перед подключением",
                timeout=5
            )
            return

        # Меняем текст кнопки во время подключения
        self.connect_button.setText("🔄 ПОДКЛЮЧЕНИЕ...")
        self.connect_button.setEnabled(False)
        QApplication.processEvents()

        # Запускаем подключение
        self.connect_to_database()

    def connect_to_database(self):
        """Подключение к базе данных"""
        # Сбор параметров
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        dbname = self.dbname_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()

        port = int(port)

        # Настройка логгера
        logger = logging.getLogger("DB")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        try:
            file_handler = logging.FileHandler("db/db_app.log", encoding='utf-8')
            log_file_path = "db/db_app.log"
        except FileNotFoundError:
            file_handler = logging.FileHandler("db_app.log", encoding='utf-8')
            log_file_path = "db_app.log"

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
            log_file=log_file_path
        )

        # Подключение
        connected = db.connect()

        # Показываем уведомление
        if connected:
            notification.notify(
                title="✅ Успешное подключение",
                message=f"Подключено к базе: {dbname}@{host}:{port}",
                timeout=5
            )
            self.db_instance = db
            self.main_window = MainWindow(db_instance=db)
            self.main_window.show()
            self.close()
        else:
            notification.notify(
                title="❌ Ошибка подключения",
                message="Не удалось подключиться к базе данных. Проверьте параметры.",
                timeout=5
            )
            self.connect_button.setText("ПОДКЛЮЧИТЬСЯ")
            self.connect_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DBConnectionWindow()
    window.show()
    sys.exit(app.exec())