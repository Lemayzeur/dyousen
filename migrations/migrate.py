from pathlib import Path
from db import get_connection

import os
import sqlite3

def create_tables():
    connection = get_connection()
    
    cursor = connection.cursor()
    print('Table students: CREATED')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            classroom_id INTEGER,
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
        )
    ''')
    print('Table users: CREATED')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT
        )
    ''')
    print('Table teachers: CREATED')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT
        )
    ''')
    print('Table classrooms: CREATED')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    print('Table teacher_classrooms: CREATED')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_classrooms (
            id INTEGER PRIMARY KEY,
            teacher_id INTEGER,
            classroom_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id),
            FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
        )
    ''')
    connection.commit()
    connection.close()

def get_applied_migrations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
    if cursor.fetchone() is None:
        cursor.execute('''
            CREATE TABLE migrations (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        connection.commit()

    cursor.execute("SELECT name FROM migrations")
    applied_migrations = set(row[0] for row in cursor.fetchall())
    connection.close()

    return applied_migrations

def apply_migration(migration_name):
    connection = get_connection()

    applied_migrations = get_applied_migrations()
    if migration_name not in applied_migrations:
        with open(os.path.join("migrations", f"{migration_name}.sql"), "r") as migration_file:
            migration_sql = migration_file.read()

        cursor = connection.cursor()
        cursor.executescript(migration_sql)

        cursor.execute("INSERT INTO migrations (name) VALUES (?)", (migration_name,))
        connection.commit()
        connection.close()


def run_migrate():
    create_tables()
    applied_migrations = get_applied_migrations()

    migrations_dir = "migrations"
    migration_files = [file for file in os.listdir(migrations_dir) if file.endswith(".sql")]
    migration_names = [os.path.splitext(file)[0] for file in migration_files]

    for migration_name in migration_names:
        if migration_name not in applied_migrations:
            apply_migration(migration_name)

    print('Migration executed successfully')