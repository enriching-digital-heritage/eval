# Evaluation software and results

Software and results of evaluations in the Lorentz workshop [Enriching Digital Heritage](https://www.lorentzcenter.nl/enriching-digital-heritage-with-llms-and-linked-open-data.html). Results of the workshop are collected at the [Research Software Directory](https://research-software-directory.org/projects/enriching-digital-heritage-with-llms-and-lod).

## Evaluation results

### Evaluation data collections

| Task | Data source | Language | Size | Persons | Locations | Topic |
| ---- | ----------- | -------- | ---- | ------- | --------- | ----- |
| Recognition | British Museum | English | 100 texts | 115 | 47 | European Renaissance art |
| Recognition | Egyptian Museum | English | 100 texts | 177 | 91 | Ancient Egypt |
| Disambiguation | British Museum | English | 100 texts | 115 | 47 | European Renaissance art |

### Systems performance

#### Recognition: British Museum data

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | NameTag 3 | 12.4 sec | 85.3% | 80.9% | 83.0 | 72.7% | 68.1% | 70.3 |
| 2. | Spacy (trf) + | 2.3 sec | 75.9% | 71.3% | 73.5 | 54.2% | 55.3% | 54.7 |
| 3. | Spacy (trf) | 2.4 sec | 75.9% | 71.3% | 73.5 | 53.7% | 46.8% | 50.0 |
| 4. | gpt-oss 20b | 30 min 52 sec | 76.7% | 60.0% | 67.3 | 57.1% | 34.0% | 42.6 |
| 5. | Llama 3.3 | 28 min 33 sec | 64.7% | 47.8% | 55.0 | 41.2% | 29.8% | 34.6 |
| 6. | Dandelion | 12.5 sec | 78.3% | 31.3% | 44.7 | 70.4% | 40.4% | 51.3 |

The :P-related stats concern Person labels while the :L-related stats concern Location labels

"Spacy (trf) +" is "Spacy (trf)" with an additional list of 349 locations provided by Gethin

#### Recognition: Egyptian Museum data

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | gpt-oss 20b | 1 hr 2 min 9 sec | 89.5% | 96.0% | 92.6 | 40.4% | 60.4% | 48.4 |
| 2. | Spacy (trf) | 2.6 sec | 81.5% | 92.1% | 86.5 | 20.9% | 20.9% | 20.9 |
| 3. | Llama 3.3 | 38 min 12 sec | 81.9% | 92.1% | 86.7 | 31.1% | 54.9% | 39.7 |
| 4. | Dandelion | 11.8 sec | 94.0% | 71.2% | 81.0 | 6.8% | 13.2% | 9.0 |
| 5. | NameTag 3 | 12.2 sec | 87.2% | 73.4% | 79.7 | 49.0% | 78.0% | 60.2 |

#### Disambiguation: British Museum data

|   | System | Time | Precision:P | Recall:P | F1:P | Precision:L | Recall:L | F1:L |
| - | ------ | ---: | :---------: | :------: | :--: | :---------: | :------: | :--: |
| 1. | Dandelion | 12.5 sec | 91.7% | 28.7% | 43.7 | 81.8% | 38.3% | 52.2 |
