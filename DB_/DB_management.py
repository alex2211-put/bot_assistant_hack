import pymongo
from typing import Dict


class DB_management:

    #connecting to MongoDB by setted URL
    def __init__(self, url, DB_name: str):
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]

    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def push_into_DB(self, message: Dict, importance_marker: str, message_type) -> None:
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
                        "message_type": message_type,
                        "content_id": {"photo": message.get("photo")[0]["file_id"],
                                       "audio": message.get("audio")[0]["file_id"],
                                       "video": message.get("video")[0]["file_id"],
                                       "voice": message.get("voice")[0]["file_id"],
                                       "document": message.get("document")[0]["file_id"],
                                       "location": message.get("location")
                                       }
                        }
            self.current_project.insert_one(cur_dict)
        except:
            raise KeyError(cur_dict)

    def select_from_DB_search_by(self, filtr: Dict):
        #filtr = {"count" : int a = 0, how : int a = {-1, 0, 1} - ищем меньше исходной даты(-1), больше(1) или равне(0); в случае, когда ищем вообще все записи по проекту и дата равна 0,передавать 1 "date" : int a = 0, "importance_marker" : "xxx", "sort" : int a = {-1, 1}}

        if filtr["count"] == 0:
            if filtr["how"] == 0:
                return self.current_project.find({"date": filtr["date"], "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})
            elif filtr["hom"] == 1:
                return self.current_project.find({"date": {'$gt': filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})
            elif filtr["how"] == -1:
                return self.current_project.find({"date": {'$lt': filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})
            
        else:    
            if filtr["how"] == 0:
                return self.current_project.find({"date": filtr["date"], "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])
            elif filtr["hom"] == 1:
                return self.current_project.find({"date": {'$gt': filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])
            elif filtr["how"] == -1:
                return self.current_project.find({"date": {'$lt': filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])

    def select_from_DB_search_by_range(self, filtr: Dict):
        #filtr = {count: int a, "date_start" : int a = 0, "date_finish" = int b != 0, "how" : int a = {-1, 0, 1}, importace_marker: "xxx", "sort": int a = {-1, 1}}
        if filtr["count"] == 0:
           
           return self.current_project.find({"date": {"$gt" : filtr["date_start"], "$lt" : filtr["date_finish"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})

        else:    
            
            return self.current_project.find({"date": {"$gt" : filtr["date_start"], "$lt" : filtr["date_finish"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])
         