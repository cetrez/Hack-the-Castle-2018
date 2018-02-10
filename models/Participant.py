from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class Participant(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    fb_id = Required(int)
    group = Optional('Group')
    question = Optional(int)
    feedback = Set('Feedback')
    bot_state = Optional('State')

    # ---- Query
    @staticmethod
    @db_session
    def create_participant(name, fb_id):
        p = Participant(name=name, fb_id=fb_id)
        return p

    @staticmethod
    @db_session
    def get_participant(fb_id):
        return Participant.get(fb_id=fb_id)

    @staticmethod
    @db_session
    def select_all_participants():
        return select(p for p in Participant)[:]

    @staticmethod
    @db_session
    def update_participant(p_id, q):
        Participant.get(id=p_id).question = q
