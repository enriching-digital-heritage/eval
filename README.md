# Evaluation software and results

Software and results of the Lorentz workshop [Enriching Digital Heritage](https://www.lorentzcenter.nl/enriching-digital-heritage-with-llms-and-linked-open-data.html). Results of the workshop are collected at the [Research Software Directory](https://research-software-directory.org/projects/enriching-digital-heritage-with-llms-and-lod).

## Evaluation results

### Evaluation data collections

| Task | Data source | Language | Size | Persons | Locations | Topic |
| ---- | ----------- | -------- | ---- | ------- | --------- | ----- |
| Recognition | British Museum | English | 100 texts | 115 | 47 | European Renaissance art |
| Recognition | Egyptian Museum | English | 100 texts | 177 | 91 | Ancient Egypt |
| Disambiguation | British Museum | English | 100 texts | 115 | 47 | European Renaissance art |

### Systems performance

#### Recognition: British Museum data

|   | System | Time | Label | Precision | Recall |  F1 | Label | Precision | Recall |  F1 |
| - | ------ | ---- | ----- | :-------: | :----: | :-: | ----- | :-------: | :----: | :-: |
| 1. | NameTag 3 | 12.4 sec | Person | 85.3% | 80.9% | 83.0 | Location | 72.7% | 68.1% | 70.3 |
| 2. | Spacy (trf) + | 2.4 sec | Person | 74.1% | 69.6% | 71.8 | Location | 54.2% | 55.3% | 54.7 |
| 3. | Spacy (trf) | 2.3 sec | Person | 74.1% | 69.6% | 71.8 | Location | 53.7% | 46.8% | 50.0 |
| 4. | gpt-oss 20b | 30 min 52 sec | Person | 76.7% | 60.0% | 67.3 | Location | 57.1% | 34.0% | 42.6 |
| 5. | Llama 3.3 | 28 min 33 sec | Person | 64.7% | 47.8% | 55.0 | Location | 41.2% | 29.8% | 34.6 |
| 6. | Dandelion | 12.5 sec | Person | 78.3% | 31.3% | 44.7 | Location | 70.4% | 40.4% | 51.3 |

"Spacy (trf) +" is "Spacy (trf)" with an additional list of 349 locations provided by Gethin

#### Recognition: Egyptian Museum data

|   | System | Time | Label | Precision | Recall | F1  | Label | Precision | Recall | F1  |
| - | ------ | ---- | ----- | :-------: | :----: | :-: | ----- | :-------: | :----: | :-: |
| 1. | gpt-oss 20b | 1 hr 2 min 9 sec | Person | 89.5% | 96.0% | 92.6 | Location | 40.4% | 60.4% | 48.4 |
| 2. | Spacy (trf) | 2.6 sec | Person | 81.5% | 92.1% | 86.5 | Location | 20.9% | 20.9% | 20.9 |
| 3. | Llama 3.3 | 38 min 12 sec | Person | 81.8% | 91.5% | 86.4 | Location | 30.4% | 53.8% | 38.8 |
| 4. | Dandelion | 11.8 sec | Person | 94.0% | 71.2% | 81.0 | Location | 6.8% | 13.2% | 9.0 |
| 5. | NameTag 3 | 12.2 sec | Person | 87.2% | 73.4% | 79.7 | Location | 49.0% | 78.0% | 60.2 |

#### Disambiguation: British Museum data

|   | System | Time | Label | Precision | Recall |  F1 | Label | Precision | Recall |  F1 |
| - | ------ | ---- | ----- | :-------: | :----: | :-: | ----- | :-------: | :----: | :-: |
| 1. | Dandelion | 12.5 sec | Person | 91.7% | 28.7% | 43.7 | Location | 81.8% | 38.3% | 52.2 |
