from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_NAME = "school.db"

DB_FILE_PATH = BASE_DIR / "db" / DB_NAME