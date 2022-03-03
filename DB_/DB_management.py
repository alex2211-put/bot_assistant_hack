import pymongo
from typing import Dict

class DB_management:
    
    #connecting to MongoDB by setted URL
    def __init__(self, url, DB_name: str):
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]


    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def push_into_DB(self, message: Dict, importance_marker: str) -> None:
        try:
            cur_dict = {"message_id": message["message_id"],
                        "chat_id": message["chat"]["id"],
                        "user_id": message["from"]["id"],
                        "first_name": message["from"]["first_name"],
                        "user_name": message["from"]["user_name"],
                        "date": message["date"],
                        # докнинь, как лучше сделать: это поле передовать через сам метод, или через поле в словаре message
                        "importance_marker": message.get("importance_marker", "green"),
                        "message_text": message["text"],
                        "media_group_id": message.get(["media_group_id"]),
                        "message_type": message.get("message_type"),
                        "content_id": {"photo": [i_d["file_id"] for i_d in message.get("photo")],
                                       "audio": [i_d["file_id"] for i_d in message.get("audio")],
                                       "video": [i_d["file_id"] for i_d in message.get("video")],
                                       "voice": [i_d["file_id"] for i_d in message.get("voice")],
                                       "document": [i_d["file_id"] for i_d in message.get("document")],
                                       "location": message.get("location")
                                       }
                        }
            self.current_project.insert_one(cur_dict)
        except:
            raise KeyError(cur_dict)

    def select_from_DB_search_by(self, filtr: Dict): 
    #filtr = {"count" : int a = None, how : int a = {-1, 0, 1} - ищем меньше исходной даты(-1), больше(1) или равне(0); в случае, когда ищем вообще все записи по проекту и дата равна 0,передавать 1 "date" : int a = 0, "importance_marker" : "xxx", "sort" : int a = {-1, 1}}
        
        if filtr["how"] == 0:
            return self.current_project.find({"date": filtr["date"], "importance_marker": filtr["importance_marker"] }).sotr({$natural: filtr["sort"]}).limit(filtr["limit"])
        elif filtr["hom"] == 1:
            return self.current_project.find({"date":{$gt: filtr["date"]}, "importance_marker": filtr["importance_marker"] }).sotr({$natural: filtr["sort"]}).limit(filtr["limit"])
        elif filtr["how"] == -1:
            return self.current_project.find({"date":{$lt: filtr["date"]}, "importance_marker": filtr["importance_marker"] }).sotr({$natural: filtr["sort"]}).limit(filtr["limit"])
    
    def select_from_DB_search_by_range(self, filtr: Dict):
        pass



    