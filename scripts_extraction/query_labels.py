import json
import requests


json_f = open("../people.json", "r", encoding="utf-8")
data = json.load(json_f)
json_f.close()

output = list()
for item in data:
    q_id = item["wikidata"].replace("https://www.wikidata.org/wiki/", "wd:")
    url = 'http://localhost:1234/api/endpoint/sparql'
    headers = {'Accept': 'application/sparql-results+json'}
    query = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX schema: <http://schema.org/>
    
    SELECT ?label ?altLabel ?prefLabel ?name
    WHERE {
    """ + q_id + """ rdfs:label ?label.
    FILTER (lang(?label) = "it")
    OPTIONAL {
        """ + q_id + """ skos:altLabel ?altLabel .
        FILTER (lang(?altLabel) = "it")
        }
    OPTIONAL {
        """ + q_id + """ skos:prefLabel ?prefLabel .
        FILTER (lang(?prefLabel) = "it")
        }
    OPTIONAL {
        """ + q_id + """ schema:name ?name .
        FILTER (lang(?name) = "it")
        }
    }
    """
    response = requests.post(url, headers=headers, data={'query': query})
    results = response.json()
    labels = set()
    try:
        for result in results["results"]["bindings"]:
            for value in result.values():
                labels.add(value["value"])
    except Exception as e:
        print(results, q_id)
    item["labels"] = list(labels)
    output.append(item)

out_f = open("../people_labels.json", "w", encoding="utf-8")
json.dump(output, out_f, indent=4, ensure_ascii=False)