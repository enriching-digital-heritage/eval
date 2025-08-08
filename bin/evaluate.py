#!/usr/bin/env python3
# evaluate: run ner against tokenized data and compare with manual annotations
# usage: evaluate machine_annotations_file < gold_annotations_file
# 20250718 e.tjongkimsang@esciencecenter.nl

import argparse
import regex
import spacy
import sys

def read_lines_from_stdin():
    lines = []
    for line in sys.stdin:
        lines.append(line.strip())
    return lines

def read_lines_from_file(file_name):
    with open(file_name, "r") as file_handle:
        lines = [line.strip() for line in file_handle]
    file_handle.close()
    return lines

def add_entity(entity_dict, entity_label, entity_text):
    if entity_label in entity_dict:
        if entity_text in entity_dict[entity_label]:
            entity_dict[entity_label][entity_text] += 1
        else:
            entity_dict[entity_label][entity_text] = 1
    else:
        entity_dict[entity_label] = { entity_text: 1}
    return entity_dict

def add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label):
    if current_text != "":
        texts.append(current_text)
        if current_entity_label:
            current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
        entities.append(current_entities)
    return("", {}, "", "")
 

TRANSLATE_ANNOTATION_LABEL = {'p': 'p', 'l': 'l', 'g': 'l', 'f': 'l', 
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
                current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = ""
                current_entity_text = ""
        else:
            (token_label, token_text) = line.split()
            token_label = TRANSLATE_ANNOTATION_LABEL[token_label]
            current_text = token_text if current_text == "" else current_text + " " + token_text
            if token_label == ".":
                if current_entity_label:
                    current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = ""
                current_entity_text = ""
            elif token_label == current_entity_label:
                current_entity_text = current_entity_text + " " + token_text
            else:
                if current_entity_label:
                    current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = token_label
                current_entity_text = token_text
    add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label)
    return texts, entities

def get_entity_text(tokens, token_id):
    entity_text = tokens[token_id]
    while token_id < len(tokens) - 1:
        token_id += 1
        if regex.search("^[A-Z]+:$", tokens[token_id]):
            break
        entity_text += " " + tokens[token_id]
    return regex.sub(";$", "", entity_text)

TRANSLATE_MACHINE_LABEL = {'P': 'p', 'L': 'l', 'G': 'l', 'F': 'l'}

def read_machine_analysis(file_name):
    lines = read_lines_from_file(file_name)
    entities = []
    for line in lines:
        if regex.search("Entities:", line):
            tokens = line.split()
            current_entities = {}
            for i in range(0, len(tokens)):
                if tokens[i] in ["PERSON:", "PER:", "LOC:", "GPE:", "FAC:"]:
                    entity_label = TRANSLATE_MACHINE_LABEL[tokens[i][0]]
                    entity_text = get_entity_text(tokens, i+1)
                    current_entities = add_entity(current_entities, entity_label, entity_text)
            entities.append(current_entities)
    return entities

DOC_SEPARATOR = "-DOCSTART-"
parser = argparse.ArgumentParser()
parser.add_argument("machine_output_file")
parser.parse_args()
args = parser.parse_args()

lines = read_lines_from_stdin()
source_texts, gold_entities = read_annotations(lines)
machine_entities = read_machine_analysis(args.machine_output_file)

correct_count = {'p': 0, 'l': 0}
wrong_count = {'p': 0, 'l': 0}
missing_count = {'p': 0, 'l': 0}
for label in ['p', 'l']:
    for i in range(0, len(machine_entities)):
        if label in gold_entities[i] and label in machine_entities[i]:
            for token in gold_entities[i][label]:
                if not token in machine_entities[i][label]:
                    missing_count[label] += gold_entities[i][label][token]
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

for label in ['l', 'p']:
    precision = round(100 * correct_count[label] /  (correct_count[label] + wrong_count[label]), 1)
    recall = round(100* correct_count[label] /  (correct_count[label] + missing_count[label]), 1)
    f1 = round(2 * precision * recall / (precision + recall), 1)
    print(f"Precision: {precision}% ({label}, {correct_count[label] + missing_count[label]})")
    print(f"Recall:    {recall}%")
    print(f"F1:        {f1}" )
