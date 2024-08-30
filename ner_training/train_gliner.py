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
    output_dir="/kaggle/working/z_gliner",
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

trainer.model.save_pretrained("../models/gliner_base_b4_e4")

trained_model = GLiNER.from_pretrained("../models/gliner_base_b4_e4", load_tokenizer=True)

text = """
Aristotele diceva più essere le cose che le parole * : e il Perticari loc. cit. p. 187-8. spiega ed applica questa sentenza alla necessità di far {sempre} nuovi vocaboli per le nuove {cognizioni} e idee. (24. Maggio 1823.).
"""

# Labels for entity prediction
labels = ["persona", "opera", "luogo"] # for v2.1 use capital case for better performance

# Perform entity prediction
entities = trained_model.predict_entities(text, labels, threshold=0.5)

# Display predicted entities and their labels
for entity in entities:
    print(entity["text"], "=>", entity["label"])

# Deve produrre come output:

# Aristotele => persona
# Perticari => persona