#!/usr/bin/env python3
# evaluate_disambiguation.py: compare json machine data with with manual annotations
# usage: evaluate_disamboguation.py machine_annotations_file < gold_annotations_file
# 20250805 e.tjongkimsang@esciencecenter.nl


import argparse
import distance
import polars as pl
import regex
import sys


ENTITY_LABELS = ["LOC", "PER"]


def read_csv_data(data_source):
    """Read machine analysis from csv file or standard input and return it as a list of dicts of lines"""
    return pl.read_csv(data_source).to_dicts()


def normalize_dbpedia_uri(dbpedia_uri):
    """Standardize http protocol and folder of DBpedia uri and return it"""
    dbpedia_uri = regex.sub("^https:", "http:", dbpedia_uri)
    dbpedia_uri = regex.sub("/resource/", "/page/", dbpedia_uri)
    return dbpedia_uri


def normalize_data(entity_list):
    """Normalize the DBpedia uri and remove the Wikidata uri and return them"""
    normalized_entities = []
    for entity in entity_list:
        if "dbpedia_uri" in entity and entity["dbpedia_uri"]:
            normalized_entities.append({"line_nbr": entity["line_nbr"],
                                        "entity_label": entity["entity_label"],
                                        "entity_text": entity["entity_text"],
                                        "dbpedia_uri": normalize_dbpedia_uri(entity["dbpedia_uri"])})
    return normalized_entities
    
        
parser = argparse.ArgumentParser()
parser.add_argument("machine_output_file")
parser.parse_args()
args = parser.parse_args()

annotations_list = normalize_data(read_csv_data(sys.stdin))
machine_analysis_list = normalize_data(read_csv_data(args.machine_output_file))

for target_entity_label in ENTITY_LABELS:
    correct = 0
    missing = 0
    for entity in annotations_list:
        if entity["entity_label"] == target_entity_label:
            if entity in machine_analysis_list:
                correct += 1
                machine_analysis_list.remove(entity)
                entity["matched"] = True
            else:
                missing += 1
    wrong = len([entity for entity in machine_analysis_list if entity["entity_label"] == target_entity_label])
    for machine_entity in machine_analysis_list:
        if machine_entity["entity_label"] == target_entity_label:
            for annotation_entity in annotations_list:
                if annotation_entity["entity_label"] == target_entity_label and machine_entity["line_nbr"] == annotation_entity["line_nbr"] and "matched" not in entity:
                    annotation_text = annotation_entity["entity_text"]
                    machine_text = machine_entity["entity_text"]
                    levenshtein = round(distance.levenshtein(annotation_text, machine_text)/max(len(annotation_text), len(machine_text)), 2)
                    if levenshtein < 0.3 and levenshtein > 0:
                         print(f"{levenshtein} {annotation_text}; {machine_text} {annotation_entity['dbpedia_uri']} {machine_entity['dbpedia_uri']}")
    if correct + wrong == 0:
        precision = 0
    else:
        precision = round(100 * correct /  (correct + wrong), 1)
    if correct + missing == 0:
        recall = 0
    else:
        recall = round(100* correct /  (correct + missing), 1)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = round(2 * precision * recall / (precision + recall), 1)
    print(f"Precision: {precision}% ({target_entity_label}, {correct + missing})")
    print(f"Recall:    {recall}%")
    print(f"F1:        {f1}" )
