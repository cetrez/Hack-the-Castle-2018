from pony.orm import *

db = Database()

class Info(db.Entity):
    keywords = Required(str)
    text = Required(str)

class Group(db.Entity):
    name = Required(str)
    participants = Set('Participant')

class Participant(db.Entity):
    name = Required(str)
    fb_id = Required(str)
    group = Required(Group)

class Question(db.Entity):
    question = Required(str)
    template = Required('Questionaire')

class Questionaire(db.Entity):
    questions = Set(Question)

class Feedback:
    question = Required(Question)
    participant = Required(Participant)
    answer = Required(str)

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

