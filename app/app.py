from pycaret.classification import *
from flask import Flask, render_template, request, jsonify
import joblib
import pickle
import numpy as np
import mysql.connector
import pandas as pd

model = joblib.load('ada_model.pkl')

mydb = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="g4"
)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/analyse")
def graph():
    cursor = mydb.cursor()
    cursor.execute("SELECT users.username, COUNT(*) as count FROM messages JOIN users ON messages.username = users.username GROUP BY users.username ORDER BY count DESC LIMIT 20")
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    # Prepare the data for Chart.js
    data = {
        "labels": usernames,
        "datasets": [
            {
                "label": "Nombre de messages",
                "data": counts,
                "backgroundColor": [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                "borderColor": [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                "borderWidth": 1
            }
        ]
    }
    options = {
        "title": {
            "display": True,
            "text": "Utilisateurs les plus actifs"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }

    # Pass the data and options to the template
    return render_template("analyse.html", data=data, options=options)

from pycaret.utils import check_metric
from pycaret.classification import predict_model

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        ville = request.form['ville']
        pays = request.form['pays']
        genre = request.form['genre']
        date_naissance = request.form['date_naissance']
        niveau_education = request.form['niveau_education']
        messages = request.form['messages']
        course_id = request.form['course_id']
        
        # Create a dataframe with the input features
        input_df = pd.DataFrame({
            'city': [ville] if ville else [''],
            'country': [pays] if pays else [''],
            'gender': [genre],
            'year_of_birth': [date_naissance] if date_naissance else [''],
            'level_of_education': [niveau_education],
            'body': [messages] if messages else [''],
            'course_id': [course_id] if course_id else [''],
            'subjectivity': 0.45,
            'polarity': -0.225
        })
        

        # Make a prediction using the preprocessed input features
        prediction = predict_model(model, data=input_df)
        prediction = prediction['Label'][0]
        
        # modify the prediction value based on the condition
        if prediction == 'Y':
            prediction = '''Continue comme ça ! La prédiction indique que tu as de grandes chances d'obtenir ton diplôme.'''
        elif prediction == 'N':
            prediction = '''Désolé, la prédiction indique que vous n'obtiendrez pas votre diplôme.'''
        
        # Render the prediction result
        return render_template('prediction.html', prediction=prediction)

    # Render the form
    return render_template('prediction.html')

if __name__ == '__main__':
    app.run(debug=True)
