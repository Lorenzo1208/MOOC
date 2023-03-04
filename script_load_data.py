import pymongo
import mysql.connector
import utils
import time
import csv
from datetime import datetime

# Connexion à la base MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MOOC"]
forum_collection = db["forum"]
user_collection = db["user"]

# Extraire les données de la collection "forum" de MongoDB
forum_data = forum_collection.find()
user_data = user_collection.find(batch_size=1000)

# Connexion à la base MySQL
mydb = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="g4"
)

start_time = time.time()  # Début du chronomètre

opening_dates = {}

def get_username(msg):
    if 'username' in msg and msg['username'] is not None:
        return msg['username']
    else:
        return "anonyme"

def get_title(msg):
    if 'title' in msg and msg['title'] is not None:
        return msg['title']
    else:
        return "Pas de titre"

def get_course_id(msg):
    if 'course_id' in msg and msg['course_id'] is not None:
        return msg['course_id']
    else:
        return "Pas d'id de cours"

# def get_date(msg):
#     dt = msg['created_at']
#     return dt[:10] + ' ' + dt[11:19]

def get_date(msg):
    dt_str = msg['created_at']
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')
    return dt

def add_course(course_id, opening_dates, msg):
    if course_id not in opening_dates:
        opening_dates[course_id] = get_date(msg)
        mycursor = mydb.cursor()
        sql = "INSERT INTO course (id, opening_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id, opening_date=VALUES(opening_date);"
        val = (course_id, opening_dates[course_id])
        mycursor.execute(sql, val)
        mydb.commit()
        # print("Cours ajouté avec id: ", course_id, "et opening_date: ", opening_dates[course_id])

def add_thread(thread_id, title, course_id):
    mycursor = mydb.cursor()
    sql = "INSERT INTO thread (_id, title, course_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE _id=_id;"
    val = (thread_id, title, course_id)
    mycursor.execute(sql, val)
    mydb.commit()
    # print("Thread ajouté avec titre: ", title, "et course_id: ", course_id)

def add_user(msg):
    if not msg['anonymous']:
        mycursor = mydb.cursor()
        username = get_username(msg)
        user_id = msg.get('user_id')
        if user_id is None:
            return  # ou lever une exception, selon le comportement souhaité

        sql = "INSERT INTO users (username, user_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE username=VALUES(username), user_id=VALUES(user_id);"
        val = (username, user_id)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Utilisateur ajouté avec username: ", username, "et user_id: ", user_id)
        
        
# def fill_users_table():
#     for user in user_collection.find(batch_size=1000):
#         username = user.get('username')
#         if username is not None:
#             mycursor = mydb.cursor()
#             sql = "INSERT INTO users (username) VALUES (%s) ON DUPLICATE KEY UPDATE username=VALUES(username);"
#             val = (username,)
#             mycursor.execute(sql, val)
#             mydb.commit()
#             mycursor.execute("SELECT * FROM users")
#             result = mycursor.fetchall()
            

# fill_users_table()

def add_message(msg, thread_id, username, parent_id, dt):
    mycursor = mydb.cursor()
    sql = """INSERT INTO messages 
            (id, created_at, type, depth, body, thread_id, username, parent_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE parent_id=VALUES(parent_id), depth=VALUES(depth), thread_id=VALUES(thread_id);"""

    val = (msg['id'], dt, msg['type'], msg['depth'] if 'depth' in msg else None, msg['body'], thread_id, username, parent_id)

    mycursor.execute(sql, val)
    mydb.commit()

def add_result(username, course_id, grade, city, country):
    mycursor = mydb.cursor()

    # Check if the course_id exists in the course table
    mycursor.execute("SELECT id FROM course WHERE id = %s", (course_id,))
    result = mycursor.fetchone()
    if result is None:
        print(f"Course {course_id} does not exist in the course table")
        return

    # Insert the result
    sql = "INSERT INTO result (username, course_id, grade, city, country) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username), course_id=VALUES(course_id), grade=VALUES(grade), city=VALUES(city), country=VALUES(country);"
    val = (username, course_id, grade, city, country)
    try:
        mycursor.execute(sql, val)
        mydb.commit()
    except mysql.connector.Error as err:
        print("Une erreur s'est produite: {}".format(err))
        print("Le nom d'utilisateur est : {}".format(username))

    # print("Résultat ajouté avec : ", username, "course_id: ", course_id, "grade: ", grade)


def traitement(msg=None, parent_id=None, thread_id=None, title=None, course_id=None,  opening_date=None, grade=None, username=None, city=None, country=None):
    '''
    Effectue un traitement sur l'obj passé (Message)
    :param msg: Message
    :param limit: int, limite de messages à traiter
    :return:
    '''
    
    if thread_id is None:
        return
    
    # Récupération des données
    username = get_username(msg)
    title = get_title(msg)
    course_id = get_course_id(msg)
    dt = get_date(msg)
    # print("Recurse ", msg['id'], msg['depth'] if 'depth' in msg else '-', parent_id, dt)

    # Insertion dans la table course- si elle n'existe pas déjà
    add_course(course_id, opening_dates, msg)

    # Insertion des utilisateurs
    add_user(msg)
    # fill_users_table()
    

    # Insertion des threads
    add_thread(thread_id, title, course_id)

    # Insertion des messages
    add_message(msg, thread_id, username, parent_id, dt)

    # Insertion des résultats
    add_result(username, course_id, grade, city, country)

    # Récursivement, parcourir les enfants du message
    if 'children' in msg:
        for child in msg['children']:
            traitement(child, msg['id'])

# for msg in forum_data:
#     utils.recur_message(msg['content'], traitement, thread_id=msg['_id'])

for course in user_data:
    for key, value in course.items():
        if isinstance(value, dict) and 'grade' in value:
            grade = value['grade']
            username = course['username']
            course_id = key
            country = value.get('country')
            city = value.get('city')
            # print(f"Grade for {username} {course_id}: {grade}")
            add_result(username, course_id, grade, city, country)



def export_table_to_csv(table_name):
    # Récupération des données
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM {table_name}")
    rows = mycursor.fetchall()

    # Exportation des données en CSV
    with open(f'{table_name}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([i[0] for i in mycursor.description])
        for row in rows:
            writer.writerow(row)

# export_table_to_csv('thread')

elapsed_time = time.time() - start_time  # Fin du chronomètre
print(f"Temps d'exécution : {elapsed_time:.2f} secondes")
