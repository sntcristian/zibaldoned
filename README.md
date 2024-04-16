# ZibaldonED

## Extract Silver Annotations for Entity Disambiguation from DigitalZibaldone

This repository contains data and source code used to extract silver annotations from the [DigitalZibaldone](https://digitalzibaldone.net/), a web platform that contains an XML/TEI editions of Giacomo Leopardi's *Zibaldone 
di pensieri*.

This project develops a simple Web Scraping strategy were entity annotations are extracted from the links in each 
paragraph. As an example, places referenced in the Zibaldone are linked to Wikidata. 

```html
<p> 
<a href="https://www.wikidata.org/wiki/Q220">Rome</a> is the capital of <a href="https://www.wikidata.
org/wiki/Q38">Italy</a>.
</p>
```
The result of the annotation process from the paragraphs in pp.2700-3000 is available in  [this file](data/annotations_23.csv). 

## Experiments

Three Named Entity Recognition (NER) models were tested on the annotations from the aforementioned file:
* KIND: Transformer Model trained on the dataset [KIND](https://github.com/dhfbk/KIND)
* Wikineural: Transformer Model trained on the Italian portion of [Wikineural](https://github.com/Babelscape/wikineural)
* LLaMantino-16B: Encoder-Decoder LLM for Italian based on LLaMa 2 and trained via Instruction-Tuning on [KIND](https://github.com/dhfbk/KIND)

Results are available in the [results](./results) folder.




