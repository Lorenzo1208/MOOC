import pymongo
import mysql.connector
import utils
import time

# Connexion à la base MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MOOC"]
forum_collection = db["forum"]
user_collection = db["user"]

# Extraire les données de la collection "forum" de MongoDB
forum_data = forum_collection.find()
user_data = user_collection.find()

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

def get_date(msg):
    dt = msg['created_at']
    return dt[:10] + ' ' + dt[11:19]

def add_course(course_id, opening_dates, msg):
    if course_id not in opening_dates:
        opening_dates[course_id] = msg['created_at']
        mycursor = mydb.cursor()
        sql = "INSERT IGNORE INTO course (id, opening_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id, opening_date=VALUES(opening_date);"
        val = (course_id, opening_dates[course_id])
        mycursor.execute(sql, val)
        mydb.commit()
        # print("Cours ajouté avec id: ", course_id, "et opening_date: ", opening_dates[course_id])

def add_thread(thread_id, title, course_id):
    mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO thread (_id, title, course_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE _id=_id;"
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

        sql = "INSERT IGNORE INTO users (username, user_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE username=VALUES(username), user_id=VALUES(user_id);"
        val = (username, user_id)
        mycursor.execute(sql, val)
        mydb.commit()
        # print("Utilisateur ajouté avec username: ", username, "et user_id: ", user_id)


def add_message(msg, thread_id, username, parent_id, dt):
    mycursor = mydb.cursor()
    sql = """INSERT IGNORE INTO messages 
            (id, created_at, type, depth, body, thread_id, username, parent_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE parent_id=VALUES(parent_id), depth=VALUES(depth), thread_id=VALUES(thread_id);"""

    val = (msg['id'], dt, msg['type'], msg['depth'] if 'depth' in msg else None, msg['body'], thread_id, username, parent_id)

    mycursor.execute(sql, val)
    mydb.commit()

def add_result(username, course_id, grade):
    mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO result (username, course_id, grade) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username), course_id=VALUES(course_id), grade=VALUES(grade);"
    val = (username, course_id, grade)
    mycursor.execute(sql, val)
    mydb.commit()
    # print("Résultat ajouté avec : ", username, "course_id: ", course_id, "grade: ", grade)


def traitement(msg=None, parent_id=None, thread_id=None, title=None, course_id=None,  opening_date=None, grade=None, username=None):
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

    # Insertion des threads
    add_thread(thread_id, title, course_id)

    # Insertion des utilisateurs
    add_user(msg)

    # Insertion des messages
    add_message(msg, thread_id, username, parent_id, dt)

    # Insertion des résultats
    add_result(username, course_id, grade)

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
            # print(f"Grade for {username} {course_id}: {grade}")
            add_result(username, course_id, grade)

elapsed_time = time.time() - start_time  # Fin du chronomètre
print(f"Temps d'exécution : {elapsed_time:.2f} secondes")
