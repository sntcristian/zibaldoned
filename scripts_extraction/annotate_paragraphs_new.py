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


paragraphs=paragraphs[:30]

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


#load POS-tag model (useful later to match strings with levenshtein distance)
stanza.download('it')
nlp = stanza.Pipeline('it', processors='tokenize,pos')

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


    doc = nlp(text)

    # Extract and return POS tagged tokens
    pos_tagged_text = []
    for sentence in doc.sentences:
        for token in sentence.tokens:
            pos_tagged_text.append({
                'text': token.text,
                'pos_tag': token.words[0].upos,
                'start_pos': token.start_char,
                'end_pos': token.end_char
            })
    ngrams = list()
    trigrams = list()
    bigrams = list()
    unigrams = list()
    processed_tokens_idx = -1
    for idx, token in enumerate(pos_tagged_text):
        if idx > processed_tokens_idx:
            if token['pos_tag']=="PROPN":
                unigram = {"par_id":_id, "surface":token["text"], "start":token["start_pos"], "end":token["end_pos"]}
                unigrams.append(unigram)
                processed_tokens_idx = idx
                if idx < len(pos_tagged_text)-1 and pos_tagged_text[idx+1]['pos_tag'] == "PROPN":
                    bigram = {"par_id":_id, "surface":token["text"]+" "+pos_tagged_text[idx+1]['text'], "start":token["start_pos"], "end":pos_tagged_text[idx+1]["end_pos"]}
                    bigrams.append(bigram)
                    unigram = {"par_id":_id, "surface":pos_tagged_text[idx+1]['text'], "start":pos_tagged_text[idx+1]["start_pos"], "end":pos_tagged_text[idx+1]["end_pos"]}
                    unigrams.append(unigram)
                    processed_tokens_idx = idx+1
                    if idx < len(pos_tagged_text)-2 and pos_tagged_text[idx+2]['pos_tag'] == "PROPN":
                        trigram = {"par_id":_id, "surface":token["text"]+" "+pos_tagged_text[idx+1]['text']+" "+pos_tagged_text[idx+2]['text'], "start":token["start_pos"], "end":pos_tagged_text[idx+2]["end_pos"]}
                        trigrams.append(trigram)
                        unigram = {"par_id":_id, "surface":pos_tagged_text[idx+2]['text'], "start":pos_tagged_text[idx+2]["start_pos"], "end":pos_tagged_text[idx+2]["end_pos"]}
                        unigrams.append(unigram)
                        processed_tokens_idx = idx+2
                    elif idx<len(pos_tagged_text)-3 and pos_tagged_text[idx+2]['pos_tag'] == "ADP" and pos_tagged_text[idx+3]['pos_tag'] == "PROPN":
                        ngram = {"par_id":_id, "surface":token["text"]+" "+pos_tagged_text[idx+1]['text']+" "+pos_tagged_text[idx+2]['text']+" "+pos_tagged_text[idx+3]['text'], "start":token["start_pos"], "end":pos_tagged_text[idx+3]["end_pos"]}
                        ngrams.append(ngram)
                        processed_tokens_idx = idx+2
                elif idx<len(pos_tagged_text)-2 and pos_tagged_text[idx+1]['pos_tag'] == "ADP" and pos_tagged_text[idx+2]['pos_tag'] == "PROPN":
                    trigram = {"par_id":_id, "surface":token["text"]+" "+pos_tagged_text[idx+1]['text']+" "+pos_tagged_text[idx+2]['text'], "start":token["start_pos"], "end":pos_tagged_text[idx+2]["end_pos"]}
                    trigrams.append(trigram)
                    processed_tokens_idx = idx+1


    for per in persons:
        patterns = per["labels"]
        sorted_patterns = sorted(patterns, key=lambda x: len(x), reverse=True)
        for pattern in sorted_patterns:
            for ngram in ngrams:
                surface = ngram["surface"]
                distanza = Levenshtein.distance(pattern, surface)
                if distanza == 4 and len(pattern)>7:
                    start = ngram["start"]
                    end = ngram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                             "type": "PER",
                             "match": "levenshtein", "pattern": pattern})
                        annotated_chars.update(char_ranges)
                elif distanza == 3 and len(pattern)>5:
                    start = ngram["start"]
                    end = ngram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                elif distanza <= 2:
                    start = ngram["start"]
                    end = ngram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
            for trigram in trigrams:
                surface = trigram["surface"]
                distanza = Levenshtein.distance(pattern, surface)
                if distanza == 4 and len(pattern)>7:
                    start = trigram["start"]
                    end = trigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                             "type": "PER",
                             "match": "levenshtein", "pattern": pattern})
                        annotated_chars.update(char_ranges)
                elif distanza == 3 and len(pattern)>5:
                    start = trigram["start"]
                    end = trigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                elif distanza <= 2:
                    start = trigram["start"]
                    end = trigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
            for bigram in bigrams:
                surface = bigram["surface"]
                distanza = Levenshtein.distance(pattern, surface)
                if distanza == 4 and len(pattern)>7:
                    start = bigram["start"]
                    end = bigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                             "type": "PER",
                             "match": "levenshtein", "pattern": pattern})
                        annotated_chars.update(char_ranges)
                elif distanza == 3 and len(pattern)>5:
                    start = bigram["start"]
                    end = bigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                elif distanza <= 2:
                    start = bigram["start"]
                    end = bigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
            for unigram in unigrams:
                surface = unigram["surface"]
                distanza = Levenshtein.distance(pattern, surface)
                if distanza == 4 and len(pattern)>7:
                    start = unigram["start"]
                    end = unigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id": _id, "surface": surface, "start": start, "end": end, "wikidata": per["id"],
                             "type": "PER",
                             "match": "levenshtein", "pattern": pattern})
                        annotated_chars.update(char_ranges)
                elif distanza == 3 and len(pattern)>5:
                    start = unigram["start"]
                    end = unigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
                elif distanza <= 2:
                    start = unigram["start"]
                    end = unigram["end"]
                    char_ranges = set((range(start, end + 1)))
                    if len(annotated_chars.intersection(char_ranges)) == 0:
                        annotations.append(
                            {"par_id":_id, "surface": surface, "start": start, "end": end, "wikidata": per["id"], "type": "PER",
                             "match":"levenshtein", "pattern":pattern})
                        annotated_chars.update(char_ranges)
    pbar.update(1)
pbar.close()

leves = [row for row in annotations if row["match"]=="levenshtein"]
print(leves)
            
