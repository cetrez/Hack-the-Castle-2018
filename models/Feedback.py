from pony.orm import *
from models.DataBase import DataBase
from models.Participant import Participant
from models.Question import Question

db = DataBase.get_database()


class Feedback(db.Entity):
    id = PrimaryKey(int, auto=True)
    participant = Required('Participant')
    question = Required('Question')
    answer = Required(str)

    # ---- Query
    @staticmethod
    @db_session
    def select_all_feedback():
        return select(p for p in Feedback)[:]

    @staticmethod
    @db_session
    def create_feedback(q_id, p_id, a):
        q = Question[q_id]
        p = Participant[p_id]
        f = Feedback(question=q, participant=p, answer=a)
        return f
