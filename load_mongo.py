import pymongo
import sshtunnel
import json

# Mise en place du tunnel SSH
with sshtunnel.open_tunnel(
    ('20.19.186.59', 22),
    ssh_username='gretag4',
    ssh_password='Greta2023!g4',
    remote_bind_address=('172.17.0.2', 27017)
) as tunnel:
    # Connexion à la base MongoDB à travers le tunnel
    client = pymongo.MongoClient('localhost', tunnel.local_bind_port)
    db = client['MOOC']
    user_collection = db['user']
    forum_collection = db['forum']
    
    # Exemple d'utilisation avec la collection "user"
    # print(user_collection.find_one())
    # for doc in user_collection.find().limit(10):
    #     print(doc)

    # Etape 3 : Compter le nombre de documents dans chaque collection
    print(f"Nombre de documents dans la collection 'user' : {user_collection.count_documents({})}")
    print(f"Nombre de documents dans la collection 'forum' : {forum_collection.count_documents({})}")

    # Etape 4 : Compter le nombre de messages par utilisateur
    pipeline = [
        {"$unwind": "$content"},
        {"$group": {"_id": "$content.username", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]

    result = list(forum_collection.aggregate(pipeline))
    for user in result:
        print(f"{user['_id']} a posté {user['count']} messages")


