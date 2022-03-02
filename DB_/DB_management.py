import pymongo
from typing import Dict

class DB_management():
    
    #connecting to MongoDB by setted URL
    def __init__(self, url, DB_name: str):
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]


    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def push_into_DB(self, message: Dict, importance_marker: str) -> None:
        cur_dict = {"message_id": message.get("message_id", 0),
                    "chat_id": message.get("chat", 0).get("id", 0),
                    "user_id": message.get("from", 0).get("id", 0),
                    "first_name": message.get("from", 0).get("first_name", 0), 
                    "user_name": message.get("from", 0).get("user_name", 0),  
                    "date": message.get("date", 0),
                    "importance_marker": message.get("importance_marker", 0), # докнинь, как лучше сделать: это поле передовать через сам метод, или через поле в словаре message 
                    "message_text": message.get("text", 0),
                    "message_type": message.get("message_type", 0),
                    "content_id" :message.get("content_id", 0) # пока что не парсил сам контент, просто посмотри на форму записи, и поправль меня)
                    }
        self.current_project.insert(cur_dict)

    def select_from_DB_search_by(self, filtr: Dict): #filtr = {"count" : int a = 0, "date" : int a = 0, "importance_marker" : "xxx"}
        pass






    