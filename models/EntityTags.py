from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class EntityTags(db.Entity):
    id = PrimaryKey(int, auto=True)
    tag_value = Required(str)
    expressions = Required(str)
    info = Optional('Info')
    qstnnr = Optional('Questionnaire')

    # ---- Query
    @staticmethod
    @db_session
    def select_all_entitytag():
        return select(p for p in EntityTags)[:]

    @staticmethod
    @db_session
    def select_entitytag(_id):
        et = EntityTags[_id]
        return EntityTags[_id]

    @staticmethod
    @db_session
    def create_entitytag(tv, exprs):
        et = EntityTags(tag_value=tv, expressions=exprs)
        return et
