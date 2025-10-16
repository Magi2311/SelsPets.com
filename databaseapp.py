from flask import Flask, render_template, request, jsonify,redirect, url_for, session, flash, Response # type: ignore
from flask_bcrypt import Bcrypt 
import sqlite3
import os
import binascii 
from datetime import date
import joblib
from flask import Flask, request, jsonify, render_template
from flask import Flask, request, jsonify
from openai import OpenAI
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)  # За сигурна сесия
print('=== THIS IS THE REAL DATABASEAPP.PY ===')
#openai.api_key = os.getenv("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")
os.environ["OPENAI_API_KEY"] = ""
# Връзка с базата
def get_db_connection():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# === РЕГИСТРАЦИЯ ===
@app.route("/register", methods=["GET", "POST"])
def register():
    conn = None 

    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirmPassword"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        birth_date=request.form.get("birth_date")
        city = request.form["city"]
        postal_code = request.form["postal_code"]
        profile_picture = request.files.get("profile_picture")
        profile_image_data = profile_picture.read() if profile_picture else None

        if password != confirm:
            flash("Паролите не съвпадат!")
            return redirect(url_for("home"))

        # Само едно хеширане
        salt = binascii.hexlify(os.urandom(16)).decode()
        password_to_hash = password + salt
        password_hash = bcrypt.generate_password_hash(password_to_hash).decode("utf-8")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)", (email, password_hash, salt))
            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO user_profiles (
                    user_id, first_name, last_name, phone, profile_picture, birth_date, city, postal_code, username
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, first_name, last_name, phone, profile_image_data, birth_date, city, postal_code, username))

            conn.commit()

            # Автоматичен вход (или остави за login)
            session["user_id"] = user_id
            return redirect(url_for("seller_home"))

        except sqlite3.IntegrityError:
            flash("Имейлът или потребителското име вече съществуват.")
            return redirect(url_for("home"))
        
        finally:
            if conn:
                conn.close()

    return redirect(url_for("seller_home"))


# === Показване на профилната снимка ===
@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    conn = get_db_connection()
    profile = conn.execute('SELECT profile_picture FROM user_profiles WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    if profile and profile['profile_picture']:
        return Response(profile['profile_picture'], mimetype='image/jpeg')
    else:        
        return redirect(url_for('static', filename='images/images.png'))


# === ВХОД ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form["login"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users 
            WHERE email = ? OR user_id IN (
                SELECT user_id FROM user_profiles WHERE username = ?
            )
        """, (login_input, login_input))
        user = cursor.fetchone()

        if user:
            salt = user["salt"]
            password_to_check = password + salt
           
            if bcrypt.check_password_hash(user["password_hash"], password_to_check):
                session["user_id"] = user["user_id"]
                conn.close()
                return redirect(url_for("seller_home"))
            else:
                flash("Невалидна парола.")
        else:
            flash("Потребителят не е намерен.")
        conn.close()

    return redirect(url_for("seller_home"))

# === ИЗХОД ===
@app.route("/logout")
def logout():
    session.clear()
    flash("Излязохте успешно.")
    return redirect(url_for("home"))
    

# === РЕДАКТИРАНЕ НА ДАННИТЕ ===
@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("home"))

    conn = get_db_connection()

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        username = request.form["username"]
        phone = request.form["phone"]
        city = request.form["city"]
        postal_code = request.form["postal_code"]
        birth_date = request.form["birth_date"]
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        profile_picture = request.files.get("profile_picture")

        # Обновяване на таблицата users
        conn.execute("UPDATE users SET email = ? WHERE user_id = ?", (email, user_id))

        # Обновяване на таблицата user_profiles
        conn.execute("""
            UPDATE user_profiles
            SET first_name = ?, last_name = ?, username = ?, phone = ?, city = ?, postal_code = ?, birth_date = ?
            WHERE user_id = ?
        """, (first_name, last_name, username, phone, city, postal_code, birth_date, user_id))

        # Обновяване на снимка, ако е качена
        if profile_picture:
            image_data = profile_picture.read()
            conn.execute("UPDATE user_profiles SET profile_picture = ? WHERE user_id = ?", (image_data, user_id))

        # Смяна на парола ако е въведена и потвърдена
        if new_password:
            if new_password != confirm_password:
                flash("Паролите не съвпадат!")
                conn.close()
                return redirect("/seller-profile")

            new_salt = binascii.hexlify(os.urandom(16)).decode()
            new_password_to_hash = new_password + new_salt
            hashed_password = bcrypt.generate_password_hash(new_password_to_hash).decode('utf-8')
            conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE user_id = ?", (hashed_password, new_salt, user_id))

        conn.commit()
        conn.close()
        flash("Профилът е обновен успешно.")
        return redirect("/seller-profile")

    # Ако е GET заявка - зареждаме данните за показване във формата
    user = conn.execute("""
        SELECT u.email, up.first_name, up.last_name, up.phone AS phone, up.city, up.postal_code, up.username, up.profile_picture, up.birth_date
        FROM users u
        JOIN user_profiles up ON u.user_id = up.user_id
        WHERE u.user_id = ?
    """, (user_id,)).fetchone()
    conn.close()

    return render_template("Seller_profile.html", user=user,profile=user)


# === ДОБАВЯНЕ НА ЖИВОТНО (само за влезли потребители) ===
@app.route('/add_pet', methods=['POST'])
def add_pet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    type_name = request.form.get('type_name')
    breed_name = request.form.get('breed_name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    vaccinated = request.form.get('vaccinated')
    price = request.form.get('price')
    description = request.form.get('description')
    image = request.files.get('pet_picture')



    if not all([type_name, breed_name, age, gender, vaccinated, price, description, image]):
         flash('Моля, попълнете всички полета.')
         return redirect(url_for("seller_profile"))

    # Четене на снимката като BLOB
    if image is None:
        flash('Моля, качете снимка на домашния любимец.')
        return redirect(url_for("seller_profile"))
    
    pet_picture = image.read()

    conn = get_db_connection()

    # Вземи или създай type_id
    type_row = conn.execute("SELECT type_id FROM animal_types WHERE type_name = ?", (type_name,)).fetchone()
    if type_row:
        type_id = type_row['type_id']
    else:
        conn.execute("INSERT INTO animal_types (type_name) VALUES (?)", (type_name,))
        conn.commit()
        type_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Вземи или създай breed_id
    breed_row = conn.execute("SELECT breed_id FROM breeds WHERE breed_name = ? AND type_id = ?", (breed_name, type_id)).fetchone()
    if breed_row:
        breed_id = breed_row['breed_id']
    else:
        conn.execute("INSERT INTO breeds (breed_name, type_id) VALUES (?, ?)", (breed_name, type_id))
        conn.commit()
        breed_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Вкарай обявата
    conn.execute("""
        INSERT INTO pets (user_id, type_id, breed_id, age, gender, vaccinated, price, description, pet_picture,upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (user_id, type_id, breed_id, age, gender, vaccinated, price, description, pet_picture, date.today()))

    conn.commit()
    conn.close()
    flash("Успешно добавена обява!")
    return redirect(url_for("seller_profile"))

@app.route('/pet_picture/<int:pet_id>')
def pet_picture(pet_id):
    conn = get_db_connection()
    picture = conn.execute("SELECT pet_picture FROM pets WHERE pet_id = ?", (pet_id,)).fetchone()
    conn.close()

    if picture and picture['pet_picture']:
        return Response(picture['pet_picture'], mimetype='image/jpeg')
    else:
        return redirect(url_for('static', filename='images/nophotopet.jpg'))
    

# === РЕДАКТИРАНЕ НА ДАННИТЕ НА ЖИВОТНО ===
@app.route('/pets/update/<int:pet_id>', methods=['POST'])
def update_pet(pet_id):
    data = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Намери type_id и breed_id по име
        cursor.execute("SELECT type_id FROM animal_types WHERE type_name = ?", (data['type_name'],))
        type_row = cursor.fetchone()
        type_id = type_row[0]

        cursor.execute("SELECT breed_id FROM breeds WHERE breed_name = ?", (data['breed_name'],))
        breed_row = cursor.fetchone()
        breed_id = breed_row[0]

        # Обнови запис в таблица pets
        cursor.execute("""
            UPDATE pets
            SET type_id = ?, breed_id = ?, age = ?, price = ?,
                gender = ?, vaccinated = ?, description = ?
            WHERE pet_id = ?
        """, (
            type_id,
            breed_id,
            data['age'],
            data['price'],
            data['gender'],
            data['vaccinated'],
            data['description'],
            pet_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Обявата е редактирана успешно'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ads/delete/<int:pet_id>', methods=['DELETE'])
def delete_ad(pet_id):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM pets WHERE pet_id = ?", (pet_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM pets WHERE pet_id = ?", (pet_id,))
        deleted = cursor.fetchone()
        print("Обява след изтриване:", deleted)

        conn.close()

        return jsonify({'message': 'Обявата е изтрита успешно'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# === ПРЕПОРЪКА ЗА ЖИВОТНО ===
"""
animal_data = [
    {"type": "куче", "breed": "малка порода", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
     "time": 1, "travel_often": 0, "budget": 1, "experience": 2, "social": 1, "furry": 1, "active": 1, "size": 0},
    {"type": "куче", "breed": "голяма порода", "apartment": 2, "children": 1, "allergy": 0, "noise_level": 2,
     "time": 2, "travel_often": 1, "budget": 2, "experience": 2, "social": 1, "furry": 1, "active": 1, "size": 2},
    {"type": "котка", "breed": "късокосместа", "apartment": 1, "children": 0, "allergy": 1, "noise_level": 1,
     "time": 0, "travel_often": 0, "budget": 1, "experience": 1, "social": 0, "furry": 1, "active": 0, "size": 0},
    {"type": "риба", "breed": "златна", "apartment": 0, "children": 1, "allergy": 1, "noise_level": 0,
     "time": 0, "travel_often": 0, "budget": 0, "experience": 0, "social": 0, "furry": 0, "active": 0, "size": 0},
    {"type": "папагал", "breed": "вълнист папагал", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
     "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 1, "furry": 0, "active": 1, "size": 0},
    {"type": "гризач", "breed": "хамстер", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
     "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 1, "furry": 1, "active": 1, "size": 0},
    {"type": "заек", "breed": "дългокосмест", "apartment": 1, "children": 1, "allergy": 0, "noise_level": 1,
     "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 0, "furry": 1, "active": 0, "size": 1},
]
"""
df = pd.read_csv("pet_data.csv")

#df = pd.DataFrame(animal_data)

# Функции и етикети
df.rename(columns={
    'pet': 'type',
    'breed_type': 'breed'
}, inplace=True)

input_columns = ["apartment", "children", "allergy", "noise_level",
                 "time", "travel_often", "budget", "experience",
                 "social", "furry", "active", "size"]

X = df[input_columns]
y = df["type"]
model = RandomForestClassifier()
model.fit(X, y)

# Запази модела
joblib.dump(model, "pet_model.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    try:
        input_keys = ["apartment", "children", "allergy", "noise_level",
                      "time", "travel_often", "budget", "experience",
                      "social", "furry", "active", "size"]
        user_input = {key: data[key] for key in input_keys}

        top_matches = find_top_matches(user_input)

        if top_matches:
            recommendations = []
            for match in top_matches:
                rec = {
                    "type": match["type"],
                    "breed": match["breed"],
                    "details": match
                }
                recommendations.append(rec)

            recommendation_text = "🐾 Препоръчваме ти:\n"
            for i, rec in enumerate(recommendations, 1):
                recommendation_text += f"{i}. {rec['type']} - порода: {rec['breed']}\n"
            return jsonify({"recommendation": recommendation_text})
        else:
            return jsonify({"recommendation": "Не успяхме да намерим подходящо животно."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def find_top_matches(user_input, top_n=3):
    # Тегла за различни критерии
    weights = {
        "allergy": 5,      # алергии с най-голямо тегло
        "time": 4,         # време
        "budget": 4,       # бюджет
        "children": 2,
        "social": 2,
        "active": 2,
        "apartment": 1,
        "experience": 1,
        "travel_often": 1,
        "noise_level": 1,
        "furry": 1,
        "size": 1          # размер с по-малко тегло
    }

    scored_animals = []

    for _, row in df.iterrows():
        match = row.to_dict()
        score = 0
        penalty = 0

        # Алергии - ако потребителят има алергия и животното е козинесто, голямо наказание
        if "allergy" in user_input:
            user_allergy = int(user_input["allergy"])
            pet_furry = int(match.get("furry", 0))

            if user_allergy == 1 and pet_furry == 1:
                penalty += 10  # много тежко наказание
            else:
                score += weights["allergy"]

        # Време - ако времето е малко, не трябва да е много активно животното
        if "time" in user_input:
            user_time = int(user_input["time"])
            pet_active = int(match.get("active", 1))

            if user_time == 0 and pet_active == 2:
                penalty += 5
            else:
                score += weights["time"]

        # Бюджет - ако бюджетът е нисък, животното не трябва да е скъпо за гледане
        if "budget" in user_input:
            user_budget = int(user_input["budget"])
            pet_budget = int(match.get("budget", 1))

            if user_budget < pet_budget:
                penalty += 4
            else:
                score += weights["budget"]

        # Размер - по-слаб критерий, леко наказание ако не съвпада
        if "size" in user_input:
            user_size = int(user_input["size"])
            pet_size = int(match.get("size", 1))

            if user_size != pet_size:
                penalty += 1
            else:
                score += weights["size"]

        # Останалите филтри - обикновени съвпадения с тегла
        for key in user_input:
            if key in ["allergy", "time", "budget", "size"]:
                continue

            try:
                if int(user_input[key]) == int(match[key]):
                    score += weights.get(key, 1)
                else:
                    penalty += 0.5
            except (ValueError, KeyError):
                pass

        final_score = score - penalty

        if final_score > 0:
            scored_animals.append((final_score, match))

    scored_animals.sort(key=lambda x: x[0], reverse=True)
    top_matches = [animal for score, animal in scored_animals[:top_n]]
    return top_matches


""""
features = [
    "apartment", "children", "allergy", "noise_level",
    "time", "travel_often", "budget",
    "experience", "social", "furry", "active", "size"
]

client = OpenAI() 

@app.route('/predict', methods=['POST'])
def get_pet_recommendation():
    user_input = request.json
    prompt_text = f"Потребителски данни: {user_input}. Препоръчай подходящ домашен любимец."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that recommends pets based on user input."},
                {"role": "user", "content": prompt_text}
            ]
        )
        recommendation = response.choices[0].message.content
        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/all-ads')
def all_ads():
    conn = get_db_connection()
    ads = conn.execute('''
        SELECT 
            p.pet_id,
            p.age,
            p.price,
            p.gender,
            p.vaccinated,
            p.description,
            p.upload_date,
            at.type_name,
            b.breed_name,
            u.email,
            up.phone,
            up.city,
            up.profile_picture
        FROM pets p
        JOIN users u ON p.user_id = u.user_id
        JOIN user_profiles up ON u.user_id = up.user_id
        JOIN animal_types at ON p.type_id = at.type_id
        LEFT JOIN breeds b ON p.breed_id = b.breed_id
        ORDER BY p.upload_date DESC
    ''').fetchall()
    conn.close()
    return render_template('all_ads.html', ads=ads)
    """

# === СТРАНИЦИ ===
@app.route("/")
def home():
    return render_template("Home.html")

@app.route("/seller-home")
def seller_home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template("Home_seller.html", pets=pets)

@app.route("/seller")
def seller():
    return render_template("Seller.html")

@app.route("/seller-profile")
def seller_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    conn = get_db_connection()

    user = conn.execute("SELECT email FROM users WHERE user_id = ?", (user_id,)).fetchone()

    profile = conn.execute("""
        SELECT first_name, last_name, username, phone, city, postal_code, birth_date
        FROM user_profiles WHERE user_id = ?
    """, (user_id,)).fetchone()

    ads = conn.execute("""
        SELECT p.pet_id, p.age, p.price, p.gender, p.vaccinated, p.description,
               p.upload_date,
               at.type_name, b.breed_name
        FROM pets p
        JOIN animal_types at ON p.type_id = at.type_id
        LEFT JOIN breeds b ON p.breed_id = b.breed_id
        WHERE p.user_id = ?
        ORDER BY p.upload_date DESC
    """, (user_id,)).fetchall()

    animal_types = conn.execute("SELECT type_name FROM animal_types").fetchall()
    breeds = conn.execute("SELECT breed_name FROM breeds").fetchall()

    conn.close()
    print("ADS COUNT:", len(ads))
    for ad in ads:
        print(dict(ad))

    return render_template("Seller_profile.html",
                           user=user,
                           profile=profile,
                           ads=ads,
                           animal_types=animal_types,
                           breeds=breeds)

@app.route('/get-all-pets')
def get_all_pets():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
                strftime('%d-%m-%Y', p.upload_date) as formatted_date,
                u.email,
                up.phone,
                up.city,
                up.profile_picture
            FROM pets p
            JOIN animal_types at ON p.type_id = at.type_id
            LEFT JOIN breeds b ON p.breed_id = b.breed_id
            JOIN users u ON p.user_id = u.user_id
            JOIN user_profiles up ON u.user_id = up.user_id
            ORDER BY p.upload_date DESC
        """)
        
        pets = [dict(row) for row in cursor.fetchall()]
        return jsonify(pets)
    except Exception as e:
        print(f"Error in get_all_pets: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/pets")
def pets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT pets.*, animal_types.type_name, breeds.breed_name,
                   users.email, user_profiles.phone, user_profiles.city
            FROM pets
            JOIN animal_types ON pets.type_id = animal_types.type_id
            LEFT JOIN breeds ON pets.breed_id = breeds.breed_id
            JOIN users ON pets.user_id = users.user_id
            JOIN user_profiles ON pets.user_id = user_profiles.user_id
        '''

        cursor.execute(query)
        ads = cursor.fetchall()
        ads_list = [dict(row) for row in ads]

        return render_template('Pets.html', ads=ads_list)

    except Exception as e:
        print("ГРЕШКА:", str(e))
        import traceback
        print(traceback.format_exc())
        return render_template('Pets.html', ads=[])
    
@app.route("/seller-pets")
def seller_pets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT pets.*, animal_types.type_name, breeds.breed_name,
                   users.email, user_profiles.phone, user_profiles.city
            FROM pets
            JOIN animal_types ON pets.type_id = animal_types.type_id
            LEFT JOIN breeds ON pets.breed_id = breeds.breed_id
            JOIN users ON pets.user_id = users.user_id
            JOIN user_profiles ON pets.user_id = user_profiles.user_id
        '''

        cursor.execute(query)
        ads = cursor.fetchall()
        ads_list = [dict(row) for row in ads]

        return render_template("Pets_seller.html", ads=ads_list)

    except Exception as e:
        print("ГРЕШКА:", str(e))
        import traceback
        print(traceback.format_exc())
    return render_template("Pets_seller.html", ads=[])

@app.route("/contact")
def contact():
    return render_template("Contacts.html")

@app.route("/seller-contact")
def seller_contact():
    return render_template("Contacts_seller.html")

@app.route('/pet-details/<int:pet_id>')
def pet_details(pet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
            date(p.upload_date) as formatted_date
        FROM pets p
        JOIN animal_types at ON p.type_id = at.type_id
        JOIN breeds b ON p.breed_id = b.breed_id
        WHERE p.pet_id = ?
    """, (pet_id,))
    
    pet = cursor.fetchone()
    if pet:
        pet_dict = dict(pet)
        conn.close()
        return jsonify(pet_dict)
    
    conn.close()
    return jsonify({"error": "Pet not found"}), 404

@app.route('/pet-user-details/<int:pet_id>')
def pet_user_details(pet_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            up.first_name,
            up.last_name,
            up.username,
            up.phone,
            up.city,
            u.email
        FROM pets p
        JOIN users u ON p.user_id = u.user_id
        JOIN user_profiles up ON u.user_id = up.user_id
        WHERE p.pet_id = ?
    """, (pet_id,))
    
    user = cursor.fetchone()
    if user:
        user_dict = dict(user)
        conn.close()
        return jsonify(user_dict)
    
    conn.close()
    return jsonify({"error": "User not found"}), 404

@app.route("/debug/database")
def debug_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        output = []

        # Check pets table
        cursor.execute("SELECT COUNT(*) as count FROM pets")
        pets_count = cursor.fetchone()['count']
        output.append(f"Pets count: {pets_count}")
        
        if pets_count > 0:
            cursor.execute("SELECT * FROM pets")
            pets = cursor.fetchall()
            output.append("\nPets data:")
            for pet in pets:
                output.append(str(dict(pet)))

        # Check animal_types table
        cursor.execute("SELECT COUNT(*) as count FROM animal_types")
        types_count = cursor.fetchone()['count']
        output.append(f"\nAnimal types count: {types_count}")
        
        if types_count > 0:
            cursor.execute("SELECT * FROM animal_types")
            types = cursor.fetchall()
            output.append("\nAnimal types data:")
            for type_ in types:
                output.append(str(dict(type_)))

        # Check users table
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        output.append(f"\nUsers count: {users_count}")
        
        if users_count > 0:
            cursor.execute("SELECT user_id, email FROM users")
            users = cursor.fetchall()
            output.append("\nUsers data:")
            for user in users:
                output.append(str(dict(user)))

        conn.close()
        return "<br>".join(output)

    except Exception as e:
        return f"Error: {str(e)}"

# === СТАРТ ===
if __name__ == "__main__":    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
@app.route("/test")
def test():
    return "Работи!"