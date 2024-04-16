import csv
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# OPTIONAL: load the prefix tree (trie), you need to additionally download
# https://huggingface.co/facebook/mgenre-wiki/blob/main/trie.py and
# https://huggingface.co/facebook/mgenre-wiki/blob/main/titles_lang_all105_trie_with_redirect.pkl
# that is fast but memory inefficient prefix tree (trie) -- it is implemented with nested python `dict`
# NOTE: loading this map may take up to 10 minutes and occupy a lot of RAM!
# import pickle
# from trie import Trie
# with open("titles_lang_all105_marisa_trie_with_redirect.pkl", "rb") as f:
#     trie = Trie.load_from_dict(pickle.load(f))

# or a memory efficient but a bit slower prefix tree (trie) -- it is implemented with `marisa_trie` from
# https://huggingface.co/facebook/mgenre-wiki/blob/main/titles_lang_all105_marisa_trie_with_redirect.pkl
# from genre.trie import MarisaTrie
# with open("titles_lang_all105_marisa_trie_with_redirect.pkl", "rb") as f:
#     trie = pickle.load(f)

with open("../data/paragraphs.csv", "r", encoding="utf-8") as f1:
    paragraphs = csv.DictReader(f1)
    paragraphs = list(paragraphs)
    paragraphs = paragraphs[:4]

with open("../data/annotations_23.csv", "r", encoding="utf-8") as f2:
    all_spans = csv.DictReader(f2)
    all_spans = list(all_spans)

tokenizer = AutoTokenizer.from_pretrained("facebook/mgenre-wiki")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mgenre-wiki").eval()

output = []
pbar = tqdm(total=len(paragraphs))

for row in paragraphs:
    _id = row["id"]
    text = row["text"]
    spans = [span for span in all_spans if span["par_id"]==_id]
    for span in spans:
        start = int(span["start"])
        end = int(span["end"])
        annotated_text = [text[:start]+"[START] "+\
        text[start:end]+" [END]"+text[end:]]
        outputs = model.generate(
            **tokenizer(annotated_text, return_tensors="pt"),
            num_beams=5,
            num_return_sequences=5,
            # OPTIONAL: use constrained beam search
            # prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
        )
        answer = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        first_candidate = answer[0]
        title_lang = first_candidate.split(" >> ")
        title = title_lang[0]
        lang = title_lang[1]
        output.append({"par_id":_id, "start":start, "end":end, "wikititle":title, "lang":lang})
    pbar.update(1)

keys = output[0].keys()
with open("../results/mgenre_ed/output.csv", "w", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)

f.close()