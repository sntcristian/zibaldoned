import csv
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
import re
import json
from tqdm import tqdm
import gc
import torch


with open("./test.csv", "r", encoding="utf-8") as f:
    data = csv.DictReader(f)
    data = list(data)
data = data[:10]

model_id = "swap-uniba/LLaMAntino-2-13b-hf-evalita-ITA"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, load_in_8bit=True, device_map="auto")


pbar = tqdm(total=len(data))
output = list()
for row in data:
    try:
        with torch.no_grad():
            instruction_text = """Elenca le menzioni di entità presenti nel testo in input, indicandone il tipo: [PER] (persona), [LOC] (luogo), [ORG] (organizzazione). Se non ci sono entità, resituisci: 'Nessuna menzione'"""
            input_text = row["text"]
            prompt = "Di seguito è riportata un'istruzione che descrive un'attività, accompagnata da un input che aggiunge ulteriore informazione. " \
                     f"Scrivi una risposta che completi adeguatamente la richiesta.\n\n" \
                     f"### Istruzione:\n{instruction_text}\n\n" \
                     f"### Input:\n{input_text}\n\n" \
                     f"### Risposta:\n"

            input_ids = tokenizer(prompt, return_tensors="pt").input_ids
            outputs = model.generate(input_ids=input_ids)

            answer = \
            tokenizer.batch_decode(outputs.detach().cpu().numpy()[:, input_ids.shape[1]:], skip_special_tokens=True)[0]
            del outputs
            del input_ids
            gc.collect()
            torch.cuda.empty_cache()
            used_patterns = set()
            if "nessuna menzione" in answer.lower():
                pass
            else:
                candidates = answer.split("[")
                for candidate in candidates:
                    if len(candidate.split("]"))>1:
                        surface = candidate.split("]")[1].strip()
                        tag = candidate.split("]")[0].strip()
                        if len(surface)>0 and surface not in used_patterns and tag!="ORG":
                            for match in re.finditer(surface+"\W", input_text):
                                start_pos = match.start()
                                end_pos = match.end()-1
                                output.append({"id":row["id"],"surface": surface, "tag": tag, "start_pos":start_pos, "end_pos": end_pos, "left_context":input_text[0:start_pos], "right_context":input_text[end_pos:]})
                            used_patterns.add(surface)
        pbar.update(1)
    except Exception as e:
        print("Exception: ", e)
        pbar.update(1)
        continue

if len(output)>0:
    keys = output[0].keys()
    with open("../results/llamantino/output.csv", "w", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(output)
