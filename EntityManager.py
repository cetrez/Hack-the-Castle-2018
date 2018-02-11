import requests
from config import CONFIG

url = 'https://api.wit.ai/apps?v=20170307'

hed = {'Authorization': 'Bearer ' + CONFIG['WIT_BASE_TOKEN']}


def getData(value, expressions) :
    return {"doc": value+"Doc",
            "lookups": ["trait"],
            "id": (value+"UD"),
            "values": [
                {"value": value, "expressions": expressions}
            ]}


def addEntity(value, epxresstions) :
    return requests.post(url = url, json = getData(value, epxresstions), headers=hed)
