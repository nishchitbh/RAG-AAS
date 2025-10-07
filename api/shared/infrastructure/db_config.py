from pymongo import MongoClient
from api.shared.config import SingletonMeta, setting


class Mongo(metaclass=SingletonMeta):
    def __init__(self):
        client = MongoClient(setting.mongodb_connection)
        self.db = client[setting.database_name]

    def get_db(self):
        return self.db


def get_db():
    db_instance = Mongo()
    return db_instance.get_db()
