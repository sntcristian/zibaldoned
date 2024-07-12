from gliner import GLiNER
import csv
from tqdm import tqdm

model = GLiNER.from_pretrained("DeepMount00/GLiNER_ITA_LARGE")

labels = ["persona", "opera"]

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f:
    data = csv.DictReader(f)
    data = list(data)
f.close()

data = data[:4]
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
with open("../results/gliner_final/output_test.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(entita_nominate)

f.close()


# from gliner import GLiNER
#
# model = GLiNER.from_pretrained("DeepMount00/GLiNER_ITA_LARGE")
#
# text = """..."""
#
# labels = ["label1", "label2"]
#
# entities = model.predict_entities(text, labels)
#
# for entity in entities:
#     print(entity["text"], "=>", entity["label"])
