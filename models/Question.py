from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class Question(db.Entity):
    id = PrimaryKey(int, auto=True)
    question = Required(str)
    feedback = Optional('Feedback')

    @staticmethod
    @db_session
    def select_all_questions():
        return select(p for p in Question)[:]

    @staticmethod
    @db_session
    def create_question(q):
        p = Question(question=q)
        return p
