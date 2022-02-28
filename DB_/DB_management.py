import pymongo
from pymongo import MongoCient as MC
from typing import Dict

class DB_management():
    
    #connecting to MongoDB by setted URL
    def __init__(self, url):
        self.client = MC(url)
    
    def connect_to_DB(self, DB_name: str) -> None:
        self.current_DB = self.client[DB_name]

    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def write_a_message(self, message: Dict, importance_marker: str) -> None:
        cur_dict = {"message_id" : message["message_id"],
                    "chat_id" : message["chat"]["id"],
                    "user_id" : message["from"]["id"],
                    "first_name" : message["from"]["first_name"], 
                    "user_name" : message["from"]["user_name"],  
                    "date" : message["date"],
                    "importance_marker" : message["importance_marker"], # докнинь, как лучше сделать: это поле передовать через сам метод, или через поле в словаре message 
                    "message_text" : message["text"],
                    "message_type" : message["message_type"],
                    "content_id" :message["content_id"]
                    }
        self.current_project.insert(cur_dict)

    def select_from_DB_search_by(self, filtr):
        pass






    