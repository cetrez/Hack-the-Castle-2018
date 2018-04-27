from pony.orm import *
from models.DataBase import DataBase
from models.Participant import Participant
from models.Questionnaire import Questionnaire

db = DataBase.get_database()


class State(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required('Participant')
    qstnnr = Required('Questionnaire')
    q_numb = Required(int)

    @staticmethod
    @db_session
    def get_state(part_id):
        user = Participant.get_participant(part_id)
        state = State.get(user=user)
        return state

    @staticmethod
    @db_session
    def create_state(part_id, qstn_id):
        p = Participant.get_participant(part_id)
        q = Questionnaire[qstn_id]
        state = State(user=p, qstnnr=q, q_numb=0)
        return state

    @staticmethod
    @db_session
    def inc_state(part_id):
        user = Participant.get_participant(part_id)
        state = State.get(user=user)
        if state is not None:
            state.q_numb += 1
        return state

    @staticmethod
    @db_session
    def delete_state(part_id):
        user = Participant.get_participant(part_id)
        state = State.get(user=user)
        state.delete()
        return True
