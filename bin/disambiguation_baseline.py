#!/usr/bin/env python3
# disambiguation_baseline.py: convert recognition evaluation file to disambiguation evaluation file
# usage: disambiguation_baseline.py < recognition_evaluation_file > disambiguation_evaluation_file
# 20250811 e.tjongkimsang@esciencecenter.nl


import polars as pl
import regex
import sys
import time
import utils
from SPARQLWrapper import SPARQLWrapper, JSON


LOGFILE_NAME = "/home/erikt/projects/enriching/data/dbpedia_log.txt"


def read_logfile():
    log_df = pl.read_csv(LOGFILE_NAME)
    return dict(zip(log_df["dbpedia_uri"], log_df["exists"]))


def append_to_logfile(dbpedia_uri, exists_value):
    with open(LOGFILE_NAME, "a") as outfile:
        pl.DataFrame([{"exists_value": "True" if exists_value else "",
                       "dbpedia_uri": dbpedia_uri}]).write_csv(outfile, include_header=False)
        outfile.close()


def make_dbpedia_uri(entity_text):
    """Convert entity text to DBpedia uri and return it"""
    page_name = regex.sub(" ", "_", entity_text)
    return f"https://dbpedia.org/page/{page_name}"


def check_dbpedia_uri(dbpedia_uri, log_dict):
    if dbpedia_uri in log_dict:
        return log_dict[dbpedia_uri]
    endpoint = "https://dbpedia.org/sparql"
    lemma = dbpedia_uri.split("/")[-1]
    query = f"""
    ASK WHERE {{
      ?s rdfs:label "{lemma}"@en .
    }}
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    exists_value = results['boolean']
    log_dict[dbpedia_uri] = exists_value
    append_to_logfile(dbpedia_uri, exists_value)
    time.sleep(1)
    return results['boolean']


recognition_entities = utils.read_machine_analysis(sys.stdin)
line_nbr = 0
entities_list = []
log_dict = read_logfile()
for line_dict in recognition_entities:
    line_nbr += 1
    for entity_label in line_dict:
        for entity_text in line_dict[entity_label]:
           for counter in range(0, line_dict[entity_label][entity_text]):
               dbpedia_uri = make_dbpedia_uri(entity_text)
               if check_dbpedia_uri(dbpedia_uri, log_dict):
                   entities_list.append({"line_nbr": line_nbr,
                                         "entity_label": entity_label,
                                         "entity_text": entity_text,
                                         "dbpedia_uri": make_dbpedia_uri(entity_text)})
               else:
                   print(f"Sorry, this page does not exist: {dbpedia_uri}", file=sys.stderr)
pl.DataFrame(entities_list).write_csv(sys.stdout.buffer)
