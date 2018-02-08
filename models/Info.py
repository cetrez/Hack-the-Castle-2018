from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class Info(db.Entity):
    id = PrimaryKey(int, auto=True)
    tag = Set('EntityTags')
    text = Required(str)

    @staticmethod
    @db_session
    def select_all_info():
        return select(i for i in Info)[:]

    @staticmethod
    @db_session
    def select_info(keyword):
        return select(i for i in Info if keyword in i.keywords)[:]

    @staticmethod
    @db_session
    def create_info(tag, text):
        i = Info(tag=tag, text=text)
        return i
