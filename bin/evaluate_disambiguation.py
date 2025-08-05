#!/usr/bin/env python3
# evaluate_disambiguation.py: compare json machine data with with manual annotations
# usage: evaluate_disamboguation.py machine_annotations_file < gold_annotations_file
# 20250805 e.tjongkimsang@esciencecenter.nl


import argparse
import ast
import polars as pl
import regex
import spacy
import sys


ENTITY_LABELS = ["LOC", "PER"]


def read_annotations_from_stdin():
    annotations_df = pl.read_csv(sys.stdin)
    annotations_df_columns = annotations_df.columns
    annotations_dict = {}
    for row in annotations_df.iter_rows():
        row_dict = dict(zip(annotations_df_columns, row))
        line_nbr = row_dict['line_nbr']
        entity_label = row_dict['entity_label']
        entity_text = row_dict['entity_text']
        dbpedia_uri = row_dict['dbpedia_uri']
        if line_nbr not in annotations_dict:
            annotations_dict[line_nbr] = {entity_label: {} for entity_label in ENTITY_LABELS}
        if entity_text not in annotations_dict[line_nbr][entity_label]:
            annotations_dict[line_nbr][entity_label][entity_text] = []
        annotations_dict[line_nbr][entity_label][entity_text].append(dbpedia_uri)
    return annotations_dict


def read_machine_analysis_json(file_name):
    line_nbr = 0
    machine_analysis_dict = {}
    with open(file_name, "r") as infile:
        for line in infile:
            line_nbr += 1
            line_data = ast.literal_eval(line.strip())
            if "annotations" in line_data.keys():
                for entity_data in line_data["annotations"]:
                    if "spot" in entity_data and "lod" in entity_data and 'dbpedia' in entity_data['lod']:
                        entity_label = ""
                        if ("http://dbpedia.org/ontology/Location" in entity_data["types"] or 
                            "http://dbpedia.org/ontology/Place" in entity_data["types"]):
                            entity_label = "LOC"
                        if ("http://dbpedia.org/ontology/Animal" in entity_data["types"] or
                            "http://dbpedia.org/ontology/Deity" in entity_data["types"]):
                            entity_label = "PER"
                        if entity_label != "":
                            if line_nbr not in machine_analysis_dict:
                                machine_analysis_dict[line_nbr] = {entity_label: {} for entity_label in ENTITY_LABELS}
                            if entity_data['spot'] not in machine_analysis_dict[line_nbr][entity_label]:
                                machine_analysis_dict[line_nbr][entity_label][entity_data['spot']] = []
                            machine_analysis_dict[line_nbr][entity_label][entity_data['spot']].append(entity_data['lod']['dbpedia'])
    infile.close()
    return machine_analysis_dict


def make_unique_uris(mydict):
    for line_nbr in mydict:
        for entity_label in mydict[line_nbr]:
            for entity_text in mydict[line_nbr][entity_label]:
                seen = {}
                uri_list = []
                for uri in mydict[line_nbr][entity_label][entity_text]:
                    if uri in seen:
                        seen[uri] += 1
                    else:
                        seen[uri] = 1
                    uri_list.append(f"{uri}_{seen[uri]}")
                mydict[line_nbr][entity_label][entity_text] = uri_list
    return mydict


parser = argparse.ArgumentParser()
parser.add_argument("machine_output_file")
parser.parse_args()
args = parser.parse_args()

annotations_dict = read_annotations_from_stdin()
machine_analysis_dict = read_machine_analysis_json(args.machine_output_file)

annotations_dict = make_unique_uris(annotations_dict)
machine_analysis_dict = make_unique_uris(machine_analysis_dict)


for entity_label in ENTITY_LABELS:
    correct = 0
    wrong = 0
    missing = 0
    for line_nbr in annotations_dict:
        for entity_text in annotations_dict[line_nbr][entity_label]:
            annotations_set = set(annotations_dict[line_nbr][entity_label][entity_text])
            if line_nbr not in machine_analysis_dict or entity_label not in machine_analysis_dict[line_nbr] or entity_text not in machine_analysis_dict[line_nbr][entity_label]:
                missing += len(annotations_set)
            else:
                machine_set = set(machine_analysis_dict[line_nbr][entity_label][entity_text])
                correct += len(annotations_set.intersection(machine_set))
                wrong += len(machine_set.difference(annotations_set))
                missing += len(annotations_set.difference(machine_set))
    for line_nbr in machine_analysis_dict:
        if entity_label in machine_analysis_dict[line_nbr]:
            for entity_text in machine_analysis_dict[line_nbr][entity_label]:
                machine_set = set(machine_analysis_dict[line_nbr][entity_label][entity_text])
                if line_nbr not in annotations_dict or entity_label not in machine_analysis_dict[line_nbr] or entity_text not in machine_analysis_dict[line_nbr][entity_label]:
                    wrong += len(machine_set)
    
    
    precision = round(100 * correct /  (correct + wrong), 1)
    recall = round(100* correct /  (correct + missing), 1)
    f1 = round(2 * precision * recall / (precision + recall), 1)
    print(f"Precision: {precision}% ({entity_label}, {correct + missing})")
    print(f"Recall:    {recall}%")
    print(f"F1:        {f1}" )
