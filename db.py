import pymongo as m
from bson.objectid import ObjectId

import config
from aes import AESCipher

client = m.MongoClient(config.mongo_hostname, config.mongo_port)
db = client[config.mongo_db]
queries = db[config.query_mongo_collection]
databases = db[config.database_mongo_collection]

def get_tags_list(tags):
    return [ tag.strip() for tag in tags.strip().split(",") \
            if len(tag.strip()) > 0]

def insert_query(title, sql, tags, desc, who):
    _tags = get_tags_list(tags)
    queries.insert({
            "title": title,
            "sql": sql,
            "tags": _tags,
            "desc": desc,
            "who": who
        })

def update_query(id, title, sql, tags, desc, who):
    _tags = get_tags_list(tags)
    queries.update({
        "_id": ObjectId(id)
        },
        { "$set" : {
            "title": title,
            "sql": sql,
            "tags": _tags, 
            "desc": desc,
            "who": who
            }}, upsert=False)

def delete_query(id):
    queries.remove({"_id": ObjectId(id)})

def get_queries():
    return list(queries.find())

def get_query_details(id):
    return queries.find_one(ObjectId(id))

def insert_database(name, hostname, port=None, user=None, password=None, desc=None):
    if password:
        crypt = AESCipher(config.flask_secret_key)
        encrypted_password = crypt.encrypt(password)
    else:
        encrypted_password = None

    databases.insert({
            "name": name,
            "hostname": hostname,
            "port": port,
            "user": user, 
            "password": encrypted_password,
            "desc": desc
        })

def update_database(id, name, hostname, port=None, user=None, password=None, desc=None):

    db_set = {
        "name": name,
        "hostname": hostname,
        "port": port,
        "user": user, 
        "desc": desc
    }

    if password:
        crypt = AESCipher(config.flask_secret_key)
        encrypted_password = crypt.encrypt(password)
        db_set["password"] = encrypted_password
    else:
        encrypted_password = None

    databases.update({
        "_id": ObjectId(id)
        },
        { "$set" : db_set}, upsert=False)

def delete_database(id):
    databases.remove({"_id": ObjectId(id)})

def get_databases():
    return list(databases.find())

def get_database_details(id):
    return databases.find_one(ObjectId(id))
