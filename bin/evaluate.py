#!/usr/bin/env python3
# evaluate: run ner against tokenized data and compare with manual annotations
# usage: evaluate machine_annotations_file < gold_annotations_file
# 20250718 e.tjongkimsang@esciencecenter.nl


import argparse
import distance
import regex
import spacy
import sys
import utils


def add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label):
    if current_text != "":
        texts.append(current_text)
        if current_entity_label:
            current_entities = utils.add_entity(current_entities, current_entity_label, current_entity_text)
        entities.append(current_entities)
    return("", {}, "", "")
 

TRANSLATE_ANNOTATION_LABEL = {'p': 'PER', 'l': 'LOC', 'g': 'LOC', 'f': 'LOC', 
                              'c': 'c', 'd': 'd', 'o': 'o', 'w': 'w', '.': '.'}


def read_annotations(data_lines):
    texts = []
    entities = []
    current_text = ""
    current_entities = {}
    current_entity_label = ""
    current_entity_text = ""

    for line in data_lines:
        if regex.search(DOC_SEPARATOR, line):
            current_text, current_entities, current_entity_text, current_entity_label = add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label)
        elif len(line) == 0:
            if current_entity_label:
                current_entities = utils.add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = ""
                current_entity_text = ""
        else:
            (token_label, token_text) = line.split()
            token_label = TRANSLATE_ANNOTATION_LABEL[token_label]
            current_text = token_text if current_text == "" else current_text + " " + token_text
            if token_label == ".":
                if current_entity_label:
                    current_entities = utils.add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = ""
                current_entity_text = ""
            elif token_label == current_entity_label:
                current_entity_text = current_entity_text + " " + token_text
            else:
                if current_entity_label:
                    current_entities = utils.add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = token_label
                current_entity_text = token_text
    add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label)
    return texts, entities


DOC_SEPARATOR = "-DOCSTART-"
parser = argparse.ArgumentParser()
parser.add_argument("machine_output_file")
parser.parse_args()
args = parser.parse_args()

lines = utils.read_lines_from_stdin()
source_texts, gold_entities = read_annotations(lines)
machine_entities = utils.read_machine_analysis(args.machine_output_file)

correct_count = {'PER': 0, 'LOC': 0}
wrong_count = {'PER': 0, 'LOC': 0}
missing_count = {'PER': 0, 'LOC': 0}
for label in ['PER', 'LOC']:
    for i in range(0, len(machine_entities)):
        if label in gold_entities[i] and label in machine_entities[i]:
            for token in gold_entities[i][label]:
                if not token in machine_entities[i][label]:
                    missing_count[label] += gold_entities[i][label][token]
                    for machine_token in machine_entities[i][label]:
                        levenshtein = round(distance.levenshtein(token, machine_token)/max(len(token), len(machine_token)), 2)
                        if levenshtein < 0.3:
                             print(f"{levenshtein} {token}; {machine_token}")
                else:
                    correct_count[label] += min(gold_entities[i][label][token],
                                         machine_entities[i][label][token])
                    if (gold_entities[i][label][token] > 
                        machine_entities[i][label][token]):
                        missing_count[label] += (gold_entities[i][label][token] - 
                                          machine_entities[i][label][token])
                    if (gold_entities[i][label][token] <
                        machine_entities[i][label][token]):
                        wrong_count[label] += (machine_entities[i][label][token] -
                                              gold_entities[i][label][token])
            for token in machine_entities[i][label]:
                if not token in gold_entities[i][label]:
                    wrong_count[label] += machine_entities[i][label][token]
        elif label in gold_entities[i]:
            for token in gold_entities[i][label]:
                missing_count[label] += gold_entities[i][label][token]
        elif label in machine_entities[i]:
            for token in machine_entities[i][label]:
                wrong_count[label] += machine_entities[i][label][token]

for label in ['LOC', 'PER']:
    if correct_count[label] + wrong_count[label] == 0:
        precision = 0
    else:
        precision = round(100 * correct_count[label] /  (correct_count[label] + wrong_count[label]), 1)
    if correct_count[label] + missing_count[label] == 0:
        recall = 0
    else:
        recall = round(100* correct_count[label] /  (correct_count[label] + missing_count[label]), 1)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = round(2 * precision * recall / (precision + recall), 1)
    print(f"Precision: {precision}% ({label}, {correct_count[label] + missing_count[label]})")
    print(f"Recall:    {recall}%")
    print(f"F1:        {f1}" )
