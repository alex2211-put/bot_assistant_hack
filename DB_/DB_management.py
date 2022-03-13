import pymongo
from typing import Dict
from typing import List


class DB_management:

    #connecting to MongoDB by setted URL
    def __init__(self, url, DB_name: str):
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]

    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def __get_id(self, message: Dict) -> List:
        l = ["vioce", "photo", "video", "audio", "document", "location"]
        content_type = [i for i in l if message.get(i) is not None]
        if content_type != []:
            content_type = content_type[0]
            try:
                msg_id = message.get(content_type)["id"]
            except:
                raise KeyError()
            return [content_type, msg_id]
        else:
            return [None, None] 


    def push_into_DB(self, message: Dict, importance_marker: str, message_type) -> None:
        
        content_type, content_id = self.__get_id(message)
        try:
            cur_dict = {"message_id": message["message_id"],
                        "chat_id": message["chat"]["id"],
                        "user_id": message["from"]["id"],
                        "first_name": message["from"].get("first_name"),
                        "last_name": message["from"].get("last_name"),
                        "user_name": message["from"]["user_name"],
                        "date": message["date"],
                        "importance_marker":importance_marker,
                        "message_text": message["text"],
                        "media_group_id": message.get(["media_group_id"]),
                        "message_type": message_type,
                        "content_type": content_type,
                        "content_id": content_id
                        }
            self.current_project.insert_one(cur_dict)
        except:
            raise KeyError(cur_dict)

    def select_from_DB_search_by(self, filtr: Dict):
        '''
        Discribtion param filtr
        :count : int a = 0 by default
        :how : int a = {'$gt', 0, '$lt'} - ищем меньше исходной даты(-1), больше(1) или равне(0), в случае, когда ищем вообще все записи по проекту и дата равна 0,передавать 1 
        :date : int a = 0 by default
        :importance_marker : "xxx"
        :sort : int a = {-1, 1}}
        :return : dict
        '''
        if filtr["count"] == 0:
            if filtr["how"] == 0:
                return self.current_project.find({"date": filtr["date"], "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})
            else:
                return self.current_project.find({"date": {filtr["how"]: filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})

        else:    
            if filtr["how"] == 0:
                return self.current_project.find({"date": filtr["date"], "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])
            else:
                return self.current_project.find({"date": {filtr["how"]: filtr["date"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])

    def select_from_DB_search_by_range(self, filtr: Dict):
        '''
         Discribtion param filtr
        :count : int a = 0 by default
        :date_start: int a
        :date_finish : int b
        :importance_marker : "xxx"
        :sort : int a = {-1, 1}}
        :return : dict
        '''
        if filtr["count"] == 0:
           
           return self.current_project.find({"date": {"$gt" : filtr["date_start"], "$lt" : filtr["date_finish"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]})

        else:    
            
            return self.current_project.find({"date": {"$gt" : filtr["date_start"], "$lt" : filtr["date_finish"]}, "importance_marker": filtr["importance_marker"]}).sotr({'date': filtr["sort"]}).limit(filtr["count"])
         