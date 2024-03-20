from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Windows.MainWindow import Ui_MainWindow
from Utils.db import DatabaseManager


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.choose_3.hide()
        self.db = DatabaseManager("Data\\Student_Advisor.db")
        self.db.create_table()
        self.home_btn_1.clicked.connect(lambda: self.change_page(self.page))
        self.home_btn_2.clicked.connect(lambda: self.change_page(self.page))
        self.random_btn_1.clicked.connect(lambda: self.change_page(self.page_2)) 
        self.random_btn_2.clicked.connect(lambda: self.change_page(self.page_2)) 
        self.student_btn_1.clicked.connect(lambda: self.change_page(self.page_3, "Student"))
        self.student_btn_2.clicked.connect(lambda: self.change_page(self.page_3, "Student"))
        self.advisors_btn_1.clicked.connect(lambda: self.change_page(self.page_3, "Advisor"))
        self.advisors_btn_2.clicked.connect(lambda: self.change_page(self.page_3, "Advisor"))
        self.relation_btn_1.clicked.connect(lambda: self.change_page(self.page_4))
        self.relation_btn_2.clicked.connect(lambda: self.change_page(self.page_4))

    def change_page(self, name, index = None):
        self.stackedWidget.setCurrentWidget(name)
        if index == "Student":
            self.groupBox_2.setTitle("Student DB")
        elif index == "Advisor":
            self.groupBox_2.setTitle("Advisor DB")