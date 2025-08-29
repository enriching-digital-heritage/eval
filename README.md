# Evaluation software and results

Software and results of evaluations in the Lorentz workshop [Enriching Digital Heritage](https://www.lorentzcenter.nl/enriching-digital-heritage-with-llms-and-linked-open-data.html). Results of the workshop are collected at the [Research Software Directory](https://research-software-directory.org/projects/enriching-digital-heritage-with-llms-and-lod).

## Evaluation results

### Evaluation data collections

| Task | Data source | Language | Size | Persons | Locations | Topic |
| ---- | ----------- | -------- | ---- | ------- | --------- | ----- |
| Recognition &nbsp; | British Museum | English | 100 texts | 115 | 47 | European Renaissance art |
| Recognition | Egyptian Museum | English | 100 texts | 177 | 91 | Ancient Egypt |
| Disambiguation | British Museum | English | 100 texts | 106(+9) | 44(+3) | European Renaissance art |

The British Museum disambiguation dataset contains as many entities as the recognition dataset but for 12 entities (9 PER/3 LOC) there are no links available

### Systems performance

#### Recognition: British Museum data

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | NameTag 3 | 12.4 sec | 85.3% | 80.9% | 83.0 | 75.0% | 70.2% | 72.5 |
| 2. | Spacy (trf) + | 2.3 sec | 75.9% | 71.3% | 73.5 | 54.2% | 55.3% | 54.7 |
| 3. | Spacy (trf) | 2.4 sec | 75.9% | 71.3% | 73.5 | 53.7% | 46.8% | 50.0 |
| 4. | gpt-oss 20b | 30 min 52 sec | 83.3% | 65.2% | 73.1 | 57.1% | 34.0% | 42.6 |
| 5. | Llama 3.3 | &nbsp; 28 min 33 sec | 67.1% | 49.6% | 57.0 | 41.2% | 29.8% | 34.6 |
| 6. | Dandelion | 12.5 sec | 78.3% | 31.3% | 44.7 | 74.1% | 42.6% | 54.1 |

The :P-related stats concern Person labels while the :L-related stats concern Location labels

"Spacy (trf) +" is "Spacy (trf)" with an additional list of 349 locations provided by Gethin

#### Recognition: Egyptian Museum data

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | gpt-oss 20b | 1 hr 2 min 9 sec | 90.5% | 96.6% | 93.2 | 58.1% | 86.8% | 69.6 |
| 2. | Llama 3.3 | 38 min 12 sec | 81.9% | 92.1% | 86.7 | 46.6% | 82.4% | 59.5 |
| 3. | Spacy (trf) | 2.6 sec | 81.0% | 91.5% | 85.9 | 44.0% | 44.0% | 44.0 |
| 4. | Dandelion | 11.8 sec | 94.8% | 71.8% | 81.7 | 7.3% | 14.3 | 9.7 |
| 5. | NameTag 3 | 12.2 sec | 86.6% | 72.9% | 79.2 | 49.0% | 78.0% | 60.2 |

#### Disambiguation: British Museum data (dbpedia)

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | NameTag 3 (b)     | ~5 min   | 95.9% | 44.3% | 60.6 | 81.8% | 40.9% | 54.5 |
| 2. | Spacy (trf) + (b) &nbsp; &nbsp; &nbsp; | ~5 min   | 97.7% | 39.6% | 56.4 | 70.8% | 38.6% | 50.0 |
| 3. | Dandelion         | 12.5 sec | 73.9% | 32.1% | 44.8 | 70.4% | 43.2% | 53.5 |

(b) stands for baseline disambiguation system, it guesses the resource uri without using the context
