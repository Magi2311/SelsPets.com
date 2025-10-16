
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import joblib
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

ANIMAL_DATABASE = [
    {
        "type": "куче", "breed": "малка порода", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
        "time": 1, "travel_often": 0, "budget": 1, "experience": 2, "social": 1, "furry": 1, "active": 1, "size": 0
    },
    {
        "type": "куче", "breed": "голяма порода", "apartment": 2, "children": 1, "allergy": 0, "noise_level": 2,
        "time": 2, "travel_often": 1, "budget": 2, "experience": 2, "social": 1, "furry": 1, "active": 1, "size": 2
    },
    {
        "type": "котка", "breed": "късокосместа", "apartment": 1, "children": 0, "allergy": 1, "noise_level": 1,
        "time": 0, "travel_often": 0, "budget": 1, "experience": 1, "social": 0, "furry": 1, "active": 0, "size": 0
    },
    {
        "type": "риба", "breed": "златна", "apartment": 0, "children": 1, "allergy": 1, "noise_level": 0,
        "time": 0, "travel_often": 0, "budget": 0, "experience": 0, "social": 0, "furry": 0, "active": 0, "size": 0
    },
    {
        "type": "папагал", "breed": "вълнист папагал", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
        "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 1, "furry": 0, "active": 1, "size": 0
    },
    {
        "type": "гризач", "breed": "хамстер", "apartment": 0, "children": 1, "allergy": 0, "noise_level": 1,
        "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 1, "furry": 1, "active": 1, "size": 0
    },
    {
        "type": "заек", "breed": "дългокосмест", "apartment": 1, "children": 1, "allergy": 0, "noise_level": 1,
        "time": 1, "travel_often": 0, "budget": 1, "experience": 1, "social": 0, "furry": 1, "active": 0, "size": 1
    },
]

features = [
    "apartment", "children", "allergy", "noise_level",
    "time", "travel_often", "budget",
    "experience", "social", "furry", "active", "size"
]
df = pd.DataFrame(ANIMAL_DATABASE)
X = df[features]
y_type = df["type"]
y_breed = df["breed"]

model_type = RandomForestClassifier(n_estimators=100, random_state=42)
model_breed = RandomForestClassifier(n_estimators=100, random_state=42)
model_type.fit(X, y_type)
model_breed.fit(X, y_breed)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Входни данни от анкетата
        data = request.get_json()
        input_data = {key: int(data[key]) for key in features if key in data}
        input_df = pd.DataFrame([input_data])

        # Прогноза от Random Forest
        predicted_type = model_type.predict(input_df)[0]
        predicted_breed = model_breed.predict(input_df)[0]
        ml_recommendation = f"{predicted_type}, порода: {predicted_breed}"

        # Създаване на prompt за GPT
        prompt = (
            f"Потребителски данни: {input_data}.\n"
            f"Машинният модел препоръчва: {ml_recommendation}.\n"
            f"Съгласен ли си с тази препоръка? Ако не – предложи по-добро животно и обясни защо."
        )

        # Запитване към GPT
        gpt_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти си асистент, който препоръчва домашен любимец на база анкетни данни."},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_recommendation = gpt_response.choices[0].message.content

        # Връщане на резултатите
        return jsonify({
            "ml_prediction": ml_recommendation,
            "recommendation": gpt_recommendation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
