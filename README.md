## Extract Silver Annotations for Entity Linking from DigitalZibaldone

This repository contains data and source code used to extract silver annotations from the [DigitalZibaldone](https://digitalzibaldone.net/), a web platform that contains an XML/TEI editions of Giacomo Leopardi's *Zibaldone di pensieri*.

This project develops a simple Web Scraping strategy were entity annotations are extracted from the links in each 
paragraph. As an example, places referenced in the Zibaldone are linked to Wikidata. 

html
<p> 
<a href="https://www.wikidata.org/wiki/Q220">Rome</a> is the capital of <a href="https://www.wikidata.org/wiki/Q38">Italy</a>.
</p>

By applying this algorithm, we automatically collected **2,968 references to persons, locations and bibliographic works** 
from 1,028 paragraphs ([available here](data/)). 

## Named Entity Recognition Evaluation

Four Named Entity Recognition (NER) models were tested on the annotations of persons and locations from the aforementioned file:
* `LLaMa3.1-instruct-8B (Generative)`: Instruction-tuned LLM prompted in order to generate named entity annotations from text
* `LLaMa3.1-instruct-8B (Extractive)`: Instruction-tuned LLM prompted in order to extract a list of named entities from a text
* `GLiNER_ITA_BASE (Zero-shot)`: Pre-trained GliNER model trained on general-domain Italian for Universal Named Entity Recognition
* `GLiNER_ITA_BASE (Fine-tuned)`: Fine-tuned GliNER model trained on a [training portion](data/json_data/train.json) of Zibaldone
 

## Extract Silver Annotations for Entity Linking from DigitalZibaldone

This repository contains data and source code used to extract silver annotations from the [DigitalZibaldone](https://digitalzibaldone.net/), a web platform that contains an XML/TEI editions of Giacomo Leopardi's *Zibaldone di pensieri*.

This project develops a simple Web Scraping strategy were entity annotations are extracted from the links in each 
paragraph. As an example, places referenced in the Zibaldone are linked to Wikidata.

html
<p> 
<a href="https://www.wikidata.org/wiki/Q220">Rome</a> is the capital of <a href="https://www.wikidata.org/wiki/Q38">Italy</a>.
</p>

By applying this algorithm, we automatically collected **2,968 references to persons, locations and bibliographic works** 
from 1,028 paragraphs ([available here](data/)).

## Named Entity Recognition Evaluation

Four Named Entity Recognition (NER) models were tested on the annotations of persons and locations from the aforementioned file:
* `LLaMa3.1-instruct-8B (Generative)`: Instruction-tuned LLM prompted in order to generate named entity annotations from text.
* `LLaMa3.1-instruct-8B (Extractive)`: Instruction-tuned LLM prompted in order to extract a list of named entities from a text.
* `GLiNER_ITA_BASE (Zero-shot)`: Pre-trained GliNER model trained on general-domain Italian for Universal Named Entity Recognition.
* `GLiNER_ITA_BASE (Fine-tuned)`: Fine-tuned GliNER model trained on a [training portion](data/json_data/train.json) of Zibaldone.

### Exact Matching Results

| Metric             | LLaMa Generative | LLaMa Extractive | GliNER Zero-Shot | GLiNER Fine-Tuned |
|--------------------|------------------------|------------------------|------------------------|-------------------------|
| Precision MicroAvg  | 22.48                  | 37.06                  | 30.60                  | **75.15**                   |
| Recall MicroAvg     | 48.42                  | 29.06                  | 50.79                  | **63.74**                   |
| F1 MicroAvg         | 30.71                  | 32.58                  | 38.19                  | **68.98**                   |


### Fuzzy Matching Results

| Metric             | LLaMa Generative  | LLaMa Extractive | GliNER Zero-Shot | GLiNER Fine-Tuned |
|--------------------|------------------------|------------------------|------------------------|-------------------------|
| Precision MicroAvg  | 24.73                  | 44.07                  | 35.33                  | **82.40**                   |
| Recall MicroAvg     | 53.27                  | 34.55                  | 58.64                  | **69.90**                   |
| F1 MicroAvg         | 33.78                  | 38.74                  | 44.09                  | **75.64**                   |




## Entity Linking Evaluation

TO BE DONE

## References

* Basile, P., Musacchio, E., Polignano, M., Siciliani, L., Fiameni, G., & Semeraro, G. (2023). LLaMAntino: LLaMA 2 Models for Effective Text Generation in Italian Language (arXiv:2312.09993). arXiv. https://doi.org/10.48550/arXiv.2312.09993
* De Cao, N., Wu, L., Popat, K., Artetxe, M., Goyal, N., Plekhanov, M., Zettlemoyer, L., Cancedda, N., Riedel, S., & 
Petroni, F. (2022). Multilingual Autoregressive Entity Linking. Transactions of the Association for Computational Linguistics, 10, 274–290. https://doi.org/10.1162/tacl_a_00460
* Paccosi, T., & Palmero Aprosio, A. (2022). KIND: An Italian Multi-Domain Dataset for Named Entity Recognition. In N. Calzolari, F. Béchet, P. Blache, K. Choukri, C. Cieri, T. Declerck, S. Goggi, H. Isahara, B. Maegaard, J. Mariani, H. Mazo, J. Odijk, & S. Piperidis (A c. Di), Proceedings of the Thirteenth Language Resources and Evaluation Conference (pp. 501–507). European Language Resources Association. https://aclanthology.org/2022.lrec-1.52
* Pan, X., Zhang, B., May, J., Nothman, J., Knight, K., & Ji, H. (2017). Cross-lingual Name Tagging and Linking for 282 Languages. In R. Barzilay & M.-Y. Kan (A c. Di), Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) (pp. 1946–1958). Association for Computational Linguistics. https://doi.org/10.18653/v1/P17-1178
* Stoyanova, S. & Johnston, B. (Eds.), *Giacomo Leopardi's Zibaldone di pensieri: a digital research platform*. https://digitalzibaldone.net/