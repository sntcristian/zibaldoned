import csv, json
import Levenshtein
import stanza
import re
from tqdm import tqdm

with open("paragraphs.csv", "r", encoding="utf-8") as f1:
    paragraphs = csv.DictReader(f1)
    paragraphs = list(paragraphs)
f1.close()

with open("people_labels.json", "r", encoding="utf-8") as f2:
    people = json.load(f2)
f2.close()

with open("places_labels.csv", "r", encoding="utf-8") as f3:
    places = csv.DictReader(f3)
    places = list(places)
f3.close()

# Convert labels in csv and json into same format
def convert_labels(people, places):
    output_dict = dict()
    for per in people:
        pars = per["ps"]
        for par in pars:
            if par in output_dict:
                output_dict[par].append({"id":per["wikidata"].replace("https://www.wikidata.org/wiki/",""),
                                         "labels":set([per["it"]]+per["labels"]), "type":"PER"})
            else:
                output_dict[par]=[{"id": per["wikidata"].replace("https://www.wikidata.org/wiki/", ""),"labels": set([per["it"]] + per["labels"]), "type":"PER"}]
    for loc in places:
        par = loc["par_id"]
        if par in output_dict:
            output_dict[par].append({"id":loc["wd_id"],"labels":[loc["surface"]],"type":"LOC"})
        else:
            output_dict[par]=[{"id":loc["wd_id"],"labels":[loc["surface"]],"type":"LOC"}]
    return output_dict

labels_dict = convert_labels(people=people, places=places)

#load NER model (useful later to match strings with levenshtein distance)
stanza.download('it')
nlp = stanza.Pipeline('it', processors='tokenize,ner')

pbar = tqdm(total=len(paragraphs))
annotations = list()
for par in paragraphs:
    annotated_chars = set()
    _id = par["id"]
    text = par["text"]
    text = re.sub(r"\[.*?\]\s", "", text)
    entities = labels_dict[_id]
    persons = [item for item in entities if item["type"]=="PER"]
    places = [item for item in entities if item["type"] == "LOC"]

    # match labels of places in paragraph
    for loc in places:
        pattern = loc["labels"][0]
        for match in re.finditer(pattern+"\W", text):
            surface = match.group(0)[:-1]
            start = match.start()
            end = match.end()-1
            char_ranges = set((range(start, end+1)))
            # make sure no annotation overlaps
            if len(annotated_chars.intersection(char_ranges)) == 0:
                annotations.append(
                    {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": loc["id"], "type": "LOC",
                     "match":"exact", "pattern":None})
                annotated_chars.update(char_ranges)

    # match person labels in paragraph
    for per in persons:
        patterns = per["labels"]
        sorted_patterns = sorted(patterns, key=lambda x: len(x), reverse=True)
        for pattern in sorted_patterns:
            for match in re.finditer(pattern+"\W", text):
                surface = match.group(0)[:-1]
                start = match.start()
                end = match.end()-1
                char_ranges = set((range(start, end+1)))
                if len(annotated_chars.intersection(char_ranges)) == 0:
                    annotations.append(
                        {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                         "match":"exact", "pattern":None})
                    annotated_chars.update(char_ranges)

    # use NER to find unmatched labels of persons (e.g. abbreviations)
    doc = nlp(text)
    entita_nominate = []
    for sent in doc.sentences:
        for entita in sent.ents:
            if entita.type == "PER":
                entita_nominate.append((entita.text, entita.start_char, entita.end_char))
    for per in persons:
        patterns = per["labels"]
        sorted_patterns = sorted(patterns, key=lambda x: len(x), reverse=True)
        for pattern in sorted_patterns:
            for entita in entita_nominate:
                surface = entita[0]
                # use levenshtein distance to specify similarity threshold
                distanza = Levenshtein.distance(pattern, surface)
                if distanza == 4 and len(pattern)>7:
                    start = entita[1]
                    end = entita[2]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                             "type": "PER",
                             "match": "levenshtein", "pattern": pattern})
                        annotated_chars.update(char_ranges)
                elif distanza == 3 and len(pattern)>5:
                    start = entita[1]
                    end = entita[2]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                elif distanza <= 2:
                    start = entita[1]
                    end = entita[2]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                else:
                    pattern_tokens = pattern.split(" ")
                    surface_tokens = surface.split(" ")
                    count = 0
                    for token in surface_tokens:
                        if token in pattern_tokens and len(token)>2:
                            count += 1
                    if count >= 1:
                        start = entita[1]
                        end = entita[2]
                        char_ranges = set((range(start, end + 1)))
                        if len(annotated_chars.intersection(char_ranges)) == 0:
                            annotations.append(
                                {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                                 "type": "PER",
                                 "match": "partial", "pattern": pattern})
                            annotated_chars.update(char_ranges)

    pbar.update(1)
pbar.close()

keys = annotations[0].keys()
with open("annotations.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(annotations)