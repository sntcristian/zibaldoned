import json
from nameparser import HumanName


json_f = open("people_labels.json", "r", encoding="utf-8")
data = json.load(json_f)
json_f.close()
output = list()

for item in data:
    name = HumanName(item["it"]).as_dict(False)
    tokens = [value for key, value in name.items()]
    item["tokens"]=tokens
    output.append(item)

out_f = open("people_gazetteer.json", "w", encoding="utf-8")
json.dump(output, out_f, indent=4, ensure_ascii=False)