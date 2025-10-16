import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def check_pets():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n=== Raw Pets Data ===")
    cursor.execute("SELECT * FROM pets")
    pets = cursor.fetchall()
    for pet in pets:
        print("\n---")
        print(dict(pet))
    
    print("\n=== Raw Users Data ===")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print("\n---")
        print(dict(user))
    
    print("\n=== Raw Animal Types Data ===")
    cursor.execute("SELECT * FROM animal_types")
    types = cursor.fetchall()
    for t in types:
        print(dict(t))
    
    print("\n=== Raw Breeds Data ===")
    cursor.execute("SELECT * FROM breeds")
    breeds = cursor.fetchall()
    for b in breeds:
        print(dict(b))

if __name__ == "__main__":
    check_pets() 