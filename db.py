import pymongo as m
from bson.objectid import ObjectId

client = m.MongoClient()
db = client.lspl_queries
queries = db.queries

def insert_query(title, sql, tags):
    _tags = tags.strip().split(",")
    queries.insert({
            "title": title,
            "sql": sql,
            "tags": _tags
        })

def get_queries():
    _queries = []
    for query in queries.find():
        _queries.append(query)
    return _queries

def get_query_details(id):
    return queries.find_one(ObjectId(id))
