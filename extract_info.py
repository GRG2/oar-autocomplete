import csv
import json
import re
from typing import Dict

nerdm = (
    open("nerdm.json", "r", encoding="utf-8")
    .read()
    .encode("latin-1", errors="ignore")
    .decode("utf-8", errors="ignore")
)
nerdm = json.loads(nerdm)

lastnames = {}
fullnames = {}
contactnames = {}
keywords = {}
topics = {}

def dict_increment(dict, key):
    dict[key] = dict.get(key, 0) + 1


for document in nerdm["ResultData"]:
    title = document["title"]
    for author in document.get("authors", []):
        fullname = " ".join(author["fn"].split())
        dict_increment(fullnames, fullname)
        if ("familyName" in author):
            familyName = author["familyName"]
            dict_increment(
                lastnames,
                author["familyName"].strip() + " " + " ".join(author["fn"].split()[1:]),
            )

    if "contactPoint" in document.keys():
        dict_increment(contactnames, " ".join(document["contactPoint"]["fn"].split()))

    if "keyword" in document.keys():
        for keyword in document["keyword"]:
            dict_increment(keywords, keyword.lower())
    
    if "topic" in document.keys():
        for topic in document["topic"]:
            dict_increment(topics, topic["tag"].lower().split(":")[0])
    

fieldnames = ["TERM_REDUCED", "SECTION", "FREQ"]
writer = csv.DictWriter(
    open("parsed.csv", "w+", newline=''),
    delimiter=",",
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL,
    fieldnames=fieldnames
)

writer.writeheader()

for lastname, count in lastnames.items():
    writer.writerow({
        "TERM_REDUCED": lastname,
        "SECTION": "Lastname",
        "FREQ": count
    })
for fullname, count in fullnames.items():
    writer.writerow({
        "TERM_REDUCED": fullname,
        "SECTION": "Fullname",
        "FREQ": count
    })
for contactname, count in contactnames.items():
    writer.writerow({
        "TERM_REDUCED": contactname,
        "SECTION": "ContactPoint",
        "FREQ": count
    })
for keyword, count in keywords.items():
    writer.writerow({
        "TERM_REDUCED": keyword,
        "SECTION": "Keyword",
        "FREQ": count
    })
for topic, count in topics.items():
    writer.writerow({
        "TERM_REDUCED": topic,
        "SECTION": "Topic",
        "FREQ": count
    })
