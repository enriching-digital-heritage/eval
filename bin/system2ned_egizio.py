#!/usr/bin/env python3
# system2ned_egizio.py: convert named entity recognition system to ned_egizio format
# usage: system2ned_egizio.py recognition_annotation.txt < system_evaluate.txt
# note: target format: https://github.com/marcostranisci/ned_egizio/blob/main/data/egizio_datiedescrizioni_entities.csv
# 20250819 e.tjongkimsang@esciencecenter.nl


import argparse
import polars as pl
import regex
import sys
import utils


parser = argparse.ArgumentParser()
parser.add_argument("annotations_filename")
parser.parse_args()
args = parser.parse_args()

source_texts, gold_entities = utils.read_annotations(args.annotations_filename)
machine_entities = utils.read_machine_analysis(sys.stdin)

print("Description,entities")
for text, entities_dict in zip(source_texts, machine_entities):
    entities_list = [entity_text for entity_label in entities_dict 
                                 for entity_text in entities_dict[entity_label]
                                 for counter in range(0, entities_dict[entity_label][entity_text])]
    text = regex.sub('"', '\\"', text)
    print(f"\"{text}\",{entities_list}")

data = pl.read_csv("nametag3_output_evaluate.csv")
