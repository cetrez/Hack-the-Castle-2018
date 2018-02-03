from pony.orm import *

db = Database()

class Info(db.Entity):
    keywords = Required(str)
    text = Required(str)

class EntityTags(db.Entity):
    tag_value = Required(str)
    expressions = Required(str)

class Group(db.Entity):
    name = Required(str)
    participants = Set('Participant')

class Participant(db.Entity):
    name = Required(str)
    fb_id = Required(str)
    group = Optional(Group)

class Question(db.Entity):
    question = Required(str)

class Feedback:
    question = Required(Question)
    participant = Required(Participant)
    answer = Required(str)

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


#---- Participants
@db_session
def create_participant(name, fb_id):
    p = Participant(name=name, fb_id=fb_id)
    return p

@db_session
def get_participant(fb_id):
    return Participant.get(fb_id=fb_id)

@db_session
def select_participants():
    return select(p for p in Participant)[:]


#---- Questions
@db_session
def select_questions():
    return select(p for p in Question)[:]

@db_session
def create_question(q):
    p = Question(question=q)
    return p


#---- Feedback
@db_session
def select_feedbacks():
    return select(p for p in Feedback)[:]

@db_session
def create_feedback(q, p, a):
    f = Feedback(question=q, participant=p, answer=a)
    return f


#---- EntityTags
@db_session
def select_all_entitytag():
    return select(p for p in Question)[:]

@db_session
def create_entitytag(tv, exprs):
    et = EntityTags(tag_value=tv, expressions=exprs)
    return et
