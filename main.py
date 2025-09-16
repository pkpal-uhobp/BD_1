from db.Class_DB import DB

import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QStandardItemModel, QStandardItem

from ui.ui_main_rc import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = DB()

        self.log_model = QStandardItemModel()
        self.ui.log_listView.setModel(self.log_model)

        # 👇 ДОБАВЬ ЭТО — сохраняем ссылку на tabWidget
        self.tabWidget = self.ui.tabWidget  # ← Это важно!
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.connect_signals()

    def connect_signals(self):
        self.ui.connection_pushButton.clicked.connect(self.connect_to_db)
        self.ui.connection_pushButton_5.clicked.connect(self.create_schema)
        self.ui.connection_pushButton_4.clicked.connect(self.drop_schema)

        # 👇 Новые кнопки
        self.ui.add_book_pushButton.clicked.connect(self.add_book)
        # self.ui.delete_book_pushButton.clicked.connect(self.delete_book)
        # self.ui.edit_book_pushButton.clicked.connect(self.edit_book)

        # Аналогично для читателей и выдач
        # self.ui.add_reader_pushButton_2.clicked.connect(self.add_reader)
        # self.ui.delete_reader_pushButton.clicked.connect(self.delete_reader)
        # self.ui.edit_reader_pushButton.clicked.connect(self.edit_reader)
        #
        # self.ui.issue_book_pushButton.clicked.connect(self.issue_book)
        # self.ui.delete_issue_pushButton.clicked.connect(self.delete_issue)
        # self.ui.edit_issued_history_pushButton.clicked.connect(self.edit_issue)

    def connect_to_db(self):
        host = self.ui.host_lineEdit.text()
        port = self.ui.port_lineEdit.text()
        user = self.ui.user_lineEdit.text()
        password = self.ui.password_lineEdit.text()

        self.db.host = host
        self.db.port = int(port) if port else 5432
        self.db.user = user
        self.db.password = password

        if self.db.connect():
            self.add_log("Успешное подключение к БД")
        else:
            self.add_log("Ошибка подключения к БД")

    def create_schema(self):
        """Создание схемы БД"""
        if self.db.create_schema():
            self.add_log("Схема БД успешно создана")
        else:
            self.add_log("Ошибка создания схемы БД")

    def drop_schema(self):
        """Удаление схемы БД"""
        if self.db.drop_schema():
            self.add_log("Схема БД успешно удалена")
        else:
            self.add_log("Ошибка удаления схемы БД")

    def add_log(self, message):
        """Добавляет сообщение в лог-лист и прокручивает вниз"""
        item = QStandardItem(message)
        self.log_model.appendRow(item)

        # Автоматически прокручиваем вниз при добавлении нового сообщения
        index = self.log_model.index(self.log_model.rowCount() - 1, 0)
        self.ui.log_listView.scrollTo(index)

    def on_tab_changed(self, index):
        """Загрузка данных при переключении вкладок"""
        if index == 1:  # Вкладка "Книги"
            self.load_books_data()
        elif index == 2:  # Вкладка "Читатели"
            self.load_readers_data()
        elif index == 3:  # Вкладка "История"
            self.load_issued_books_data()

    def add_book(self):
        name = self.ui.book_name_lineEdit.text().strip()
        author = self.ui.book_author_lineEdit.text().strip()
        genre = self.ui.book_genre_lineEdit.text().strip()
        cost = self.ui.book_deposit_lineEdit.text().strip()
        daily_rate = self.ui.book_daily_rental_rate_lineEdit.text().strip()

        if not all([name, author, genre, cost, daily_rate]):
            self.add_log("⚠️ Все поля должны быть заполнены!")
            return

        try:
            cost = float(cost)
            daily_rate = float(daily_rate)
        except ValueError:
            self.add_log("❌ Стоимость и цена в день должны быть числами!")
            return

        if self.db.insert_data("Books", {
           "title": name,
           "authors": [author],
           "genre": genre,
           "deposit_amount": cost,
           "daily_rental_rate": daily_rate
       }):
            self.add_log(f"✅ Книга '{name}' добавлена")
            self.load_books_data()  # Обновляем таблицу
            self.clear_book_inputs()  # Очищаем поля
        else:
            self.add_log("❌ Ошибка добавления книги")

    def clear_book_inputs(self):
        self.ui.book_name_lineEdit.clear()
        self.ui.book_author_lineEdit.clear()
        self.ui.book_genre_lineEdit.clear()
        self.ui.book_deposit_lineEdit.clear()
        self.ui.book_daily_rental_rate_lineEdit.clear()

    def load_books_data(self):
        """Загрузка данных о книгах в таблицу book_tableView"""
        books = self.db.get_table_data("Books")
        print(books)
        # Очищаем старую модель
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Жанр", "Стоимость", "Цена в день"])

        for book in books:
            row = []
            for field in book.keys():  # book — кортеж или список полей
                item = QStandardItem(str(book[field]))
                item.setEditable(False)  # Только для просмотра
                row.append(item)
            model.appendRow(row)

        self.ui.book_tableView.setModel(model)
        self.ui.book_tableView.resizeColumnsToContents()

    def load_readers_data(self):
        """Загрузка данных о читателях в таблицу"""
        readers = self.db.get_table_data("Readers")
        # Создание модели для таблицы

    def load_issued_books_data(self):
        """Загрузка данных о выданных книгах"""
        issued_books = self.db.get_table_data("Issued_Books")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
