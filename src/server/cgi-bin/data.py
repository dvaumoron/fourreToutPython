
import json

def load():
    with open("data.json") as f:
        return json.load(f)

def dump(d):
    with open("data.json", mode="w") as f:
        json.dump(d, f, indent="\t")
