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
def graph1():
    
    cursor = mydb.cursor()
    cursor.execute("""SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS count
        FROM messages
        GROUP BY month
        ORDER BY month ASC;
        """)
    rows = cursor.fetchall()
    dates = [str(row[0]) for row in rows]
    counts = [row[1] for row in rows]
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("""SELECT users.username, COUNT(*) as count FROM messages JOIN users ON messages.username = users.username
    GROUP BY users.username ORDER BY count DESC LIMIT 20""")
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    cursor.close()
    
    cursor = mydb.cursor()
    cursor.execute("""SELECT 
        COUNT(CASE WHEN users.gender = 'M' THEN 1 END) AS nb_hommes2,
        COUNT(CASE WHEN users.gender = 'F' THEN 1 END) AS nb_femmes2,
        COUNT(CASE WHEN users.gender = 'O' THEN 1 END) AS nb_autre
        FROM 
        users""")
    rows = cursor.fetchall()
    nb_hommes = rows[0][0]
    nb_femmes = rows[0][1]
    nb_autre = rows[0][2]
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("""SELECT 
        users.gender,
        COUNT(*) as total,
        COUNT(CASE WHEN result.Certificate_Eligible  = 'Y' THEN 1 END) AS nb_reussites,
        COUNT(CASE WHEN result.Certificate_Eligible = 'N' THEN 1 END) AS nb_echecs,
        100 * COUNT(CASE WHEN result.Certificate_Eligible = 'Y' THEN 1 END) / COUNT(*) AS proportion_reussite
        FROM users JOIN result ON
        users.username = result.username
        WHERE users.gender != 'None' AND users.gender != ''
        GROUP BY users.gender
        ORDER BY proportion_reussite DESC;""")
    rows = cursor.fetchall()
    genre1 = [row[0] for row in rows]
    pourcent_reussite1 = [row[4] for row in rows]
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("""SELECT users.country, COUNT(*) as total FROM users JOIN result ON users.username = result.username
    WHERE users.country IS NOT NULL AND users.country != ''  GROUP BY users.country ORDER BY total DESC LIMIT 15""")
    rows = cursor.fetchall()
    country = [row[0] for row in rows]
    count_country = [row[1] for row in rows]
    cursor.close()
    
    cursor = mydb.cursor()
    cursor.execute("""SELECT 
    users.country,
    COUNT(*) as total,
    COUNT(CASE WHEN result.Certificate_Eligible = 'Y' THEN 1 END) AS nb_reussites,
    COUNT(CASE WHEN result.Certificate_Eligible = 'N' THEN 1 END) AS nb_echecs,
    100 * COUNT(CASE WHEN result.Certificate_Eligible = 'Y' THEN 1 END) / COUNT(*) AS proportion_reussite
    FROM 
        users
    JOIN
        result
    ON
        users.username = result.username
    WHERE users.country IS NOT NULL AND users.country != ''
    GROUP BY
        users.country
    HAVING 
    total >= 5
    ORDER BY
        proportion_reussite DESC
    LIMIT 15;
    """)
    rows = cursor.fetchall()
    country2 = [row[0] for row in rows]
    pourcentage_reussite = [row[4] for row in rows]
    cursor.close()
    
    cursor = mydb.cursor()
    cursor.execute("""SELECT users.level_of_education, COUNT(*) as total FROM users JOIN result ON users.username = result.username
    WHERE users.level_of_education IS NOT NULL AND users.level_of_education != '' AND users.level_of_education != 'None'
    GROUP BY users.level_of_education ORDER BY total DESC;""")
    rows = cursor.fetchall()
    level_of_education = [row[0] for row in rows]
    count_level = [row[1] for row in rows]
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("""SELECT 
    users.level_of_education ,
    COUNT(*) as total,
    COUNT(CASE WHEN result.Certificate_Eligible = 'Y' THEN 1 END) AS nb_reussites,
    COUNT(CASE WHEN result.Certificate_Eligible = 'N' THEN 1 END) AS nb_echecs,
    100 * COUNT(CASE WHEN result.Certificate_Eligible = 'Y' THEN 1 END) / COUNT(*) AS proportion_reussite
    FROM users
    JOIN result
    ON users.username = result.username
    WHERE users.level_of_education IS NOT NULL AND users.level_of_education != ''
    GROUP BY users.level_of_education
    ORDER BY proportion_reussite DESC;""")
    rows = cursor.fetchall()
    level_of_education1 = [row[0] for row in rows]
    pourcent_reussite2 = [row[4] for row in rows]
    cursor.close()

    data0 = {
        "labels": dates,
        "datasets": [{
            "label": '# of Messages',
            "data": counts,
            "backgroundColor": 'rgba(255, 99, 132, 0.2)',
            "borderColor": 'rgba(255, 99, 132, 1)',
            "borderWidth": 1
        }]
    }
    options0 = {
        "scales": {
            "xAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }

    
    data1 = {
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
    options1 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
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



    data2 = {
        "labels": ['Hommes', 'Femmes', 'Autre'],
        "datasets": [
            {
                "label": "Proportion hommes-femmes",
                "data": [nb_hommes, nb_femmes, nb_autre],
                "backgroundColor": [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 205, 86, 0.2)'   # Nouvelle couleur
                ],
                "borderColor": [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 205, 86, 1)'     # Nouvelle couleur
                ],
                "borderWidth": 1
            }
        ]
    }

    options2 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Proportion hommes-femmes"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }


    data21 = {
        "labels": genre1,
        "datasets": [
            {
                "label": "Pourcentage de réussite",
                "data": pourcent_reussite1,
                "backgroundColor": [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 205, 86, 0.2)'   # Nouvelle couleur
                ],
                "borderColor": [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 205, 86, 1)'     # Nouvelle couleur
                ],
                "borderWidth": 1
            }
        ]
    }

    options21 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Genre ayant le meilleur taux de réussite"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }


    data3 = {
        "labels": country,
        "datasets": [
            {
                "label": "Nombre d'utilisateurs",
                "data": count_country,
                "backgroundColor": [
                                       f'rgba({r},{g},{b},0.2)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                              (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                              (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                              (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                              (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                                   ][:len(country)],
                "borderColor": [
                                   f'rgba({r},{g},{b},1)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                        (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                        (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                        (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                        (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                               ][:len(country)],
                "borderWidth": 1
            }
        ]
    }

    options3 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Pays avec le plus grand nombre de ressortissants"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }


    data4 = {
        "labels": country2,
        "datasets": [
            {
                "label": "Pourcentage de réussite",
                "data": pourcentage_reussite,
                "backgroundColor": [
                                       f'rgba({r},{g},{b},0.2)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                              (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                              (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                              (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                              (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                                   ][:len(country)],
                "borderColor": [
                                   f'rgba({r},{g},{b},1)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                        (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                        (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                        (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                        (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                               ][:len(country)],
                "borderWidth": 1
            }
        ]
    }

    options4 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Pays avec le meilleur taux de réussite"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }
    

    data6 = {
        "labels": level_of_education,
        "datasets": [
            {
                "label": "Nombre d'utilisateurs",
                "data": count_level,
                "backgroundColor": [
                                       f'rgba({r},{g},{b},0.2)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                              (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                              (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                              (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                              (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                                   ][:len(level_of_education)],
                "borderColor": [
                                   f'rgba({r},{g},{b},1)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                        (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                        (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                        (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                        (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                               ][:len(level_of_education)],
                "borderWidth": 1
            }
        ]
    }

    options6 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Nombre d'utilisateurs par niveau d'études"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }


    data7 = {
        "labels": level_of_education1,
        "datasets": [
            {
                "label": "Pourcentage de réussite",
                "data": pourcent_reussite2,
                "backgroundColor": [
                                       f'rgba({r},{g},{b},0.2)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                              (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                              (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                              (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                              (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                                   ][:len(level_of_education1)],
                "borderColor": [
                                   f'rgba({r},{g},{b},1)' for r,g,b in [(255, 99, 132), (54, 162, 235), (255, 206, 86),
                                                                        (75, 192, 192), (153, 102, 255), (255, 159, 64),
                                                                        (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                                        (255, 255, 0), (0, 255, 255), (255, 0, 255),
                                                                        (128, 0, 0), (0, 128, 0), (0, 0, 128)]
                               ][:len(level_of_education1)],
                "borderWidth": 1
            }
        ]
    }

    options7 = {
        "animation": {
            "duration": 2000,
            "easing": "easeInOutExpo"
        },
        "title": {
            "display": True,
            "text": "Taux de réussite par niveau d'études"
        },
        "scales": {
            "yAxes": [{
                "ticks": {
                    "beginAtZero": True
                }
            }]
        }
    }



    data = {'graph0': {'data': data0, 'options': options0},
            'graph1': {'data': data1, 'options': options1},
            'graph2': {'data': data2, 'options': options2},
            'graph21': {'data': data21, 'options': options21},
            'graph3': {'data': data3, 'options': options3},
            'graph4': {'data': data4, 'options': options4},
            'graph6': {'data': data6, 'options': options6},
            'graph7': {'data': data7, 'options': options7}}


    # Pass the data and options to the template
    return render_template("analyse.html", data=data, chart0_id="myChart0", chart1_id="myChart1", chart2_id="myChart2", chart21_id="myChart21", chart3_id="myChart3", chart4_id="myChart4",chart6_id="myChart6", chart7_id="myChart7")




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
     app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, use_reloader=True)
