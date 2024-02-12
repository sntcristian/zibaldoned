import csv
import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re


with open("../people.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ps = set()
for row in data:
    ps.update(row["ps"])

output = []
places = []

pbar = tqdm(total=len(ps))
for p in ps:
    response = requests.get("https://digitalzibaldone.net/node/"+p)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        node = soup.find('div', id=p)
        if node:
            text = re.sub("\s+", " ", node.text)
            output.append({"id":p, "text":text})
            wikidata_links = node.find_all('a', href=lambda href: href and href.startswith(
                    '/paragraph/Q'))
            for link in wikidata_links:
                surface = re.sub("\s+", " ", link.text.strip())
                wiki_id = re.sub("/paragraph/", "", link.get("href"))
                places.append({"surface":surface, "wd_id":wiki_id, "par_id":p})
            pbar.update(1)
    else:
        pbar.update(1)
        continue

o_keys = output[0].keys()
with open("../paragraphs.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, o_keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)

p_keys = places[0].keys()
with open("places.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, p_keys)
    dict_writer.writeheader()
    dict_writer.writerows(places)