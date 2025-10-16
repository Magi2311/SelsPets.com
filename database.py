import sqlite3
import re
from datetime import datetime, date

# Свързване с базата
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Таблица за потребители
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL
)
""")

# Таблица с профилите на потребителите
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    profile_picture BLOB,
    birth_date TEXT NOT NULL,
    city TEXT,
    postal_code TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

# Таблица за видове животни
cursor.execute("""
CREATE TABLE IF NOT EXISTS animal_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL
)
""")

# Таблица за породи
cursor.execute("""
CREATE TABLE IF NOT EXISTS breeds (
    breed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL,
    breed_name TEXT NOT NULL,
    FOREIGN KEY(type_id) REFERENCES animal_types(type_id)
)
""")

# Таблица за животни
cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    upload_date TEXT DEFAULT CURRENT_DATE,
    gender TEXT CHECK(gender IN ('мъжки', 'женски')) NOT NULL,
    breed_id INTEGER,
    age TEXT,
    pet_picture BLOB,
    price REAL CHECK(price >= 0),
    description TEXT,
    vaccinated TEXT CHECK(vaccinated IN ('да', 'не')) NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(type_id) REFERENCES animal_types(type_id),
    FOREIGN KEY(breed_id) REFERENCES breeds(breed_id)
)
""")

conn.commit()
print("Таблиците са създадени успешно.")

# === Функции за валидации ===

def is_cyrillic(text):
    return re.match(r'^[\u0400-\u04FF\s]+$', text)

def is_valid_phone(phone):
    return re.match(r'^\+359\d{9}$', phone)

def is_valid_postal_code(code):
    return re.match(r'^\d{4}$', code)

def is_adult(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age >= 18
    except ValueError:
        return False

conn.close()

