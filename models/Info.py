from pony.orm import *
from models.DataBase import DataBase
from models.EntityTags import EntityTags

db = DataBase.get_database()


class Info(db.Entity):
    id = PrimaryKey(int, auto=True)
    tag = Required('EntityTags')
    info_text = Required(str)

    @staticmethod
    @db_session
    def select_all_info():
        all_info = select(info for info in Info)[:]
        for x in range(0, len(all_info)):
            all_info[x].tag.load()
        return all_info

    @staticmethod
    @db_session
    def get_info(keyword):
        et = EntityTags.get(tag_value=keyword)
        if et is not None:
            i = Info.get(tag=et)
            return i
        return None

    @staticmethod
    @db_session
    def create_info(tag_id, info_text):
        et = EntityTags.select_entitytag(tag_id)
        i = Info(tag=et, info_text=info_text)
        return i
