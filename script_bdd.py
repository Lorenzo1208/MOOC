import pymongo
import mysql.connector
import utils
import time

# Connexion à la base MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MOOC"]
forum_collection = db["forum"]

# Extraire les données de la collection "forum" de MongoDB
forum_data = forum_collection.find().batch_size(1000)


# Connexion à la base MySQL
mydb = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="root",
    database="g4"
)

start_time = time.time()  # Début du chronomètre

def traitement(msg, parent_id=None, thread_id=None):
    '''
    Effectue un traitement sur l'obj passé (Message)
    :param msg: Message
    :param limit: int, limite de messages à traiter
    :return:
    '''
    username = msg['username'] if 'username' in msg and msg['username'] is not None else "anonyme"
    dt = msg['created_at']
    dt = dt[:10]+' '+dt[11:19]
    print("Recurse ", msg['id'], msg['depth'] if 'depth' in msg else '-', parent_id, dt)

    # Insertion des utilisateurs
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
            (id, type, created_at, username, depth, body, parent_id, thread_id) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE parent_id=VALUES(parent_id), depth=VALUES(depth), thread_id=VALUES(thread_id);"""

    val = (msg['id'], msg['type'], dt, username, msg['depth'] if 'depth' in msg else None, msg['body'], parent_id, thread_id)
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
