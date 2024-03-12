# ZibaldonED

## Extract Silver Annotations for Entity Disambiguation from DigitalZibaldone

This repository contains data and source code used to extract silver annotations from the [DigitalZibaldone](https://digitalzibaldone.net/), a web platform that contains an XML/TEI editions of Giacomo Leopardi's *Zibaldone 
di pensieri*.

This project develops three strategies:

1. Scraping links to places in Wikidata which are directly provided in Zibaldone's text in the following form

```html
<p> 
<a href="/paragraph/Q220">Rome</a> is the capital of <a href="/paragraph/Q38">Italy</a>
</p>
```
2. Scraping the *Index of People* from [this page](https://digitalzibaldone.net/index/people), which contains the list 
   of names along with the paragraphs in which are referenced and their Wikidata identifier
   1. This index is used to create a dictionary of spelling variations to find people in Zibaldone's text by exploiting 
      labels 
      and aliases in Wikidata 
3. Match names of people extracted in the previous step to portions of Zibaldone's text by using exact string 
   matching and a combination of POS-tagging with levenshtein distance in order to find surface forms in the text which 
   are 
   not present in our dictionary of names
   1. Source code is available [here](scripts_extraction/annotate_paragraphs.py)

## Result

The result of the annotation process is available in  [this file](scripts_extraction/annotations.csv). 
Documentation on how to use source code coming soon.
