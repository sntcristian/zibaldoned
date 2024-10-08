import json
import csv
from tqdm import tqdm
import time
import requests
from thefuzz import fuzz
import re

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f:
    list_of_paragraphs = csv.DictReader(f)
    list_of_paragraphs = list(list_of_paragraphs)


with open("../results/mgenre_el/candidates.json", "r", encoding="utf-8") as f2:
    list_of_candidates = json.load(f2)

output = []
list_of_paragraphs = list_of_paragraphs[150:]

def execute_sparql_query(query, max_retries=5, backoff_factor=1):
    # Definizione dell'endpoint SPARQL di Wikidata
    endpoint_url = "https://query.wikidata.org/sparql"

    # Parametri per la richiesta HTTP
    params = {
        'query': query,
        'format': 'json'
    }

    for attempt in range(max_retries):
        response = requests.get(endpoint_url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Calcolo del ritardo esponenziale
            delay = backoff_factor * (2 ** attempt)
            print(f"Rate limit exceeded. Waiting {delay} seconds before retrying...")
            time.sleep(delay)
        else:
            raise Exception(f"Errore nella richiesta SPARQL: {response.status_code}")

    raise Exception(f"Errore nella richiesta SPARQL dopo {max_retries} tentativi.")


def query_person(item_id):
    output = {"label": "", "birth_date":"", "classes": []}

    query_label = f"""
    SELECT ?itemLabel ?birthdate
    WHERE {{
      wd:{item_id} rdfs:label ?itemLabel .
      FILTER(lang(?itemLabel)="it")
      OPTIONAL {{
        wd:{item_id} wdt:P569 ?birthdate .
      }}
    }}
    """

    # Esecuzione della query
    results = execute_sparql_query(query_label)
    print("Risultati query_label per query_person:", results)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    for result in bindings:
        itemLabel = result.get("itemLabel", {}).get("value", "")
        output["label"] = itemLabel
        birthdate = result.get("birthdate", {}).get("value", "N/A")
        output["birth_date"] = birthdate

    query_classes = f"""
        SELECT ?class ?classLabel ?supclass ?supclassLabel
        WHERE {{
          wd:{item_id} wdt:P31 ?class.
          OPTIONAL {{
            ?class wdt:P279* ?supclass.
          }}
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en" .
           }}
        }}
        """

    # Esecuzione della query
    results = execute_sparql_query(query_classes)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    classes = set()
    for result in bindings:
        classLabel = result.get("classLabel", {}).get("value", "")
        if len(classLabel) > 0:
            classes.add(classLabel.lower())
        supclassLabel = result.get("supclassLabel", {}).get("value", "")
        if len(supclassLabel) > 0:
            classes.add(supclassLabel.lower())
    output["classes"] = classes
    return output


def query_location(item_id):
    output = {"label":"", "classes":[]}

    query_label = f"""
    SELECT ?itemLabel
    WHERE {{
      wd:{item_id} rdfs:label ?itemLabel .
      FILTER(lang(?itemLabel)="it")
    }}
    """

    # Esecuzione della query
    results = execute_sparql_query(query_label)
    print("Risultati query_label per query_location:", results)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    for result in bindings:
        itemLabel = result.get("itemLabel", {}).get("value", "")
        output["label"] = itemLabel

    query_classes = f"""
        SELECT ?class ?classLabel ?supclass ?supclassLabel
        WHERE {{
          wd:{item_id} wdt:P31 ?class.
          OPTIONAL {{
            ?class wdt:P279* ?supclass.
          }}
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en" .
           }}
        }}
        """

    # Esecuzione della query
    results = execute_sparql_query(query_classes)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    classes = set()
    for result in bindings:
        classLabel = result.get("classLabel", {}).get("value", "")
        if len(classLabel) > 0:
            classes.add(classLabel.lower())
        supclassLabel = result.get("supclassLabel", {}).get("value", "")
        if len(supclassLabel) > 0:
            classes.add(supclassLabel.lower())
    output["classes"] = classes
    return output


def query_work(item_id):
    output = {"label": "", "publication_date": "", "classes": []}

    query_label = f"""
    SELECT ?itemLabel ?publicationDate
    WHERE {{
      wd:{item_id} rdfs:label ?itemLabel .
      FILTER(lang(?itemLabel)="it")
      OPTIONAL {{
        wd:{item_id} wdt:P577 ?publicationDate .
      }}
    }}
    """

    # Esecuzione della query
    results = execute_sparql_query(query_label)
    print("Risultati query_label per query_work:", results)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    for result in bindings:
        itemLabel = result.get("itemLabel", {}).get("value", "")
        output["label"] = itemLabel
        publicationDate = result.get("publicationDate", {}).get("value", "N/A")
        output["publication_date"] = publicationDate

    query_classes = f"""
        SELECT ?class ?classLabel ?supclass ?supclassLabel
        WHERE {{
          wd:{item_id} wdt:P31 ?class.
          OPTIONAL {{
            ?class wdt:P279* ?supclass.
          }}
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en" .
           }}
        }}
        """

    # Esecuzione della query
    results = execute_sparql_query(query_classes)

    # Estrazione dei risultati
    bindings = results["results"]["bindings"]
    classes = set()
    for result in bindings:
        classLabel = result.get("classLabel", {}).get("value", "")
        if len(classLabel) > 0:
            classes.add(classLabel.lower())
        supclassLabel = result.get("supclassLabel", {}).get("value", "")
        if len(supclassLabel) > 0:
            classes.add(supclassLabel.lower())
    output["classes"] = classes
    return output

pbar = tqdm(total=len(list_of_paragraphs))
for paragraph in list_of_paragraphs:
    _id = paragraph["id"]
    text = paragraph["text"]
    candidates_paragraph = [candidate for candidate in list_of_candidates if candidate["id"]==_id]
    for candidates in candidates_paragraph:
        list_of_wdentities = [item["wb_id"] for item in candidates["candidates"]]
        entity_type = candidates["type"]
        surface_form = text[int(candidates["start_pos"]):int(candidates["end_pos"])]
        filtered_candidates = []
        max_ratio = 0
        for item in list_of_wdentities:
            if entity_type=="PER":
                data = query_person(item) #dictionary: {"label", "birth_date", "classes"}
                label = data.get("label","")
                birth_date = re.match(r'^\-?\d{4}', data["birth_date"])
                classes = data["classes"]
                if birth_date:
                    date = birth_date.group(0)
                    if date.startswith("-"):
                        date = 0
                    else:
                        date = int(birth_date.group(0))
                    if date > 1833:
                        continue
                if "person" not in classes or "wikimedia disambiguation page" in classes:
                    continue
                ratio = fuzz.ratio(surface_form.lower(), label.lower())
                if ratio>max_ratio:
                    max_ratio=ratio
                    filtered_candidates.insert(0, (item, label, ratio))
                else:
                    filtered_candidates.append((item, label, ratio))
            elif entity_type=="LOC":
                data = query_location(item) #dictionary: {"label", "classes"}
                label = data["label"]
                classes = data["classes"]
                if "geographic location" not in classes or "wikimedia disambiguation page" in classes:
                    continue
                ratio = fuzz.ratio(surface_form.lower(), label.lower())
                if ratio>max_ratio:
                    max_ratio=ratio
                    filtered_candidates.insert(0, (item, label, ratio))
                else:
                    filtered_candidates.append((item, label, ratio))

            elif entity_type=="WORK":
                data = query_work(item) #dictionary: {"label", "publication_date", "classes"}
                label = data["label"]
                publication_date = re.match(r'^\d{4}', data["publication_date"])
                classes = data["classes"]
                if publication_date:
                    date = int(publication_date.group(0))
                    if date > 1833:
                        continue
                if "work" not in classes or "wikimedia disambiguation page" in classes:
                    continue
                ratio = fuzz.ratio(surface_form.lower(), label.lower())
                if ratio>max_ratio:
                    max_ratio=ratio
                    filtered_candidates.insert(0, (item, label, ratio))
                else:
                    filtered_candidates.append((item, label, ratio))

        if len(filtered_candidates)>=1:
            output.append({"id": _id, "start_pos": candidates["start_pos"], "end_pos": candidates["end_pos"],
                                "surface": surface_form, "type": candidates["type"],
                                "wb_id": filtered_candidates[0][0], "alias":filtered_candidates[0][1]})
        else:
            output.append({"id": _id, "start_pos": candidates["start_pos"], "end_pos": candidates["end_pos"],
                           "surface": surface_form, "type": candidates["type"],
                           "wb_id": "NIL", "alias":""})
    pbar.update(1)





keys = output[0].keys()
with open('../results/mgenre_el/output_filtered_150.csv', 'w', encoding='utf-8') as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
    f.close()





