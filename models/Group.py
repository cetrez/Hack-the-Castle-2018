from pony.orm import *
from models.DataBase import DataBase

db = DataBase.get_database()

class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    participants = Set('Participant')
