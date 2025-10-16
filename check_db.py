import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# Check pets table
cursor.execute("SELECT COUNT(*) FROM pets")
pets_count = cursor.fetchone()[0]
print(f"Number of pets in database: {pets_count}")

if pets_count > 0:
    # Get sample pet data
    cursor.execute("""
        SELECT 
            p.pet_id,
            p.age,
            p.gender,
            p.vaccinated,
            p.price,
            p.description,
            at.type_name,
            b.breed_name,
            p.upload_date
        FROM pets p
        JOIN animal_types at ON p.type_id = at.type_id
        JOIN breeds b ON p.breed_id = b.breed_id
        LIMIT 1
    """)
    sample_pet = cursor.fetchone()
    if sample_pet:
        print("\nSample pet data:")
        for key in sample_pet.keys():
            print(f"{key}: {sample_pet[key]}")

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\nTables in database:")
for table in tables:
    print(table[0])

conn.close() 