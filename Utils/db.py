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
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                age INTEGER
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS advisors (
                advisor_id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                age INTEGER
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_advisor (
                student_id INTEGER,
                advisor_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id),
                PRIMARY KEY (student_id, advisor_id)
            )
            ''')
            conn.commit()

    def load_column(self, column):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column} FROM employee")
            return [str(row[0]) for row in cursor.fetchall()]

    def add_data(self, table_name, name, surname, age):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"INSERT INTO {table_name} (name, surname, age) VALUES (?, ?, ?)"
    
            cursor.execute(query, (name, surname, age))
            conn.commit()

    def load_data(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employee")
            return cursor.fetchall()

    def delete_row(self, row_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employee WHERE id = ?", (row_id,))
            conn.commit()

    def search(self, name=None, surname=None, age=None, id=None):
        conditions = []
        values = ()
        if id:
            conditions.append("id LIKE ?")
            values += ('%' + id + '%',)
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
                query = "SELECT * FROM employee WHERE " + " AND ".join(conditions)
                cursor.execute(query, values)
                return cursor.fetchall()
        else:
            return self.load_data()

    def update(self, name, surname, age, id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE employee SET name = ?, surname = ?, age = ? WHERE id = ?", (name, surname, age, id))
            conn.commit()

    def most_common(self, value):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {value}, COUNT(*) AS count FROM employee GROUP BY {value} ORDER BY count DESC")
            return cursor.fetchone()

    def least_common(self, value):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {value}, COUNT(*) AS count FROM employee GROUP BY {value} ORDER BY count ASC")
            return cursor.fetchone()

    def average_age(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(age) FROM employee")
            return cursor.fetchone()[0]

    def same_name_surname_age(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM employee WHERE (name, surname, age) IN (SELECT name, surname, age FROM employee GROUP "
                "BY name, surname, age HAVING COUNT(*) > 1)")
            return cursor.fetchall()
        
    def check_bd(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employee")
            data = cursor.fetchall()
        return True if not data else False


# conn = sqlite3.connect('student_advisor.db')
# cursor = conn.cursor()

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS students (
#     student_id INTEGER PRIMARY KEY,
#     name TEXT
# )
# ''')

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS advisors (
#     advisor_id INTEGER PRIMARY KEY,
#     name TEXT
# )
# ''')

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS student_advisor (
#     student_id INTEGER,
#     advisor_id INTEGER,
#     FOREIGN KEY (student_id) REFERENCES students(student_id),
#     FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id),
#     PRIMARY KEY (student_id, advisor_id)
# )
# ''')

# cursor.execute('''
# INSERT INTO students (name) VALUES
# ('John'),
# ('Alice'),
# ('Bob'),
# ('Emily')
# ''')

# cursor.execute('''
# INSERT INTO advisors (name) VALUES
# ('Dr. Smith'),
# ('Prof. Johnson'),
# ('Dr. Brown')
# ''')

# cursor.execute('''
# INSERT INTO student_advisor (student_id, advisor_id) VALUES
# (1, 1),
# (2, 1),
# (3, 2),
# (4, 3),
# (1, 3),
# (4, 1)
# ''')

# conn.commit()

# cursor.execute('''
# SELECT advisors.name, COUNT(student_advisor.student_id) AS num_students
# FROM advisors
# LEFT JOIN student_advisor ON advisors.advisor_id = student_advisor.advisor_id
# GROUP BY advisors.name
# ''')

# advisors_with_students = cursor.fetchall()

# for advisor in advisors_with_students:
#     print(f"{advisor[0]}: {advisor[1]} students")

# conn.close()
