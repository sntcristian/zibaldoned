import requests
import re
import json
from bs4 import BeautifulSoup



def web_scraper(url):
    response = requests.get(url)
    output = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trova tutte le div con classe "person-entry"
        person_entries = soup.find_all('div', class_='person-entry')

        # Itera su tutte le div trovate
        for person_entry in person_entries:
            # Trova i link all'interno di ciascuna div
            wikidata_label = person_entry.find('label', string="Wikidata ")
            if wikidata_label:
                wikidata_url = wikidata_label.find_next("a")
                wikidata_url = wikidata_url.get("href")
                italian_label = person_entry.find('label', string='Italian')
                italian_name = italian_label.find_parent('p')
                label_text = italian_name.text.strip()
                label_text = re.sub("Italian: ", "", label_text)
                ps = set()
                links = person_entry.find_all('a', href=lambda href: href and href.startswith(
                    'https://digitalzibaldone.net/node/p'))
                # Stampa i link trovati
                for link in links:
                    p_id = re.sub("https://digitalzibaldone.net/node/", "", link.get('href'))
                    ps.add(p_id)
                ps = list(ps)
                if len(ps)>0:
                    output.append({"wikidata":wikidata_url, "it":label_text, "ps":ps})

        return output
    else:
        print(f"Errore {response.status_code}: Impossibile recuperare la pagina")
        return None

# Sostituisci con l'URL della pagina che vuoi analizzare
url_to_scrape = 'https://digitalzibaldone.net/index/people'
response = web_scraper(url_to_scrape)
if response:
    with open("people.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False)

print(len(response))