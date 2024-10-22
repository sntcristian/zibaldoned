import csv
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import os

tokenizer = AutoTokenizer.from_pretrained("nickprock/bert-italian-finetuned-ner")
tagger = AutoModelForTokenClassification.from_pretrained("nickprock/bert-italian-finetuned-ner")
nlp = pipeline("ner", model=tagger, tokenizer=tokenizer, aggregation_strategy="simple")

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f:
    data = csv.DictReader(f)
    data = list(data)


data = data
pbar = tqdm(total=len(data))
output = list()
for row in data:
    doc_id = row["id"]
    text = row["text"]
    ner = nlp(text)
    for ent in ner:
        if ent["entity_group"]=="ORG" or ent["entity_group"]=="MISC":
            continue
        else:
            if len(output)==0 or output[-1]["end_pos"]!=ent["start"]:
                output.append({
                        "id":doc_id,
                        "start_pos":ent["start"],
                        "end_pos":ent["end"],
                        "surface":ent["word"],
                        "type":ent["entity_group"],
                        "score":ent["score"]
                    })
            else:
                output[-1]={
                        "id":doc_id,
                        "start_pos":output[-1]["start_pos"],
                        "end_pos":ent["end"],
                        "surface":output[-1]["surface"]+ent["word"][2:],
                        "type":ent["entity_group"],
                        "score":ent["score"]
                        }
    pbar.update(1)
pbar.close()

if not os.path.exists("../results/wikiann"):
    os.makedirs("../results/wikiann")

keys = output[0].keys()
a_file = open("../results/wikiann/output.csv", "w", encoding="utf-8")
dict_writer = csv.DictWriter(a_file, keys)
dict_writer.writeheader()
dict_writer.writerows(output)
a_file.close()