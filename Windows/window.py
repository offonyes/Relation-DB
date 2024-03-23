from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from Windows.MainWindow import Ui_MainWindow
from Utils.db import *
from Utils.utils import Worker


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.worker = None
        self.thread = None
        self.setupUi(self)
        self.db = DatabaseManager("Data\\Student_Advisor.db")
        self.db.create_table()
        self.region_cb.addItems(regions())
        self.region_cb.setCurrentIndex(23)
        self.home_btn_1.clicked.connect(lambda: self.change_page(self.page))
        self.home_btn_2.clicked.connect(lambda: self.change_page(self.page))
        self.random_btn_1.clicked.connect(lambda: self.change_page(self.page_2))
        self.random_btn_2.clicked.connect(lambda: self.change_page(self.page_2))
        self.student_btn_1.clicked.connect(lambda: self.change_page(self.page_3, "students"))
        self.student_btn_2.clicked.connect(lambda: self.change_page(self.page_3, "students"))
        self.advisors_btn_1.clicked.connect(lambda: self.change_page(self.page_3, "advisors"))
        self.advisors_btn_2.clicked.connect(lambda: self.change_page(self.page_3, "advisors"))
        self.relation_btn_1.clicked.connect(lambda: self.change_page(self.page_4, "student_advisor"))
        self.relation_btn_2.clicked.connect(lambda: self.change_page(self.page_4, "student_advisor"))
        self.random_db_pb.clicked.connect(
            lambda: self.add_random_data(self.region_cb.currentText(), int(self.student_dsb.value()),
                                         int(self.advisors_dsb.value()), int(self.relation_dsb.value())))
        self.add_button.clicked.connect(
            lambda: self.add_one_data(self.name_input.text(), self.surname_input.text(), self.age_input.text()))
        self.add_button_2.clicked.connect(
            lambda: self.add_one_relation(self.student_id.text(), self.advisor_id_input.text())
        )
        self.delete_button.clicked.connect(lambda: self.delete_data())
        self.delete_button_2.clicked.connect(lambda: self.delete_data("student_advisor", self.tableWidget_2))
        self.search_button.clicked.connect(
            lambda: self.search_info(self.name_input.text(), self.surname_input.text(), self.age_input.text()))
        self.search_button_2.clicked.connect(lambda:
                                             self.search_info_relation(self.student_id.text(),
                                                                       self.advisor_id_input.text()))
        self.save_button.clicked.connect(self.save)
        self.action_cb.currentIndexChanged.connect(self.action_combobox_changed)
        self.result_btn.clicked.connect(lambda: self.action(self.action_cb.currentIndex()))

    @staticmethod
    def format_result(data, st_or_ad, order=None):
        formatted_output = f"Order: {order}\n\n"
        for _, name, surname, students_count in data:
            formatted_output += f"{name} {surname} has {students_count} {st_or_ad}\n"
        return formatted_output
    
    def action(self, index):
        result = ""
        if self.db.check_bd():
            QMessageBox.warning(self, "Warning", "There are no data in the database.\nGenerate randomly or add "
                                                 "manually.")
            return
        order = {"Ascending.": "ASC",
                 "Descending.": "DESC"}
        match index:
            case 0:
                data = self.db.list_advisors_with_students_count(order[self.choose_3.currentText()])
                result = self.format_result(data, "students", self.choose_3.currentText())
            case 1:
                data = self.db.list_students_with_advisors_count(order[self.choose_3.currentText()])
                result = self.format_result(data, "advisors", self.choose_3.currentText())
            case 2:
                _, name, surname, students_count = self.db.list_advisors_with_students_count("DESC")[0]
                result = f"{name} {surname} has the largest number of students, that is {students_count} "
            case 3:
                _, name, surname, students_count = self.db.list_advisors_with_students_count("ASC")[0]
                result = f"{name} {surname} has the smallest number of students, that is {students_count} "
            case 4:
                _, name, surname, advisors_count = self.db.list_students_with_advisors_count("DESC")[0]
                result = f"{name} {surname} has the largest number of advisors, that is {advisors_count} "
            case 5:
                _, name, surname, advisors_count = self.db.list_students_with_advisors_count("ASC")[0]
                result = f"{name} {surname} has the smallest number of advisors, that is {advisors_count} "
        self.result_lbl.setText(result)

    def action_combobox_changed(self, index):
        if index == 1 or index == 0:
            self.choose_3.show()
        else:
            self.choose_3.hide()

    def save(self):
        table_name = self.st_ad_groupbox.title().split(" ")[0].lower()
        for row in range(self.tableWidget.rowCount()):
            name = self.tableWidget.item(row, 1).text()
            surname = self.tableWidget.item(row, 2).text()
            age = self.tableWidget.item(row, 3).text()

            row_id = int(self.tableWidget.item(row, 0).text())
            self.db.update(table_name, name, surname, age, row_id)

        QMessageBox.information(self, "Success", "Successfully saved all changes.")

    def search_info_relation(self, student_id, advisor_id):
        tablewidget = self.tableWidget_2
        self.load_data_into_table(self.db.search("student_advisor", student_id=student_id, advisor_id=advisor_id),
                                  tablewidget)

    def search_info(self, name, surname, age):
        table_name = self.st_ad_groupbox.title().split(" ")[0].lower()
        tablewidget = self.tableWidget
        self.load_data_into_table(self.db.search(table_name, name=name, surname=surname, age=age), tablewidget)

    def add_one_relation(self, student_id, advisor_id):
        existing_relations = set(self.db.get_existing_relations())
        if student_id == "" or advisor_id == "":
            QMessageBox.warning(self, "Warning", "Please enter all information.")
            return
        student_id = int(student_id)
        advisor_id = int(advisor_id)
        if (student_id, advisor_id) not in existing_relations:
            self.db.add_data("student_advisor", student_id=student_id, advisor_id=advisor_id)
            self.load_data_into_table(self.db.load_data("student_advisor"), self.tableWidget_2)
        else:
            QMessageBox.warning(self, "Warning", "This relation exist.")

    def delete_data(self, table_name=None, tablewidget=None):
        if table_name is None:
            table_name = self.st_ad_groupbox.title().split(" ")[0].lower()
            tablewidget = self.tableWidget
        selected_rows = tablewidget.selectedItems()
        selected_indexes = set()
        for item in selected_rows:
            selected_indexes.add(item.row())

        confirm_dialog = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Do you really want to delete data in  {list(selected_indexes)}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm_dialog == QMessageBox.Yes:
            for index in sorted(selected_indexes, reverse=True):
                row_id = tablewidget.item(index, 0).text()
                self.db.delete_row(table_name, row_id)

            self.load_data_into_table(self.db.load_data(table_name), tablewidget)

    def add_random_data(self, region, student_number, advisor_number, relation_number):
        self.random_groupbox.setEnabled(False)
        self.random_db_pb.setEnabled(False)
        self.thread = QThread()
        self.worker = Worker(region, student_number, advisor_number, relation_number)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.worker.progress_bar.connect(self.handle_progressbar)
        self.worker.finished.connect(self.handle_results)

    def handle_progressbar(self, percentage):
        self.random_progressbar.setValue(percentage)

    def handle_results(self):
        QMessageBox.information(self, "Success", "Successfully generated and saved.")
        self.random_groupbox.setEnabled(True)
        self.random_db_pb.setEnabled(True)

    def change_page(self, name, index=None):
        self.stackedWidget.setCurrentWidget(name)
        self.name_input.clear()
        self.surname_input.clear()
        self.age_input.clear()
        if index == "students":
            self.st_ad_groupbox.setTitle("Students DB")
            self.load_data_into_table(self.db.load_data(index), self.tableWidget)
        elif index == "advisors":
            self.st_ad_groupbox.setTitle("Advisors DB")
            self.load_data_into_table(self.db.load_data(index), self.tableWidget)
        elif index == "student_advisor":
            self.load_data_into_table(self.db.load_data(index), self.tableWidget_2)

    def add_one_data(self, name, surname, age):
        table_name = self.st_ad_groupbox.title().split(" ")[0].lower()
        if name and surname and age:
            self.db.add_data(table_name, name=name, surname=surname, age=age)
            self.load_data_into_table(self.db.load_data(table_name), self.tableWidget)
        else:
            QMessageBox.warning(self, "Warning", "Please enter all information.")

    def load_data_into_table(self, data, tablewidget):
        tablewidget.clearContents()
        tablewidget.setRowCount(0)
        for row_index, row_data in enumerate(data):
            tablewidget.setRowCount(tablewidget.rowCount() + 1)
            for column_index, column_data in enumerate(row_data):
                item = QTableWidgetItem(str(column_data))
                tablewidget.setItem(row_index, column_index, item)
            item = tablewidget.item(row_index, 0)
            item.setFlags(item.flags() ^ 2)
            if tablewidget == self.tableWidget_2:
                item = tablewidget.item(row_index, 1)
                item.setFlags(item.flags() ^ 2)
