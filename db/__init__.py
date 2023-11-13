import sqlite3
from config.settings import DB_FILE_PATH

def get_connection():
 	return sqlite3.connect(DB_FILE_PATH)