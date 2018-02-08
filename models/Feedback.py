from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class Feedback(db.Entity):
    id = PrimaryKey(int, auto=True)
    participant = Required(str)
    question = Required('Question')
    answer = Required(str)

    # ---- Query
    @staticmethod
    @db_session
    def select_all_feedback():
        return select(p for p in Feedback)[:]

    @staticmethod
    @db_session
    def create_feedback(self, q, p, a):
        f = Feedback(question=q, participant=p, answer=a)
        return f
