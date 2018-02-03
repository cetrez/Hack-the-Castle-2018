from pony.orm import *

db = Database()


class Info(db.Entity):
    id = PrimaryKey(int, auto=True)
    keywords = Required(str)
    text = Required(str)


class EntityTags(db.Entity):
    id = PrimaryKey(int, auto=True)
    tag_value = Required(str)
    expressions = Required(str)


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    participants = Set('Participant')


class Participant(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    fb_id = Required(str)
    group = Optional(Group)
    question = Optional(int)


class Question(db.Entity):
    id = PrimaryKey(int, auto=True)
    question = Required(str)


class Feedback(db.Entity):
    id = PrimaryKey(int, auto=True)
    participant = Required(str)
    question = Optional(str)
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

@db_session
def select_info(keyword):
    return select(i for i in Info if keyword in i.keywords)[:]

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

@db_session
def update_participant(p_id, q):
    Participant.get(id=p_id).question = q

#---- EntityTags
@db_session
def select_all_entitytag():
    return select(p for p in EntityTags)[:]

@db_session
def create_entitytag(tv, exprs):
    et = EntityTags(tag_value=tv, expressions=exprs)
    return et
