from gliner import GLiNER
import csv
from tqdm import tqdm

model = GLiNER.from_pretrained("DeepMount00/universal_ner_ita", token="put token for gated model")

labels = ["persona", "luogo"]

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f:
    data = csv.DictReader(f)
    data = list(data)
f.close()

pbar = tqdm(total=len(data))
entita_nominate = []
for row in data:
    doc_id = row["id"]
    doc_txt = row["text"]
    entities = model.predict_entities(doc_txt, labels)
    for entity in entities:
        entry = {"id":doc_id,
                 "surface_form":entity["text"],
                 "start_pos":entity["start"],
                 "end_pos":entity["end"],
                 "type":entity["label"]}
        entita_nominate.append(entry)
    pbar.update(1)
pbar.close()

keys = entita_nominate[0].keys()
with open("../results/gliner_final/output.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(entita_nominate)

f.close()
