import pymongo
import mysql.connector
import utils
import time

# Connexion à la base MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MOOC"]
forum_collection = db["forum"]

# Extraire les données de la collection "forum" de MongoDB
forum_data = forum_collection.find()

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

def traitement(msg, parent_id=None, thread_id=None, title=None, course_id=None,  opening_date=None):
    '''
    Effectue un traitement sur l'obj passé (Message)
    :param msg: Message
    :param limit: int, limite de messages à traiter
    :return:
    '''
    
    if thread_id is None:
        return
    
    username = msg['username'] if 'username' in msg and msg['username'] is not None else "anonyme"
    title = msg['title'] if 'title' in msg and msg['title'] is not None else "Pas de titre"
    course_id = msg['course_id'] if 'course_id' in msg and msg['course_id'] is not None else "Pas d'id de cours"


    dt = msg['created_at']
    dt = dt[:10]+' '+dt[11:19]
    print("Recurse ", msg['id'], msg['depth'] if 'depth' in msg else '-', parent_id, dt)

    if course_id not in opening_dates:
        opening_dates[course_id] = msg['created_at']  # stocke la première date de création de chaque cours


    # Insertion dans la table course si elle n'existe pas déjà
    mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO course (id, opening_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id, opening_date=VALUES(opening_date);"
    val = (course_id, opening_dates[course_id])
    mycursor.execute(sql, val)
    mydb.commit()
    print("Cours ajouté avec id: ", course_id, "et opening_date: ", opening_dates[course_id])

    # Insertion des threads
    mycursor = mydb.cursor()
    sql = "INSERT INTO thread (_id, title, course_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE _id=_id;"
    val = (thread_id, title, course_id)
    mycursor.execute(sql, val)
    mydb.commit()
    print("Thread ajouté avec titre: ", title, "et course_id: ", course_id)

# Insertion des utilisateurs
    if not msg['anonymous']:
        mycursor = mydb.cursor()
        sql = "INSERT IGNORE INTO users (username, user_id) VALUES (%s,%s) ;"
        username = msg.get('username', 'anonyme')  # Si la clé 'username' n'existe pas, la valeur par défaut est 'anonyme'
        user_id = msg.get('user_id')
        val = (username, user_id)
        mycursor.execute(sql, val)
        mydb.commit()

    # Insertion des messages
    mycursor = mydb.cursor()
    sql = """INSERT IGNORE INTO messages 
            (id, created_at,type, depth, body, thread_id, username,parent_id) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE parent_id=VALUES(parent_id), depth=VALUES(depth), thread_id=VALUES(thread_id);"""

    val = (msg['id'], dt, msg['type'], msg['depth'] if 'depth' in msg else None, msg['body'], thread_id, username, parent_id)

    mycursor.execute(sql, val)
    mydb.commit()

    # Récursivement, parcourir les enfants du message
    if 'children' in msg:
        for child in msg['children']:
            traitement(child, msg['id'])


for msg in forum_data:
    utils.recur_message(msg['content'], traitement, thread_id=msg['_id'])


elapsed_time = time.time() - start_time  # Fin du chronomètre
print(f"Temps d'exécution : {elapsed_time:.2f} secondes")
