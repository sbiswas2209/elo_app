import json
from utils.database import insert_document, delete_all

delete_all("actresses")

with open('data.json') as f:
    d = json.load(f)
    for element in d:
        insert_document("actresses", {
            'url': element["url"],
            'name': element["name"],
            'rating': 100,
            "recentActivity": 0
        })