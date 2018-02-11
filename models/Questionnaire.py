from pony.orm import *
from models.DataBase import DataBase
from models.EntityTags import EntityTags
db = DataBase.get_database()


class Questionnaire(db.Entity):
    id = PrimaryKey(int, auto=True)
    event = Required(str)
    title = Required(str)
    tag = Optional('EntityTags')
    questions = Set('Question')
    bot_state = Optional('State')

    @staticmethod
    @db_session
    def get_questionnaire(keyword):
        et = EntityTags.get(tag_value=keyword)
        q = Questionnaire.get(tag=et)
        q.load()
        return q

    @staticmethod
    @db_session
    def select_all_questionnaires():
        q = select(p for p in Questionnaire)[:]
        for x in range(0, len(q)):
            q[x].questions.load()
            q[x].tag.load()
        return q

    @staticmethod
    @db_session
    def select_all_questions(qstnnr_id):
        # an array of question obj
        questions = select((qst.questions) for qst in Questionnaire if qst.id == qstnnr_id)[:]
        return questions

    @staticmethod
    @db_session
    def create_questionnaire(title, et_id):
        et = EntityTags[et_id]
        q = Questionnaire(title=title, tag=et, event='Hack the castle')
        return q
