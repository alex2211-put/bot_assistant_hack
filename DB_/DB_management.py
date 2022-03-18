import pymongo
from typing import Dict
from typing import List
import get_url
#1 - url из конфига
#2 - выборка по имени проекта
#3 - перегрузить класс для lt, gt
#4 - сделать запись архивной




class DB_management:

    def __init__(self, DB_name: str):
        url = get_url.get_url()
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client[DB_name]

    def connect_to_a_project(self, project_name: str):
        self.current_project = self.current_DB[project_name]

    def _get_id(self, message: Dict) -> List:
        types_of_content = ["voice", "photo",
                            "video", "audio", "document", "location"]
        for i in types_of_content:
            if message.get(i):
                content_type = i
                break
        content_id = message.get(content_type)["id"]
        return [content_type, content_id]

    def insert_into_DB(self,
                     message: Dict,
                     importance_marker: str,
                     message_type,
                     ):

        content_type, content_id = self._get_id(message)

        cur_dict = {"message_id": message["message_id"],
                    "chat_id": message["chat"]["id"],
                    "user_id": message["from"]["id"],
                    "first_name": message["from"].get("first_name"),
                    "last_name": message["from"].get("last_name"),
                    "user_name": message["from"].get("user_name"),
                    "date": message["date"],
                    "importance_marker": importance_marker,
                    "message_text": message["text"],
                    "media_group_id": message.get(["media_group_id"]),
                    "message_type": message_type,
                    "content_type": content_type,
                    "content_id": content_id,
                    "archived": False
                    }
        self.current_project.insert_one(cur_dict)

    def select_from_DB_search_by(self,
                             count: int = 100,
                             how: str = 'eq',
                             date: int = 0,
                             importance_marker: str = 'green',
                             sort: int = 1,
                             need_arh_doc: bool = False,
                             ) -> Dict:
        '''
        Discribtion param filtr
        :how = {'$gt', 'eq', '$lt'} -меньше даты(lt), больше(gt) или равна(0)
        :sort : int a = {-1, 1}}
        '''
        if count == 0:
            if how == 'eq':
                self.curr_select = self.current_project.find(
                {"date": date,
                "importance_marker": importance_marker,
                "archived": need_arh_doc}).sort({'date': sort})
            else:
                self.curr_select = self.current_project.find(
                {"date": {how: date},
                "importance_marker": importance_marker,
                "archived": need_arh_doc}).sort({'date': sort})

        else:
            if how == 'eq':
                self.curr_select = self.current_project.find(
                {"date": date,
                "importance_marker": importance_marker,
                "archived": need_arh_doc}
                ).sort({'date': sort}).limit(count)
            else:
                self.curr_select = self.current_project.find(
                {"date": {how: date},
                "importance_marker": importance_marker,
                "archived": need_arh_doc}
                ).sort({'date': sort}).limit(count)
        return self.curr_select
        

    def select_from_DB_search_by_range(self,
                                       count: int = 100,
                                       date_start: int = 0,
                                       date_finish: int = 2000000000,
                                       importance_marker: str = 'green',
                                       sort: int = 1,
                                       need_arh_doc: bool = False,
                                       ) -> Dict:
        if count == 0:
            self.curr_select = self.current_project.find({"date": 
            {"$gt": date_start, "$lt": date_finish},
            "importance_marker": importance_marker,
            "archived": need_arh_doc}
            ).sort({'date': sort})
        else:
            self.curr_select = self.current_project.find({"date": 
            {"$gt": date_start, "$lt": date_finish},
            "importance_marker": importance_marker,
            "archived": need_arh_doc}
            ).sort({'date': sort}).limit(count)
        return self.curr_select

    def select_from_project(self,
                            project_name: str,
                            count: int = 100,
                            how: str = 'eq',
                            date: int = 0,
                            importance_marker: str = 'green',
                            sort: int = 1,
                            need_arh_doc: bool = False,
                            ) -> Dict:
        
        self.current_project = project_name
        self.curr_select = self.select_from_DB_search_by(count,
                                             how,
                                             date,
                                             importance_marker,
                                             sort, need_arh_doc)
        return self.curr_select

    def select_from_project_by_range(self,
                                     project_name: str,
                                     count: int = 100,
                                     date_start: int = 0,
                                     date_finish: int = 2000000000,
                                     importance_marker: str = 'green',
                                     sort: int = 1,
                                     need_arh_doc: bool = False,
                                     ) -> Dict:
        
        self.current_project = project_name
        self.curr_select = self.select_from_DB_search_by_range(count,
                                                   date_start,
                                                   date_finish,
                                                   importance_marker,
                                                   sort,
                                                   need_arh_doc)
        return self.curr_select
    
    def archvate_docs(self,
                      project_name: str,
                      count: int = 100,
                      how: str = 'eq',
                      date: int = 0,
                      importance_marker: str = 'green',
                      sort: int = 1,
                      need_arh_doc: bool = False,
                      ):
        self.current_project = project_name
        for curr_doc in self.select_from_DB_search_by(count,
                                             how,
                                             date,
                                             importance_marker,
                                             sort, 
                                             need_arh_doc):
            curr_doc['archived'] = True   

    def archvate_docs_by_range(self,
                               project_name: str,
                               count: int = 100,
                               date_start: int = 0,
                               date_finish: int = 2000000000,
                               importance_marker: str = 'green',
                               sort: int = 1,
                               need_arh_doc: bool = False,
                                ):
        self.current_project = project_name
        for curr_doc in self.select_from_DB_search_by_range(count,
                                                     date_start,
                                                     date_finish,
                                                     importance_marker,
                                                     sort,
                                                     need_arh_doc):
            curr_doc['archived'] = True

    def archived_curr_select(self):

        for curr_doc in self.curr_select:
            curr_doc['archived'] = True

        
    
        