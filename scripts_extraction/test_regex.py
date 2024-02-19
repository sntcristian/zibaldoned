import re
import csv

regex = r"(([A-Z][a-z]{0,4}[\W]+)?([A-Z][a-z]+)(\s([A-Z][a-z]{0,4}\W)?([A-Z][a-z]+))?\.?)"

with open("../paragraphs.csv", "r", encoding="utf-8") as f1:
    paragraphs = csv.DictReader(f1)
    paragraphs = list(paragraphs)
f1.close()

for par in paragraphs:
    annotated_chars = set()
    _id = par["id"]
    text = par["text"]
    text = re.sub(r"\[.*?\]\s", "", text)
    matches = re.findall(regex, text)
    for match in matches:
        print(match)
