import sqlite3
import json


def regions():
    with open("Data\\data.json", "r") as f:
        data = json.load(f)
    return list(data.keys())


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                age INTEGER
            );

            CREATE TABLE IF NOT EXISTS advisors (
                advisor_id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                age INTEGER
            );

            CREATE TABLE IF NOT EXISTS student_advisor (
                student_id INTEGER,
                advisor_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id),
                PRIMARY KEY (student_id, advisor_id)
            );
            ''')
            conn.commit()

    def add_data(self, table_name, name=None, surname=None, age=None, student_id=None, advisor_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if table_name != "student_advisor":
                cursor.execute(f"INSERT INTO {table_name} (name, surname, age) VALUES (?, ?, ?)",
                               (name, surname, age))
            else:
                cursor.execute(f"INSERT INTO {table_name} (student_id, advisor_id) VALUES (?,?)",
                               (student_id, advisor_id))
            conn.commit()

    def get_existing_relations(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, advisor_id FROM student_advisor")
            existing_relations = cursor.fetchall()
            return existing_relations

    def delete_row(self, table_name, row_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if table_name == "advisors":
                cursor.execute(f"DELETE FROM {table_name} WHERE advisor_id = ?", (row_id,))
            else:
                cursor.execute(f"DELETE FROM {table_name} WHERE student_id = ?", (row_id,))
            conn.commit()

    def load_data(self, table_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

    def search(self, table_name, name=None, surname=None, age=None, student_id=None, advisor_id=None):
        conditions = []
        values = ()
        if student_id:
            conditions.append("student_id LIKE ?")
            values += ('%' + student_id + '%',)
        if advisor_id:
            conditions.append("advisor_id LIKE ?")
            values += ('%' + advisor_id + '%',)
        if name:
            conditions.append("name LIKE ?")
            values += ('%' + name + '%',)
        if surname:
            conditions.append("surname LIKE ?")
            values += ('%' + surname + '%',)
        if age:
            conditions.append("age LIKE ?")
            values += ('%' + age + '%',)

        if conditions:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"SELECT * FROM {table_name} WHERE " + " AND ".join(conditions)
                cursor.execute(query, values)
                return cursor.fetchall()
        else:
            return self.load_data(table_name)

    def update(self, table_name, name, surname, age, id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if table_name == "students":
                cursor.execute(f"UPDATE {table_name} SET name = ?, surname = ?, age = ? WHERE student_id = ?",
                               (name, surname, age, id))
            elif table_name == "advisors":
                cursor.execute(f"UPDATE {table_name} SET name = ?, surname = ?, age = ? WHERE advisor_id = ?",
                               (name, surname, age, id))
            conn.commit()

    def check_bd(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_advisor")
            data = cursor.fetchall()
        return True if not data else False

    def list_advisors_with_students_count(self, order_by):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT advisors.advisor_id, advisors.name, advisors.surname, COUNT(student_advisor.student_id) 
                AS student_count
                FROM advisors
                LEFT JOIN student_advisor ON advisors.advisor_id = student_advisor.advisor_id
                GROUP BY advisors.advisor_id
                ORDER BY student_count {}
            '''.format(order_by))
            return cursor.fetchall()

    def list_students_with_advisors_count(self, order_by):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT students.student_id, students.name, students.surname, COUNT(student_advisor.advisor_id) 
                AS advisor_count
                FROM students
                LEFT JOIN student_advisor ON students.student_id = student_advisor.student_id
                GROUP BY students.student_id
                ORDER BY advisor_count {}
            '''.format(order_by))
            return cursor.fetchall()
