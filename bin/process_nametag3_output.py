#!/usr/bin/env python3
# process_nametag3_output.py: convert nametag3 output to evaluate.py input format
# usage: process_nametag3_output.py < nametag3_output.txt
# 20250731 e.tjongkimsang@esciencecenter.nl

import regex
import spacy
import sys

def read_lines_from_stdin():
    lines = []
    for line in sys.stdin:
        lines.append(line.strip())
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

def add_text(current_text, current_entities, current_entity_text, current_entity_label):
    if current_text != "":
        if current_entity_label:
            current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
        print(f"Entities: ", end="")
        for entity_label in current_entities:
            for entity_text in current_entities[entity_label]:
                for i in range(0, current_entities[entity_label][entity_text]):
                    print(f"{entity_label}: {entity_text}; ", end="")
        print("")
    return("", {}, "", "")
 

def process_nametag3_lines(data_lines):
    current_text = ""
    current_entities = {}
    current_entity_label = ""
    current_entity_text = ""

    for line in data_lines:
        if regex.search(DOC_SEPARATOR, line):
            current_text, current_entities, current_entity_text, current_entity_label = add_text(current_text, current_entities, current_entity_text, current_entity_label)
        elif len(line) == 0:
            if current_entity_label:
                current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
                current_entity_label = ""
                current_entity_text = ""
        else:
            (token_text, token_label) = line.split()
            token_label = token_label[2:] if len(token_label) > 1 else token_label
            current_text = token_text if current_text == "" else current_text + " " + token_text
            if token_label == "O":
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
    add_text(current_text, current_entities, current_entity_text, current_entity_label)


DOC_SEPARATOR = "-DOCSTART-"

data_lines = read_lines_from_stdin()
process_nametag3_lines(data_lines)
