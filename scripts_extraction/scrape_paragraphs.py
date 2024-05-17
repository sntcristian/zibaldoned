import csv
import requests
from bs4 import BeautifulSoup
import re



initial_paragraph = "https://digitalzibaldone.net/node/p1_1"

output = []
places = []
persons = []
works = []

def scrape_paragraphs_recursive(paragraph_num):
    if paragraph_num != None:
        response = requests.get(paragraph_num)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            nextprev_div = soup.find('div', class_='nextprev')
            if paragraph_num == "https://digitalzibaldone.net/node/p1_1":
                link_p_seguente = nextprev_div.find_all('a')[0]
            elif paragraph_num == "https://digitalzibaldone.net/node/p800_1":
                link_p_seguente = None
            else:
                link_p_seguente = nextprev_div.find_all('a')[1]
            if link_p_seguente != None:
                next_page = link_p_seguente.get("href")
            else:
                next_page = None
            print(next_page)
            node = soup.find('div', id=paragraph_num.replace("https://digitalzibaldone.net/node/", ""))
            if node:
                text = re.sub("\s+", " ", node.text)
                text = re.sub(r"^\[.*?\]\s", "", text)
                output.append({"id": paragraph_num, "text": text})
                links = node.find_all("a")
                for link in links:
                    href = link.get("href")
                    if href.startswith("https://www.wikidata.org/wiki/"):
                        surface = re.sub("\s+", " ", link.text.strip())
                        places.append({"surface":surface, "_id":href, "par_id":paragraph_num})
                    elif "person" in link.get("class", []):
                        surface = re.sub("\s+", " ", link.text.strip())
                        persons.append({"surface": surface, "_id": href, "par_id": paragraph_num})
                    elif href.startswith("/node/") and not href.startswith("/node/p"):
                        surface = re.sub("\s+", " ", link.text.strip())
                        works.append({"surface": surface, "_id": href.replace("/node/", ""), "par_id": paragraph_num})
            scrape_paragraphs_recursive(next_page)
    else:
        return None

scrape_paragraphs_recursive(initial_paragraph)

if len(output)>0:
    o_keys = output[0].keys()
    with open("../data/paragraphs_1_1_800_1.csv", "w", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, o_keys)
        dict_writer.writeheader()
        dict_writer.writerows(output)

if len(places)>0:
    p_keys = places[0].keys()
    with open("places_1_1_800_1.csv.csv", "w", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, p_keys)
        dict_writer.writeheader()
        dict_writer.writerows(places)

if len(persons)>0:
    p_keys = persons[0].keys()
    with open("people_1_1_800_1.csv.csv", "w", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, p_keys)
        dict_writer.writeheader()
        dict_writer.writerows(persons)

if len(works)>0:
    w_keys = works[0].keys()
    with open("works_1_1_800_1.csv.csv", "w", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, w_keys)
        dict_writer.writeheader()
        dict_writer.writerows(works)