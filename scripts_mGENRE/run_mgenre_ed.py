import requests
import re
import csv
import json
from tqdm import tqdm
import pickle
from genre.trie import Trie, MarisaTrie
from genre.fairseq_model import mGENRE


with open("../data/paragraphs_test.csv", "r", encoding="utf-8") as f1:
    paragraphs = csv.DictReader(f1)
    paragraphs = list(paragraphs)
    paragraphs = paragraphs[:4]

with open("../data/annotations_test.csv", "r", encoding="utf-8") as f2:
    all_spans = csv.DictReader(f2)
    all_spans = list(all_spans)

# data to have
with open("../GENRE_models/lang_title2wikidataID-normalized_with_redirect.pkl", "rb") as f:
   lang_title2wikidataID = pickle.load(f)

with open("../GENRE_models/titles_lang_all105_marisa_trie_with_redirect.pkl", "rb") as f2:
    trie = pickle.load(f2)

model = mGENRE.from_pretrained("../GENRE_models/fairseq_model_ed").eval()

output = []

pbar = tqdm(total=len(paragraphs))
for item in paragraphs:
    text = item["text"]
    data_id = item["id"]
    entities = []
    begin = []
    end = []
    labels = []
    sentences = []
    wb_ids = []
    scores = []
    surface_forms = [(int(ent["start"]), int(ent["end"]), ent["type"]) for ent in all_spans \
                     if ent["par_id"] == data_id]
    for ent in surface_forms:
        start_pos = ent[0]
        end_pos = ent[1]
        if start_pos >= 500:
            history_start = start_pos - 500
        else:
            history_start = 0
        if end_pos + 500 <= len(text):
            future_end = end_pos + 500
        else:
            future_end = len(text)
        label = ent[2]
        mention = text[history_start:start_pos] + "[START] " + text[start_pos:end_pos] + " [END]" + text[end_pos:future_end]
        begin.append(start_pos)
        end.append(end_pos)
        labels.append(label)
        sentences.append(mention)
    results = model.sample(
       sentences,
       prefix_allowed_tokens_fn=lambda batch_id, sent: [
           e for e in trie.get(sent.tolist()) if e < len(model.task.target_dictionary)
       ],
       text_to_id=lambda x: max(lang_title2wikidataID[tuple(reversed(x.split(" >> ")))], key=lambda y: int(y[1:])),
       marginalize=True,
    )
    # Example output =    [[{'id': 'Q937',
    #    'texts': ['Albert Einstein >> it','Alberto Einstein >> it',    'Einstein >> it'],
    #    'scores': tensor([-0.0808, -1.4619, -1.5765]), 'score': tensor(-0.0884)}]]

    for result in results:
       print(result)
       candidate = result[0]
       name = candidate["texts"][0]
       score = candidate["score"].item()
       wb_id = candidate["id"]
       entities.append(name)
       scores.append(score)
       wb_ids.append(wb_id)

    labels = list(zip(begin, end, labels, scores, entities, wb_ids))
    for start_pos, end_pos, label, score, alias, wb_ids in labels:
       output.append(
           {
               "id": item["id"],
               "start_pos": start_pos,
               "end_pos": end_pos,
               "type": label,
               "alias": alias,
               "wb_id": wb_ids,
               "score": score
           }
       )
    pbar.update(1)
pbar.close()

keys = output[0].keys()

a_file = open("../results/mgenre_ed/output.csv", "w")
dict_writer = csv.DictWriter(a_file, keys)
dict_writer.writeheader()
dict_writer.writerows(output)
a_file.close()
