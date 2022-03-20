import pymongo
from typing import Dict
from typing import List

from DB import read_service


class DBManagement:

    def __init__(self):
        url = read_service.get_mongo_url()
        self.client = pymongo.MongoClient(url)
        self.current_DB = self.client["projects_issuses"]

    def connect_to_a_project(self, project_name: str):
        self.current_project = self.current_DB[project_name]

    def _get_id(self, message: Dict) -> List:
        types_of_content = ["voice", "photo",
                            "video", "audio", "document", "location"]
        for i in types_of_content:
            if message[i]:
                content_type = i
                break
        content_id = message[content_type]["id"]
        return [content_type, content_id]

    def insert_into_db(
            self,
            project_name,
            message: Dict,
            importance_marker: bool,
            message_type,
    ):

        self.connect_to_a_project(project_name)

        if message["text"] is None:
            content_type, content_id = self._get_id(message)
        else:
            content_type = 'text'
            content_id = None
        cur_dict = {
            "message_id": message["message_id"],
            "chat_id": message["chat"]["id"],
            "user_id": message["from"]["id"],
            "first_name": message["from"]["first_name"],
            "last_name": message["from"]["last_name"],
            "user_name": message["from"]["username"],
            "date": message["date"],
            "importance_marker": importance_marker,
            "message_text": message["text"],
            "media_group_id": message["media_group_id"],
            "message_type": message_type,
            "content_type": content_type,
            "content_id": content_id,
            "archived": False
        }
        self.current_project.insert_one(cur_dict)

    def insert_information_about_projects(
            self,
            project_name: str,
            project_info: Dict,
    ):
        self.projects_discr = self.current_DB["projects_info"]
        self.projects_discr.insert_one(project_info)

    def select_from_db(
            self,
            project_name,
            count: int = 100,
            how: str = 'eq',
            date: int = 0,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ) -> Dict:
        self.current_project = self.current_DB[project_name]
        if count == 0:
            if how == 'eq':
                self.curr_select = self.current_project.find(
                    {
                        "archived": need_arh_doc
                    },
                )
            else:
                self.curr_select = self.current_project.find(
                    {
                        "date": {how: date},
                        "archived": need_arh_doc
                    },
                ).sort({'date': sort})

        else:
            if how == 'eq':
                self.curr_select = self.current_project.find(
                    {
                        "date": date,
                        "archived": need_arh_doc
                    },
                ).sort({'date': sort}).limit(count)
            else:
                self.curr_select = self.current_project.find(
                    {
                        "date": {how: date},
                        "archived": need_arh_doc
                    },
                ).sort({'date': sort}).limit(count)
        return self.curr_select

    def select_search_by_range(
            self,
            count: int = 100,
            date_start: int = 0,
            date_finish: int = 2000000000,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ) -> Dict:
        if count == 0:
            self.curr_select = self.current_project.find(
                {
                    "date": {"$gt": date_start, "$lt": date_finish},
                    "archived": need_arh_doc
                },
            ).sort({'date': sort})
        else:
            self.curr_select = self.current_project.find(
                {
                    "date": {"$gt": date_start, "$lt": date_finish},
                    "archived": need_arh_doc
                },
            ).sort({'date': sort}
                   ).limit(count)

        return self.curr_select

    def select_by_red_marker(
            self,
            count: int = 100,
            date: int = 0,
            sort: int = 1,
            need_arh_doc: bool = False
    ) -> Dict:

        self.curr_select = self.current_project.find(
            {
                "date": {'$gt': date}
            },
        ).sort({'date': sort}
               ).limit(count)
        return self.curr_select

    def select_from_project(
            self,
            project_name: str,
            count: int = 100,
            how: str = 'eq',
            date: int = 0,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ) -> Dict:

        self.connect_to_a_project(project_name)
        self.curr_select = self.select_from_db(count,
                                               how,
                                               date,
                                               importance_marker,
                                               sort, need_arh_doc)
        return self.curr_select

    def select_from_project_by_range(
            self,
            project_name: str,
            count: int = 100,
            date_start: int = 0,
            date_finish: int = 2000000000,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ) -> Dict:

        self.connect_to_a_project(project_name)
        self.curr_select = self.select_search_by_range(
            count,
            date_start,
            date_finish,
            importance_marker,
            sort,
            need_arh_doc,
        )
        return self.curr_select

    def archvate_docs(
            self,
            project_name: str,
            count: int = 100,
            how: str = 'eq',
            date: int = 0,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ):
        self.connect_to_a_project(project_name)
        for curr_doc in self.select_from_db(
                count,
                how,
                date,
                importance_marker,
                sort,
                need_arh_doc):
            curr_doc['archived'] = True

    def archivate_docs_by_range(
            self,
            project_name: str,
            count: int = 100,
            date_start: int = 0,
            date_finish: int = 2000000000,
            importance_marker: str = 'green',
            sort: int = 1,
            need_arh_doc: bool = False,
    ):
        self.connect_to_a_project(project_name)
        for curr_doc in self.select_search_by_range(
                count,
                date_start,
                date_finish,
                importance_marker,
                sort,
                need_arh_doc):
            curr_doc['archived'] = True

    def archived_curr_select(self):

        for curr_doc in self.curr_select:
            curr_doc['archived'] = True
