import plotly.graph_objs as go
from plotly.offline import plot
from flask import Flask, render_template, request, jsonify

import mysql.connector

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

@app.route("/prediction")
def prediction():
    return render_template("prediction.html")

if __name__ == '__main__':
    app.run(debug=True)
