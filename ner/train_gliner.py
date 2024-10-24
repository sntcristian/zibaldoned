import json
import random
import os
import torch
from gliner import GLiNERConfig, GLiNER
from gliner.training import Trainer, TrainingArguments
from gliner.data_processing.collator import DataCollatorWithPadding, DataCollator
from gliner.utils import load_config_as_namespace
from gliner.data_processing import WordsSplitter, GLiNERDataset

train_path = "../data/json_data/train.json"

with open(train_path, "r") as f:
    data = json.load(f)

print('Dataset size:', len(data))

random.shuffle(data)
print('Dataset is shuffled...')

train_dataset = data[:int(len(data)*0.9)]
test_dataset = data[int(len(data)*0.9):]

print('Dataset is splitted...')

os.environ["TOKENIZERS_PARALLELISM"] = "true"

device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')

model = GLiNER.from_pretrained("DeepMount00/GLiNER_ITA_BASE")
data_collator = DataCollator(model.config, data_processor=model.data_processor, prepare_labels=True)
model.to(device)
print("done")

num_steps = 700
batch_size = 4
data_size = len(train_dataset)
num_batches = data_size // batch_size
num_epochs = max(1, num_steps // num_batches)
print("Epochs: ", num_epochs)

training_args = TrainingArguments(
    output_dir="../models/gliner_base_b4_e4",
    learning_rate=5e-6,
    weight_decay=0.01,
    others_lr=1e-5,
    others_weight_decay=0.01,
    lr_scheduler_type="linear", #cosine
    warmup_ratio=0.1,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=num_epochs,
    evaluation_strategy="steps",
    save_strategy="no",
    dataloader_num_workers = 0,
    use_cpu = False,
    report_to="none",
    )

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=model.data_processor.transformer_tokenizer,
    data_collator=data_collator,
)

trainer.train()

if not os.path.exists("../models"):
    os.makedirs("../models")

trainer.model.save_pretrained("../models/gliner_base_b4_e4")

trained_model = GLiNER.from_pretrained("../models/gliner_base_b4_e4", load_tokenizer=True)


labels = ["persona", "opera", "luogo"]


passo_1 = """
Dante Alighieri, uno dei poeti più celebri della storia, nacque a Firenze nel 1265. Firenze, all'epoca, era un centro vibrante di cultura e politica, profondamente influenzato dalle lotte tra Guelfi e Ghibellini. Dante stesso fu coinvolto in queste fazioni, esperienza che avrebbe segnato profondamente la sua vita e la sua opera. La sua opera più famosa, la Divina Commedia, rappresenta un viaggio allegorico attraverso l'Inferno, il Purgatorio e il Paradiso, un'opera che non solo riflette le sue convinzioni religiose e politiche, ma anche una critica sociale dell'epoca. Firenze, con i suoi vicoli stretti, le sue chiese gotiche e i palazzi medievali, si riflette in molte delle descrizioni di luoghi all'interno della Commedia. Tuttavia, Firenze fu anche la città da cui Dante fu esiliato nel 1302, un'esperienza che lo portò a vagare per l'Italia, in cerca di protezione presso varie corti. L'amarezza per questo esilio traspare in molti dei suoi scritti, dove spesso esprime il suo dolore per la lontananza dalla città natale.
"""

passo_2 = "Pisa, una delle repubbliche marinare più importanti d'Italia, è anche famosa per essere la città natale di Galileo Galilei. Nato nel 1564, Galileo è considerato il padre della scienza moderna grazie ai suoi contributi rivoluzionari alla fisica e all'astronomia. È a Pisa che Galileo, secondo la leggenda, avrebbe condotto il famoso esperimento dalla Torre Pendente, dimostrando che la velocità di caduta di un oggetto non dipende dal suo peso. Pisa, con la sua iconica torre e le università prestigiose, fu un luogo cruciale per la formazione intellettuale di Galileo. L'opera più influente di Galileo, il Dialogo sopra i due massimi sistemi del mondo, fu pubblicata nel 1632 e rappresentò un attacco diretto al sistema tolemaico a favore del modello copernicano. Questa opera gli costò il processo per eresia da parte dell'Inquisizione romana e la successiva condanna agli arresti domiciliari. Pisa, nel contesto della vita di Galileo, rappresenta non solo il punto di partenza della sua carriera scientifica, ma anche un simbolo del conflitto tra scienza e autorità religiosa."

passo_3 = """
Milano, il cuore economico e culturale dell'Italia, ha svolto un ruolo centrale nella vita e nell'opera di Alessandro Manzoni. Nato nel 1785, Manzoni è uno dei più grandi scrittori italiani del XIX secolo, famoso soprattutto per il suo romanzo I Promessi Sposi. Quest'opera, ambientata in Lombardia durante il XVII secolo, è un ritratto vivido della vita sociale e politica dell'epoca, ma anche un'allegoria delle sofferenze e delle speranze umane. Milano, con i suoi salotti letterari e il fervore risorgimentale, fu il luogo dove Manzoni trascorse gran parte della sua vita e trovò l'ispirazione per le sue opere. La città stessa compare ne I Promessi Sposi come uno dei luoghi chiave della narrazione, soprattutto nel contesto della peste che colpì la città nel 1630. Manzoni, influenzato dalle idee romantiche e dal clima culturale milanese, riuscì a coniugare nelle sue opere una profonda introspezione psicologica con un acuto senso della storia.
"""

passo_4 = """
Assisi, una piccola città dell'Umbria, è celebre per essere la patria di San Francesco e per le meraviglie artistiche che vi si trovano, in particolare gli affreschi di Giotto. Nato nel 1267, Giotto di Bondone è considerato il precursore del Rinascimento italiano, e il suo lavoro nella Basilica di San Francesco ad Assisi segna una svolta nella storia dell'arte. Gli affreschi della Basilica, che illustrano la vita di San Francesco, sono considerati tra le opere più innovative del periodo, grazie all'uso rivoluzionario della prospettiva e della rappresentazione realistica delle emozioni. Assisi, con la sua atmosfera spirituale e la sua bellezza naturale, ha ispirato Giotto a creare un'opera che ancora oggi è considerata un capolavoro dell'arte occidentale. La Basilica stessa è diventata un luogo di pellegrinaggio non solo per i devoti, ma anche per gli appassionati d'arte che vengono a contemplare l'opera di uno degli artisti più influenti della storia.
"""

passo_5 = """
Leonardo da Vinci, una delle menti più brillanti della storia, trascorse un periodo significativo della sua vita a Milano, una città che ha fortemente influenzato il suo lavoro. Nato nel 1452 in Toscana, Leonardo si trasferì a Milano nel 1482, dove lavorò sotto la protezione di Ludovico Sforza, il Duca di Milano. Durante il suo soggiorno milanese, Leonardo creò alcune delle sue opere più celebri, tra cui L'Ultima Cena, dipinta nel refettorio del convento di Santa Maria delle Grazie. Milano, con la sua ricca vita culturale e intellettuale, offrì a Leonardo un ambiente ideale per sviluppare le sue molteplici abilità, non solo come pittore, ma anche come ingegnere, scienziato e inventore. L'Ultima Cena, in particolare, è considerata una delle opere più influenti della storia dell'arte, sia per la sua composizione innovativa che per l'uso pionieristico della prospettiva e della luce. Milano e Leonardo da Vinci sono oggi indissolubilmente legati, con la città che continua a celebrare l'eredità del maestro attraverso musei, mostre e eventi dedicati alla sua opera.
"""

print("Passo 1:")
entities = trained_model.predict_entities(passo_1, labels, threshold=0.5)

for entity in entities:
    print(entity["text"], "=>", entity["label"])

print("Passo 2:")
entities = trained_model.predict_entities(passo_2, labels, threshold=0.5)

for entity in entities:
    print(entity["text"], "=>", entity["label"])

print("Passo 3:")
entities = trained_model.predict_entities(passo_3, labels, threshold=0.5)

for entity in entities:
    print(entity["text"], "=>", entity["label"])

print("Passo 4:")
entities = trained_model.predict_entities(passo_4, labels, threshold=0.5)

for entity in entities:
    print(entity["text"], "=>", entity["label"])

print("Passo 5:")
entities = trained_model.predict_entities(passo_5, labels, threshold=0.5)

for entity in entities:
    print(entity["text"], "=>", entity["label"])