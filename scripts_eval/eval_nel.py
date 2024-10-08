import csv


def compute_match(type, entity1, entity2):
    start_pos1 = int(entity1["start"])
    end_pos1 = int(entity1["end"])
    start_pos2 = int(entity2["start_pos"])
    end_pos2 = int(entity2["end_pos"])
    if type == "exact":
        if start_pos1 == start_pos2 and end_pos1 == end_pos2:
            return True
        else:
            return False
    if type == "relaxed":
        if len(set(range(start_pos1, end_pos1)).intersection(set(range(start_pos2, end_pos2)))) > 0:
            return True
        else:
            return False


def eval_nel(path_data, path_results):
    with open(path_data + "annotations_no_work_23.csv", "r", encoding="utf-8") as f1:
        data = list(csv.DictReader(f1, delimiter=","))
    with open(path_results + "output.csv", "r", encoding="utf-8") as f2:
        model_result = list(csv.DictReader(f2, delimiter=","))

    tp = []
    fp = []
    fn = []
    matches = []

    for entity1 in data:
        id1 = entity1["par_id"]
        wb_id1 = entity1["identifier"]
        if wb_id1.startswith("viaf"):
            continue
        else:
            for entity2 in model_result:
                id2 = entity2["id"]
                wb_id2 = entity2["wb_id"]
                if wb_id2 == "NIL":
                    continue
                else:
                    if id2 == id1 and compute_match(type="relaxed", entity1=entity1,
                                                    entity2=entity2) == True and wb_id2 == wb_id1:
                        matches.append(entity1)
                        tp.append(entity2)

    for entity1 in data:
        if entity1 not in matches and entity1["identifier"].startswith("Q"):
            fn.append(entity1)

    for entity2 in model_result:
        if entity2 not in tp and entity2["wb_id"].startswith("Q"):
            fp.append(entity2)

    precision = len(tp) / (len(tp) + len(fp))
    recall = len(tp) / (len(tp) + len(fn))
    f1 = (2 * precision * recall) / (precision + recall)
    with open(path_results + "results_baseline.txt", "w") as output:
        output.write("True Positives: " + str(len(tp)) + "\n\n")
        output.write("False Positives: " + str(len(fp)) + "\n\n")
        output.write("False Negatives: " + str(len(fn)) + "\n\n")
        output.write("Precision: " + str(precision) + "\n\n")
        output.write("Recall: " + str(recall) + "\n\n")
        output.write("F1: " + str(f1) + "\n\n")

    p_keys = matches[0].keys()
    fp_keys = fp[0].keys()
    n_keys = fn[0].keys()

    tp_file = open(path_results + "tp_baseline.csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(tp_file, p_keys)
    dict_writer.writeheader()
    dict_writer.writerows(matches)
    tp_file.close()

    fp_file = open(path_results + "fp_baseline.csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(fp_file, fp_keys)
    dict_writer.writeheader()
    dict_writer.writerows(fp)
    fp_file.close()

    fn_file = open(path_results + "fn_baseline.csv", "w", encoding="utf-8")
    dict_writer = csv.DictWriter(fn_file, n_keys)
    dict_writer.writeheader()
    dict_writer.writerows(fn)
    fn_file.close()


eval_nel(path_data="../data/", path_results="../results/mgenre_el/")
