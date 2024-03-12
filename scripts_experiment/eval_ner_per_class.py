import csv



def eval_ner(data, model_result, type):
    tp = []  # true positive
    fp = []  # false positive
    fn = []  # false negative
    matches = []  # matched annotations
    data = [row for row in data if row["type"]==type]
    model_result = [row for row in model_result if row["type"]==type]
    for entity1 in data:
        id1 = entity1["par_id"]
        start_pos1 = int(entity1["start"])
        end_pos1 = int(entity1["end"])
        ent_type1 = entity1["type"]
        for entity2 in model_result:
            id2 = entity2["id"]
            start_pos2 = int(entity2["start_pos"])
            end_pos2 = int(entity2["end_pos"])
            ent_type2 = entity2["type"]
            char_intersection = len(set(range(start_pos1, end_pos1)).intersection(set(range(start_pos2, end_pos2))))
            if id2 == id1 and char_intersection > 0 and ent_type1==ent_type2:
                matches.append(entity1)
                tp.append(entity2)
                break

    for entity1 in data:
        if entity1 not in matches:
            fn.append(entity1)

    for entity2 in model_result:
        if entity2 not in tp:
            fp.append(entity2)

    precision = len(matches) / (len(matches) + len(fp))
    recall = len(matches) / (len(matches) + len(fn))
    f1 = (2 * precision * recall) / (precision + recall)

    with open("../results/kind/results_"+type+".txt", "w") as output:
        output.write("True Positives: " + str(len(tp)) + "\n\n")
        output.write("False Positives: " + str(len(fp)) + "\n\n")
        output.write("False Negatives: " + str(len(fn)) + "\n\n")
        output.write("Precision: " + str(precision) + "\n\n")
        output.write("Recall: " + str(recall) + "\n\n")
        output.write("F1: " + str(f1) + "\n\n")

    p_keys = matches[0].keys()
    n_keys = fn[0].keys()
    fp_keys = fp[0].keys()

    tp_file = open("../results/kind/tp_ner"+type+".csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(tp_file, p_keys)
    dict_writer.writeheader()
    dict_writer.writerows(matches)
    tp_file.close()

    fp_file = open("../results/kind/fp_ner"+type+".csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(fp_file, fp_keys)
    dict_writer.writeheader()
    dict_writer.writerows(fp)
    fp_file.close()

    fn_file = open("../results/kind/fn_ner"+type+".csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(fn_file, n_keys)
    dict_writer.writeheader()
    dict_writer.writerows(fn)
    fn_file.close()


with open("../scripts_extraction/annotations_23.csv", "r", encoding="utf-8") as f2:
    data = csv.DictReader(f2)
    data = list(data)
f2.close()

with open("../results/kind/output.csv", "r", encoding="utf-8") as f3:
    model_result = csv.DictReader(f3)
    model_result = list(model_result)
f3.close()

eval_ner(data, model_result, "LOC")