# usage: import utils


import regex
import sys


def read_lines_from_stdin():
    """Read lines from standard input and return as list of strings"""
    lines = []
    for line in sys.stdin:
        lines.append(line.strip())
    return lines


def read_lines_from_file(file_name):
    """Read lines from the file file_name, return as list of strings"""
    if type(file_name) != str:
        return read_lines_from_stdin()
    else:
        with open(file_name, "r") as file_handle:
            lines = [line.strip() for line in file_handle]
        file_handle.close()
        return lines


ENTITY_LABELS = ["CARDINAL", "DATE", "EVENT", "FAC", "GPE", "LANGUAGE", "LAW", "LOC", "LOCATION", "MISC", "NORP", "ORDINAL", "ORG", "PER", "PERSON", "PRODUCT", "WORK_OF_ART"]
TRANSLATE_MACHINE_LABEL = {"FAC": "LOC", "GPE": "LOC", "LOCATION": "LOC", "PERSON": "PER"}
TRANSLATE_ANNOTATION_LABEL = {"l": "LOC", "p": "PER"}


def add_entity(entity_dict, entity_label, entity_text):
    """Add entity with label entity_label and text entity_text to entity_dict and return it"""
    if entity_label in TRANSLATE_ANNOTATION_LABEL:
        entity_label = TRANSLATE_ANNOTATION_LABEL[entity_label]
    if entity_label in entity_dict:
        if entity_text in entity_dict[entity_label]:
            entity_dict[entity_label][entity_text] += 1
        else:
            entity_dict[entity_label][entity_text] = 1
    else:
        entity_dict[entity_label] = { entity_text: 1}
    return entity_dict


tokens_seen = []


def get_entity_text(tokens, token_id):
    """Extract multi-token text of current entity from a type-position-text; string and return it"""
    entity_text = tokens[token_id]
    while token_id < len(tokens) - 1:
        token_id += 1
        if regex.sub(":$", "", tokens[token_id]) in ENTITY_LABELS:
            break
        elif regex.search("^[A-Z][A-Z][A-Z][A-Z]*$", tokens[token_id]) and tokens[token_id] not in tokens_seen:
            tokens_seen.append(tokens[token_id])
            print(f"Suspicious entity token: {tokens[token_id]}; is it a label?")
        entity_text += " " + tokens[token_id]
    return regex.sub("^(\d+\s+)?", "", regex.sub(";$", "", entity_text))




def read_machine_analysis(file_name):
    """Read all entities from an entity string and return them in a list"""
    data_lines = read_lines_from_file(file_name)
    entities = []
    for line in data_lines:
        if regex.search("Entities:", line):
            tokens = line.split()
            current_entities = {}
            for i in range(0, len(tokens)):
                token = regex.sub(":$", "", tokens[i])
                if token in ENTITY_LABELS:
                    entity_label = token
                    if entity_label in TRANSLATE_MACHINE_LABEL:
                        entity_label = TRANSLATE_MACHINE_LABEL[entity_label]
                    entity_text = get_entity_text(tokens, i+1)
                    current_entities = add_entity(current_entities, entity_label, entity_text)
            entities.append(current_entities)
    return entities


DOC_SEPARATOR = "-DOCSTART-"
TRANSLATE_ANNOTATION_LABEL = {'p': 'p', 'l': 'l', 'g': 'l', 'f': 'l',
                              'c': 'c', 'd': 'd', 'o': 'o', 'w': 'w', '.': '.'}


def add_text(texts, entities, current_text, current_entities, current_entity_text, current_entity_label):
    """Add current entity to entities list if it is non-empty and return empty values for other parameter arguments"""
    if current_text != "":
        texts.append(current_text)
        if current_entity_label:
            current_entities = add_entity(current_entities, current_entity_label, current_entity_text)
        entities.append(current_entities)
    return("", {}, "", "")


def read_annotations(file_name):
    """Read annotations from file or stdin and return the texts and the entities"""
    texts = []
    entities = []
    current_text = ""
    current_entities = {}
    current_entity_label = ""
    current_entity_text = ""

    data_lines = read_lines_from_file(file_name)
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
