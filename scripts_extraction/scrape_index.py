import requests
import json
from bs4 import BeautifulSoup

# URL della pagina da scaricare
url = 'https://digitalzibaldone.net/index/1827'

# Scaricare il contenuto della pagina
response = requests.get(url)
html_content = response.content

# Analizzare il contenuto HTML con BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Estrarre i dati dall'HTML e convertirli in formato JSON
index_entries = []

for entry in soup.find_all('div', class_='index-entry'):
    theme_id = entry.find('a')['href'].replace('..', '')
    theme_it = entry.find('div', class_='index-title-it').get_text(strip=True)
    theme_en = entry.find('div', class_='index-title-en').get_text(strip=True)
    paragraphs = [a['href'].replace('../paragraph/', 'https://digitalzibaldone.net/node/') for a in entry.find_all('a',
                                                                                                         href=True) if 'paragraph' in a['href']]

    index_entry = {
        "theme_id": theme_id,
        "theme_it": theme_it,
        "theme_en": theme_en,
        "paragraphs": paragraphs
    }

    index_entries.append(index_entry)


with open("../data/index_entries.json", "w", encoding="utf-8") as f:
    json.dump(index_entries, f, ensure_ascii=False, sort_keys=False, indent=4)


