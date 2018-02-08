from pony.orm import Database


class DataBase:
    instance = None

    def __init__(self):
        if not DataBase.instance:
            DataBase.instance = Database()

    @staticmethod
    def get_database():
        if not DataBase.instance:
            DataBase.instance = Database()
        return DataBase.instance

    @staticmethod
    def generate():
        DataBase.instance.bind(provider='sqlite', filename='database.sqlite', create_db=True)
        DataBase.instance.generate_mapping(create_tables=True)













