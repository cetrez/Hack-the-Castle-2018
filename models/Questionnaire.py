from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()


class Questionnaire(db.Entity):
    id = PrimaryKey(int, auto=True)
    event = Required(str)
    title = Required(str)
    questions = Set('Question')

    @staticmethod
    @db_session
    def select_all_questionnaires():
        q = select(p for p in Questionnaire)[:]
        for x in range(0, len(q)):
            q[x].questions.load()
        return q

    @staticmethod
    @db_session
    def select_all_questions():
        q = select(p for p in Questionnaire)[:]
        for x in range(0, len(q)):
            q[x].load()
            q[x].questions.load()
        return q

    @staticmethod
    @db_session
    def create_questionnaire(title):
        p = Questionnaire(title=title, event='Hack the castle')
        return p