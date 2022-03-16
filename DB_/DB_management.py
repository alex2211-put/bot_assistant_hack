import pymongo
from typing import Dict
from typing import List


class DB_management:

    def __init__(self, url, DB_name: str):
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]

    def connect_to_a_project(self, project_name: str) -> None:
        self.current_project = self.current_DB[project_name]

    def __get_id(self, message: Dict) -> List:
        types_of_content= ["vioce", "photo", "video", "audio", "document", "location"]
        for i in types_of_content:
            if message.get(i) is not None:
                content_type = i
                break
        try:
            msg_id = message.get(content_type)["id"]
            return [content_type, msg_id]
        except:
            raise KeyError()
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
                        "importance_marker": importance_marker,
                        "message_text": message["text"],
                        "media_group_id": message.get(["media_group_id"]),
                        "message_type": message_type,
                        "content_type": content_type,
                        "content_id": content_id
                        }
            self.current_project.insert_one(cur_dict)
        except:
            raise KeyError(cur_dict)

    def select_from_DB_search_by(self, count: int = 0, how: str = 'eq', date: int = 0, importance_marker: str = 'green', sort: int = 1) -> Dict:
        '''
        Discribtion param filtr
        :count : int a = 0 by default
        :how = {'$gt', 'eq', '$lt'} -меньше даты(lt), больше(gt) или равна(0), в случае, когда ищем все записи по проекту, передавать 1 
        :date : int a = 0 by default
        :importance_marker : "xxx"
        :sort : int a = {-1, 1}}
        :return : dict
        '''
        if count == 0:
            if how == 'eq':
                return self.current_project.find({"date": date, "importance_marker": importance_marker}).sort({'date': sort})
            else:
                return self.current_project.find({"date": {how: date}, "importance_marker": importance_marker}).sort({'date': sort})

        else:
            if how == 'eq':
                return self.current_project.find({"date": date, "importance_marker": importance_marker}).sort({'date': sort}).limit(count)
            else:
                return self.current_project.find({"date": {how: date}, "importance_marker": importance_marker}).sort({'date': sort}).limit(count)

    def select_from_DB_search_by_range(self, count: int, date_start: int, date_finish: int, importance_marker: str = 'green', sort: int = 1) -> Dict:
        '''
         Discribtion param filtr
        :count : int a = 0 by default
        :date_start: int a
        :date_finish : int b
        :importance_marker : "xxx"
        :sort : int a = {-1, 1}}
        :return : dict
        '''
        if count == 0:

           return self.current_project.find({"date": {"$gt": date_start, "$lt": date_finish}, "importance_marker": importance_marker}).sort({'date': sort})

        else:

            return self.current_project.find({"date": {"$gt": date_start, "$lt": date_finish}, "importance_marker": importance_marker}).sort({'date': sort}).limit(count)
