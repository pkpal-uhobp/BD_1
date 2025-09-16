# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListView, QMainWindow,
    QPushButton, QSizePolicy, QTabWidget, QTableView,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet(u"background-color: black; ")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_5 = QVBoxLayout(self.tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color: argb(255,255,255,30)")
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame1 = QFrame(self.frame)
        self.frame1.setObjectName(u"frame1")
        self.frame1.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.frame1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame2 = QFrame(self.frame1)
        self.frame2.setObjectName(u"frame2")
        self.frame2.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.frame2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.host_lineEdit = QLineEdit(self.frame2)
        self.host_lineEdit.setObjectName(u"host_lineEdit")

        self.horizontalLayout.addWidget(self.host_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frame2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.port_lineEdit = QLineEdit(self.frame2)
        self.port_lineEdit.setObjectName(u"port_lineEdit")

        self.horizontalLayout_2.addWidget(self.port_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.frame2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.user_lineEdit = QLineEdit(self.frame2)
        self.user_lineEdit.setObjectName(u"user_lineEdit")

        self.horizontalLayout_3.addWidget(self.user_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.frame2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.password_lineEdit = QLineEdit(self.frame2)
        self.password_lineEdit.setObjectName(u"password_lineEdit")

        self.horizontalLayout_4.addWidget(self.password_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addWidget(self.frame2)


        self.verticalLayout_3.addWidget(self.frame1)

        self.log_listView = QListView(self.frame)
        self.log_listView.setObjectName(u"log_listView")

        self.verticalLayout_3.addWidget(self.log_listView)

        self.connection_pushButton = QPushButton(self.frame)
        self.connection_pushButton.setObjectName(u"connection_pushButton")

        self.verticalLayout_3.addWidget(self.connection_pushButton)

        self.connection_pushButton_5 = QPushButton(self.frame)
        self.connection_pushButton_5.setObjectName(u"connection_pushButton_5")

        self.verticalLayout_3.addWidget(self.connection_pushButton_5)

        self.connection_pushButton_4 = QPushButton(self.frame)
        self.connection_pushButton_4.setObjectName(u"connection_pushButton_4")

        self.verticalLayout_3.addWidget(self.connection_pushButton_4)


        self.verticalLayout_5.addWidget(self.frame)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_16 = QVBoxLayout(self.tab_2)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.frame3 = QFrame(self.tab_2)
        self.frame3.setObjectName(u"frame3")
        self.frame3.setStyleSheet(u"background-color: rgba(255,255,255,30)")
        self.verticalLayout_15 = QVBoxLayout(self.frame3)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_11 = QLabel(self.frame3)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_11.addWidget(self.label_11)

        self.book_name_lineEdit = QLineEdit(self.frame3)
        self.book_name_lineEdit.setObjectName(u"book_name_lineEdit")

        self.horizontalLayout_11.addWidget(self.book_name_lineEdit)


        self.verticalLayout_14.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_12 = QLabel(self.frame3)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_12.addWidget(self.label_12)

        self.book_author_lineEdit = QLineEdit(self.frame3)
        self.book_author_lineEdit.setObjectName(u"book_author_lineEdit")

        self.horizontalLayout_12.addWidget(self.book_author_lineEdit)


        self.verticalLayout_14.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_21 = QLabel(self.frame3)
        self.label_21.setObjectName(u"label_21")

        self.horizontalLayout_21.addWidget(self.label_21)

        self.book_genre_lineEdit = QLineEdit(self.frame3)
        self.book_genre_lineEdit.setObjectName(u"book_genre_lineEdit")

        self.horizontalLayout_21.addWidget(self.book_genre_lineEdit)


        self.verticalLayout_14.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_22 = QLabel(self.frame3)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_22.addWidget(self.label_22)

        self.book_deposit_lineEdit = QLineEdit(self.frame3)
        self.book_deposit_lineEdit.setObjectName(u"book_deposit_lineEdit")

        self.horizontalLayout_22.addWidget(self.book_deposit_lineEdit)


        self.verticalLayout_14.addLayout(self.horizontalLayout_22)


        self.verticalLayout_15.addLayout(self.verticalLayout_14)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_23 = QLabel(self.frame3)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_23.addWidget(self.label_23)

        self.book_daily_rental_rate_lineEdit = QLineEdit(self.frame3)
        self.book_daily_rental_rate_lineEdit.setObjectName(u"book_daily_rental_rate_lineEdit")

        self.horizontalLayout_23.addWidget(self.book_daily_rental_rate_lineEdit)


        self.verticalLayout_15.addLayout(self.horizontalLayout_23)

        self.add_book_pushButton = QPushButton(self.frame3)
        self.add_book_pushButton.setObjectName(u"add_book_pushButton")

        self.verticalLayout_15.addWidget(self.add_book_pushButton)

        self.delete_book_pushButton = QPushButton(self.frame3)
        self.delete_book_pushButton.setObjectName(u"delete_book_pushButton")

        self.verticalLayout_15.addWidget(self.delete_book_pushButton)

        self.edit_book_pushButton = QPushButton(self.frame3)
        self.edit_book_pushButton.setObjectName(u"edit_book_pushButton")

        self.verticalLayout_15.addWidget(self.edit_book_pushButton)

        self.book_tableView = QTableView(self.frame3)
        self.book_tableView.setObjectName(u"book_tableView")

        self.verticalLayout_15.addWidget(self.book_tableView)


        self.verticalLayout_16.addWidget(self.frame3)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_19 = QVBoxLayout(self.tab_3)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.frame_7 = QFrame(self.tab_3)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"background-color: rgba(255,255,255,30)")
        self.verticalLayout_17 = QVBoxLayout(self.frame_7)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_24 = QLabel(self.frame_7)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_24.addWidget(self.label_24)

        self.reader_last_name_lineEdit = QLineEdit(self.frame_7)
        self.reader_last_name_lineEdit.setObjectName(u"reader_last_name_lineEdit")

        self.horizontalLayout_24.addWidget(self.reader_last_name_lineEdit)


        self.verticalLayout_18.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_25 = QLabel(self.frame_7)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_25.addWidget(self.label_25)

        self.reader_first_name_lineEdit = QLineEdit(self.frame_7)
        self.reader_first_name_lineEdit.setObjectName(u"reader_first_name_lineEdit")

        self.horizontalLayout_25.addWidget(self.reader_first_name_lineEdit)


        self.verticalLayout_18.addLayout(self.horizontalLayout_25)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_26 = QLabel(self.frame_7)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_26.addWidget(self.label_26)

        self.reader_middle_name_lineEdit = QLineEdit(self.frame_7)
        self.reader_middle_name_lineEdit.setObjectName(u"reader_middle_name_lineEdit")

        self.horizontalLayout_26.addWidget(self.reader_middle_name_lineEdit)


        self.verticalLayout_18.addLayout(self.horizontalLayout_26)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.label_27 = QLabel(self.frame_7)
        self.label_27.setObjectName(u"label_27")

        self.horizontalLayout_27.addWidget(self.label_27)

        self.reader_address_lineEdit = QLineEdit(self.frame_7)
        self.reader_address_lineEdit.setObjectName(u"reader_address_lineEdit")

        self.horizontalLayout_27.addWidget(self.reader_address_lineEdit)


        self.verticalLayout_18.addLayout(self.horizontalLayout_27)


        self.verticalLayout_17.addLayout(self.verticalLayout_18)

        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.label_28 = QLabel(self.frame_7)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_28.addWidget(self.label_28)

        self.reader_phone_lineEdit = QLineEdit(self.frame_7)
        self.reader_phone_lineEdit.setObjectName(u"reader_phone_lineEdit")

        self.horizontalLayout_28.addWidget(self.reader_phone_lineEdit)


        self.verticalLayout_17.addLayout(self.horizontalLayout_28)

        self.horizontalLayout_30 = QHBoxLayout()
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.label_30 = QLabel(self.frame_7)
        self.label_30.setObjectName(u"label_30")

        self.horizontalLayout_30.addWidget(self.label_30)

        self.reader_discount_category_lineEdit = QLineEdit(self.frame_7)
        self.reader_discount_category_lineEdit.setObjectName(u"reader_discount_category_lineEdit")

        self.horizontalLayout_30.addWidget(self.reader_discount_category_lineEdit)


        self.verticalLayout_17.addLayout(self.horizontalLayout_30)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.label_31 = QLabel(self.frame_7)
        self.label_31.setObjectName(u"label_31")

        self.horizontalLayout_31.addWidget(self.label_31)

        self.reader_discount_percent_lineEdit = QLineEdit(self.frame_7)
        self.reader_discount_percent_lineEdit.setObjectName(u"reader_discount_percent_lineEdit")

        self.horizontalLayout_31.addWidget(self.reader_discount_percent_lineEdit)


        self.verticalLayout_17.addLayout(self.horizontalLayout_31)

        self.add_reader_pushButton_2 = QPushButton(self.frame_7)
        self.add_reader_pushButton_2.setObjectName(u"add_reader_pushButton_2")

        self.verticalLayout_17.addWidget(self.add_reader_pushButton_2)

        self.delete_reader_pushButton = QPushButton(self.frame_7)
        self.delete_reader_pushButton.setObjectName(u"delete_reader_pushButton")

        self.verticalLayout_17.addWidget(self.delete_reader_pushButton)

        self.edit_reader_pushButton = QPushButton(self.frame_7)
        self.edit_reader_pushButton.setObjectName(u"edit_reader_pushButton")

        self.verticalLayout_17.addWidget(self.edit_reader_pushButton)

        self.reader_tableView = QTableView(self.frame_7)
        self.reader_tableView.setObjectName(u"reader_tableView")

        self.verticalLayout_17.addWidget(self.reader_tableView)


        self.verticalLayout_19.addWidget(self.frame_7)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_22 = QVBoxLayout(self.tab_4)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.frame_8 = QFrame(self.tab_4)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setStyleSheet(u"background-color: rgba(255,255,255,30)")
        self.verticalLayout_20 = QVBoxLayout(self.frame_8)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.label_32 = QLabel(self.frame_8)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_32.addWidget(self.label_32)

        self.issued_book_id_lineEdit = QLineEdit(self.frame_8)
        self.issued_book_id_lineEdit.setObjectName(u"issued_book_id_lineEdit")

        self.horizontalLayout_32.addWidget(self.issued_book_id_lineEdit)


        self.verticalLayout_21.addLayout(self.horizontalLayout_32)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.label_33 = QLabel(self.frame_8)
        self.label_33.setObjectName(u"label_33")

        self.horizontalLayout_33.addWidget(self.label_33)

        self.issued_reader_id_lineEdit = QLineEdit(self.frame_8)
        self.issued_reader_id_lineEdit.setObjectName(u"issued_reader_id_lineEdit")

        self.horizontalLayout_33.addWidget(self.issued_reader_id_lineEdit)


        self.verticalLayout_21.addLayout(self.horizontalLayout_33)

        self.horizontalLayout_34 = QHBoxLayout()
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.label_34 = QLabel(self.frame_8)
        self.label_34.setObjectName(u"label_34")

        self.horizontalLayout_34.addWidget(self.label_34)

        self.issued_date_lineEdit = QLineEdit(self.frame_8)
        self.issued_date_lineEdit.setObjectName(u"issued_date_lineEdit")

        self.horizontalLayout_34.addWidget(self.issued_date_lineEdit)


        self.verticalLayout_21.addLayout(self.horizontalLayout_34)

        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.label_35 = QLabel(self.frame_8)
        self.label_35.setObjectName(u"label_35")

        self.horizontalLayout_35.addWidget(self.label_35)

        self.issued_return_date_lineEdit = QLineEdit(self.frame_8)
        self.issued_return_date_lineEdit.setObjectName(u"issued_return_date_lineEdit")

        self.horizontalLayout_35.addWidget(self.issued_return_date_lineEdit)


        self.verticalLayout_21.addLayout(self.horizontalLayout_35)


        self.verticalLayout_20.addLayout(self.verticalLayout_21)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_36 = QLabel(self.frame_8)
        self.label_36.setObjectName(u"label_36")

        self.horizontalLayout_36.addWidget(self.label_36)

        self.issued_damage_type_lineEdit = QLineEdit(self.frame_8)
        self.issued_damage_type_lineEdit.setObjectName(u"issued_damage_type_lineEdit")

        self.horizontalLayout_36.addWidget(self.issued_damage_type_lineEdit)


        self.verticalLayout_20.addLayout(self.horizontalLayout_36)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")

        self.verticalLayout_20.addLayout(self.horizontalLayout_38)

        self.issue_book_pushButton = QPushButton(self.frame_8)
        self.issue_book_pushButton.setObjectName(u"issue_book_pushButton")

        self.verticalLayout_20.addWidget(self.issue_book_pushButton)

        self.edit_issued_history_pushButton = QPushButton(self.frame_8)
        self.edit_issued_history_pushButton.setObjectName(u"edit_issued_history_pushButton")

        self.verticalLayout_20.addWidget(self.edit_issued_history_pushButton)

        self.delete_issue_pushButton = QPushButton(self.frame_8)
        self.delete_issue_pushButton.setObjectName(u"delete_issue_pushButton")

        self.verticalLayout_20.addWidget(self.delete_issue_pushButton)

        self.reader_tableView_2 = QTableView(self.frame_8)
        self.reader_tableView_2.setObjectName(u"reader_tableView_2")

        self.verticalLayout_20.addWidget(self.reader_tableView_2)


        self.verticalLayout_22.addWidget(self.frame_8)

        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout_4.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"host", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"port", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"user", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"password", None))
        self.connection_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f \u043a \u0431\u0434", None))
        self.connection_pushButton_5.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0441\u0445\u0435\u043c\u0443", None))
        self.connection_pushButton_4.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0441\u0445\u0435\u043c\u0443", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u043d\u0438\u0433\u0438", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0432\u0442\u043e\u0440", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"\u0416\u0430\u043d\u0440", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0432 \u0434\u0435\u043d\u044c", None))
        self.add_book_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043a\u043d\u0438\u0433\u0443", None))
        self.delete_book_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u043a\u043d\u0438\u0433\u0443", None))
        self.edit_book_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043a\u043d\u0438\u0433\u0443", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\u041a\u043d\u0438\u0433\u0438", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0434\u0440\u0435\u0441", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0435\u043b\u0435\u0444\u043e\u043d", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u0438\u0434\u043a\u0430 \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.add_reader_pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.delete_reader_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.edit_reader_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"\u0427\u0438\u0442\u0430\u0442\u0435\u043b\u0438", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"id \u043a\u043d\u0438\u0433\u0438", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"id \u0447\u0438\u0442\u0430\u0442\u0435\u043b\u044f", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430 \u0432\u044b\u0434\u0430\u0447\u0438", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u0435\u0434\u043f\u043e\u043b\u0430\u0433\u0430\u0435\u043c\u0430\u044f \u0434\u0430\u0442\u0430 \u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0435\u043d\u0438\u044f", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0432\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u044f", None))
        self.issue_book_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0434\u0430\u0442\u044c \u043a\u043d\u0438\u0433\u0443", None))
        self.edit_issued_history_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0438\u0441\u0442\u043e\u0440\u0438\u044e \u0432\u044b\u0434\u0430\u0447\u0438", None))
        self.delete_issue_pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u044c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"\u0418\u0441\u0442\u043e\u0440\u0438\u044f", None))
    # retranslateUi

