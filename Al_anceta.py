
from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib

app = Flask(__name__)
model = joblib.load('pet_recommendation_model.pkl')  # Веднъж зареждаме модела

@app.route('/')
def index():
    return render_template('Al_anceta.html')

@app.route('/recommend_pet', methods=['POST'])
def recommend_pet():
    try:
        data = request.form  # взимаме данните от формата, не от JSON
        features = ['children', 'yard', 'travel_often', 'social', 'budget',
            'apartment', 'allergy', 'time', 'active', 'furry']
        input_df = pd.DataFrame([{k: int(data[k]) for k in features}])
        prediction = model.predict(input_df)[0]
        return render_template('Al_anceta.html', result=prediction)  # препращаме към шаблона с резултат
    except Exception as e:
        return render_template('Al_anceta.html', result='Грешка: ' + str(e))

if __name__ == '__main__':
    app.run(debug=True)

