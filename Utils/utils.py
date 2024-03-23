from PyQt5.QtCore import *
from Utils.db import DatabaseManager
import json
import random
from threading import Thread


class Worker(QObject):
    progress_bar = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, region, student_number, advisor_number, relation_number):
        super(Worker, self).__init__()
        self.names = None
        self.surnames = None
        self.region = region
        self.student_number = student_number
        self.advisor_number = advisor_number
        self.relation_number = relation_number
        self.all_number = self.student_number + self.advisor_number + self.relation_number
        self.percentage = 0
        self.db = DatabaseManager("Data\\Student_Advisor.db")
        self.load_data()

    def load_data(self):
        with open("Data\\data.json", "r") as f:
            data = json.load(f)
        self.names = data[self.region]["male"] + data[self.region]["female"]
        self.surnames = data[self.region]["surnames"]

    def random_data(self, min_age, max_age):
        name = random.choice(self.names)
        surname = random.choice(self.surnames)
        age = random.randint(min_age, max_age)
        return name, surname, age

    def student_run(self, number):
        for _ in range(number):
            name, surname, age = self.random_data(18, 30)
            self.db.add_data("students", name=name, surname=surname, age=age)
            self.percentage += 1
            self.progress_bar.emit(int((self.percentage / self.all_number) * 100 + 1))

    def advisor_run(self, number):
        for _ in range(number):
            name, surname, age = self.random_data(35, 60)
            self.db.add_data("advisors", name=name, surname=surname, age=age)
            self.percentage += 1
            self.progress_bar.emit(int((self.percentage / self.all_number) * 100 + 1))

    def relation_run(self, number):
        existing_relations = set(self.db.get_existing_relations())

        for _ in range(number):
            student_id = random.randint(1, self.student_number + 1)
            advisor_id = random.randint(1, self.advisor_number + 1)

            while (student_id, advisor_id) in existing_relations:
                student_id = random.randint(1, self.student_number + 1)
                advisor_id = random.randint(1, self.advisor_number + 1)

            existing_relations.add((student_id, advisor_id))
            self.db.add_data("student_advisor", student_id=student_id, advisor_id=advisor_id)
            self.percentage += 1
            self.progress_bar.emit(int((self.percentage / self.all_number) * 100 + 1))

    def run(self):
        threads = [Thread(target=self.student_run, args=(self.student_number,)),
                   Thread(target=self.advisor_run, args=(self.advisor_number,)),
                   Thread(target=self.relation_run, args=(self.relation_number,))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.finished.emit(True)
