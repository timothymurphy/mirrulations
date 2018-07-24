import json

def read_value(value):
    m = json.loads(open("config.json","r").read())
    return m[value]