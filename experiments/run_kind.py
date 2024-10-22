import stanza
import csv
from tqdm import tqdm
import os

#load NER model
stanza.download('it')
nlp = stanza.Pipeline('it', processors='tokenize,ner')

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f:
    data = csv.DictReader(f)
    data = list(data)
f.close()

pbar = tqdm(total=len(data))
entita_nominate = []
for row in data:
    doc_id = row["id"]
    doc_txt = row["text"]
    doc = nlp(doc_txt)
    for sent in doc.sentences:
        for entita in sent.ents:
            if entita.type != "ORG":
                entita_nominate.append({
                    "id":doc_id,
                    "surface_form":entita.text, 
                    "start_pos":entita.start_char, 
                    "end_pos":entita.end_char,
                    "type":entita.type})
    pbar.update(1)
pbar.close()


if not os.path.exists("../results/kind"):
    os.makedirs("../results/kind")

keys = entita_nominate[0].keys()
with open("../results/kind/output.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(entita_nominate)

f.close()