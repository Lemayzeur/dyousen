import sqlite3
from config.utils import hash_password
from db import get_connection

user_data = [
    ("yousenie", hash_password("admin1234")),
    ("max", hash_password("admin1234"))
]

student_data = [
    ("Jean", "Dupont", 2),
    ("Jacques", "Martin", 1),
    ("Sophie", "Leclerc", 3),
    ("Alexandre", "Lefevre", 5),
    ("Camille", "Girard", 1),
    ("Lucas", "Roy", 4),
    ("Charlotte", "Lavoie", 2),
    ("Hugo", "Gagnon", 3),
    ("Emma", "Boucher", 5),
    ("Maxime", "Morin", 1),
    ("Léa", "Fortin", 4),
    ("Thomas", "Bergeron", 2),
    ("Clara", "Poirier", 3),
    ("Gabriel", "Caron", 5),
    ("Zoé", "Tremblay", 1),
    ("Nathan", "Gauthier", 4),
    ("Manon", "Desjardins", 3),
    ("Louis", "Lemieux", 2),
    ("Chloé", "Rousseau", 5),
    ("Arthur", "Côté", 1),
]

teacher_data = [
    ("Georges", "BUsh"),
    ("Bill", "Gates"),
    ("Jeff", "Bezos"),
    ("Elon", "Musk"),
    ("Mark", "Zuckerberg"),
]

classroom_data = [
    ("L1",),
    ("L2",),
    ("L3",),
    ("L4",),
    ("L5",),
]

teacher_classroom_data = [
    (1, 2),
    (2, 1),
    (3, 3),
    (4, 4),
    (5, 5),
    (1, 3),
    (2, 2),
    (3, 5),
    (4, 1),
    (5, 4),
]

def insert_initial_data():
    connection = get_connection()
    cursor = connection.cursor()

    # Insert sample data into students tables
    cursor.executemany("INSERT INTO students (first_name, last_name, classroom_id) VALUES (?, ?, ?)", student_data)

    # Insert user data into the users table
    cursor.executemany("INSERT INTO users (email, password) VALUES (?, ?)", user_data)

    # Insert user data into the teachers table
    cursor.executemany("INSERT INTO teachers (first_name, last_name) VALUES (?, ?)", teacher_data)


    # Insert user data into the classrooms table
    cursor.executemany("INSERT INTO classrooms (name) VALUES (?)", classroom_data)

    # Insert user data into the teacher_classroom_data table
    cursor.executemany("INSERT INTO teacher_classrooms (teacher_id, classroom_id) VALUES (?, ?)", teacher_classroom_data)
    
    # Repeat for other tables

    connection.commit()
    connection.close()

if __name__ == "__main__":
    insert_initial_data()
