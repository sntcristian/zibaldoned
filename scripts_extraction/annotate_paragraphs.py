import csv
import re
from tqdm import tqdm



with open("paragraphs.csv", "r", encoding="utf-8") as f1:
    paragraphs = csv.DictReader(f1)
    paragraphs = list(paragraphs)
f1.close()

with open("places.csv", "r", encoding="utf-8") as f3:
    places = csv.DictReader(f3)
    places = list(places)
f3.close()

with open("people.csv", "r", encoding="utf-8") as f3:
    people = csv.DictReader(f3)
    people = list(people)
f3.close()

with open("works.csv", "r", encoding="utf-8") as f3:
    works = csv.DictReader(f3)
    works = list(works)
f3.close()


# Convert labels in csv and json into same format
def convert_labels(people, places, works):
    output_dict = dict()
    for loc in places:
        _id = loc["_id"].replace("https://www.wikidata.org/wiki/", "")
        par = loc["par_id"]
        if par in output_dict:
            output_dict[par].append({"id":_id,"labels":[loc["surface"]],"type":"LOC"})
        else:
            output_dict[par]=[{"id":_id,"labels":[loc["surface"]],"type":"LOC"}]
    for per in people:
        _id = per["_id"].replace("https://digitalzibaldone.net/node/", "")
        par = per["par_id"]
        if par in output_dict:
            output_dict[par].append({"id":_id,"labels":[per["surface"]],"type":"PER"})
        else:
            output_dict[par]=[{"id":_id,"labels":[per["surface"]],"type":"PER"}]
    for work in works:
        if work["_id"].startswith("seq"):
            continue
        else:
            par = work["par_id"]
            if par in output_dict:
                output_dict[par].append({"id":work["_id"],"labels":[work["surface"]],"type":"WORK"})
            else:
                output_dict[par]=[{"id":work["_id"],"labels":[work["surface"]],"type":"WORK"}]
    return output_dict

labels_dict = convert_labels(people=people, places=places, works=works)


pbar = tqdm(total=len(paragraphs))
annotations = list()
for par in paragraphs:
    annotated_chars = set()
    _id = par["id"]
    text = par["text"]
    entities = labels_dict.get(_id, [])
    people = [item for item in entities if item["type"]=="PER"]
    places = [item for item in entities if item["type"] == "LOC"]
    works = [item for item in entities if item["type"] == "WORK"]

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
                    {"par_id":_id, "surface": surface, "start": start, "end": end, "identifier": loc["id"],
                     "type": "LOC",
                     "match":"exact", "pattern":None})
                annotated_chars.update(char_ranges)
    for per in people:
        pattern = per["labels"][0]
        for match in re.finditer(pattern+"\W", text):
            surface = match.group(0)[:-1]
            start = match.start()
            end = match.end()-1
            char_ranges = set((range(start, end+1)))
            # make sure no annotation overlaps
            if len(annotated_chars.intersection(char_ranges)) == 0:
                annotations.append(
                    {"par_id":_id, "surface": surface, "start": start, "end": end, "identifier": per["id"],
                     "type": "PER",
                     "match":"exact", "pattern":None})
                annotated_chars.update(char_ranges)
    for work in works:
        pattern = work["labels"][0]
        for match in re.finditer(pattern+"\W", text):
            surface = match.group(0)[:-1]
            start = match.start()
            end = match.end()-1
            char_ranges = set((range(start, end+1)))
            # make sure no annotation overlaps
            if len(annotated_chars.intersection(char_ranges)) == 0:
                annotations.append(
                    {"par_id":_id, "surface": surface, "start": start, "end": end, "identifier": work["id"],
                     "type": "WORK",
                     "match":"exact", "pattern":None})
                annotated_chars.update(char_ranges)
    pbar.update(1)
pbar.close()

annotations_no_work = [anno for anno in annotations if anno["type"]!="WORK"]

keys = annotations[0].keys()
with open("annotations.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(annotations)
f.close()


keys = annotations[0].keys()
with open("annotations_no_work.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(annotations_no_work)
f.close()