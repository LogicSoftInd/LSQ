import pymongo as m
from bson.objectid import ObjectId

import config

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

def insert_database(name, hostname, port, desc):
    databases.insert({
            "name": name,
            "hostname": hostname,
            "port": port,
            "desc": desc
        })

def update_database(id, name, hostname, port, desc):
    databases.update({
        "_id": ObjectId(id)
        },
        { "$set" : {
                "name": name,
                "hostname": hostname,
                "port": port,
                "desc": desc
            }}, upsert=False)

def delete_database(id):
    databases.remove({"_id": ObjectId(id)})

def get_databases():
    return list(databases.find())

def get_database_details(id):
    return databases.find_one(ObjectId(id))
