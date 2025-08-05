#!/usr/bin/env python3
# make_annotations_file: generate black annotations file from csv file and column name
# usage: make_annotations_file data_file.csv column_name
# 20250718 e.tjongkimsang@esciencecenter.nl

import argparse
import polars as pl
import spacy

parser = argparse.ArgumentParser()
parser.add_argument("data_file_name")
parser.add_argument("column_name")
args = parser.parse_args()

# parser is required for sentence recognition
nlp = spacy.load("en_core_web_sm", disable=["tagger", "lemmatizer"])

df = pl.read_csv(args.data_file_name, truncate_ragged_lines=True)
for text in df[args.column_name]:
    print("-DOCSTART- -DOCSTART-")
    result = nlp(text)
    for token in result:
        if token.text.strip() != "":
            entity = token.ent_type_[0].lower() if token.ent_type_ else "."
            if token.is_sent_start:
                print("")
            print(f"{entity} {token.text}")
    print("")

