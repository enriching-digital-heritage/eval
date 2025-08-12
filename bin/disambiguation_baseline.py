#!/usr/bin/env python3
# disambiguation_baseline.py: convert recognition evaluation file to disambiguation evaluation file
# usage: disambiguation_baseline.py < recognition_evaluation_file > disambiguation_evaluation_file
# 20250811 e.tjongkimsang@esciencecenter.nl


import polars as pl
import regex
import sys
import utils


def make_dbpedia_uri(entity_text):
    """Convert entity text to DBpedia uri and return it"""
    page_name = regex.sub(" ", "_", entity_text)
    return f"https://dbpedia.org/page/{page_name}"


recognition_entities = utils.read_machine_analysis(sys.stdin)
line_nbr = 0
entities_list = []
for line_dict in recognition_entities:
    line_nbr += 1
    for entity_label in line_dict:
        for entity_text in line_dict[entity_label]:
           for counter in range(0, line_dict[entity_label][entity_text]):
               entities_list.append({"line_nbr": line_nbr,
                                     "entity_label": entity_label,
                                     "entity_text": entity_text,
                                     "dbpedia_uri": make_dbpedia_uri(entity_text)})
pl.DataFrame(entities_list).write_csv(sys.stdout.buffer)
