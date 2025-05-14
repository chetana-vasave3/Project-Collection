import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                course TEXT NOT NULL)''')

c.execute('''CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                topic TEXT,
                file_name TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id))''')

conn.commit()
conn.close()
