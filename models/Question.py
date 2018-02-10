from pony.orm import *
from models.DataBase import DataBase
from models.Questionnaire import Questionnaire

db = DataBase.get_database()


class Question(db.Entity):
    id = PrimaryKey(int, auto=True)
    qtnnr = Required('Questionnaire')
    question = Required(str)
    feedback = Optional('Feedback')

    @staticmethod
    @db_session
    def select_all_questions():
        return select(p for p in Question)[:]

    @staticmethod
    @db_session
    def create_question(q, qstnnr_id):
        qstnnr = Questionnaire[qstnnr_id]
        p = Question(question=q, qtnnr=qstnnr)
        return p
