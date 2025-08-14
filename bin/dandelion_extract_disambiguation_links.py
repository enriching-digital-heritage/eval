#!/usr/bin/env python3
# dandelion_extract_disambiguation_links.pl: extract entities from json output of dandelion
# usage dandelion_extract_disambiguation_links.pl < dandelion_output.json
# 20250801 e.tjongkimsang@esciencecenter.nl


import ast
import polars as pl
import sys
import time
from SPARQLWrapper import SPARQLWrapper, JSON


LOGFILE_NAME = "/home/erikt/projects/enriching/data/disambiguation_log.txt"


def read_logfile():
    log_df = pl.read_csv(LOGFILE_NAME)
    return dict(zip(log_df["dbpedia_uri"], log_df["wikidata_uri"]))


def append_to_logfile(entity_label, dbpedia_uri, wikidata_uri):
    with open(LOGFILE_NAME, "a") as outfile:
        pl.DataFrame([{"entity_label": entity_label,
                       "dbpedia_uri": dbpedia_uri,
                       "wikidata_uri": wikidata_uri}]).write_csv(outfile, include_header=False)
        outfile.close()


def find_best_wikidata_link(bindings):
    try:
        wikidata_uri = bindings[0]["wikidata"]["value"]
        wikidata_id = int(wikidata_uri.split('Q')[-1])
    except:
        wikidata_uri = ""
        wikidata_id = 0
    for i in range(1, len(bindings)):
        w_uri = bindings[i]["wikidata"]["value"]
        w_id = int(w_uri.split('Q')[-1])
        if w_id < wikidata_id:
            wikidata_uri = w_uri
            wikipedia_id = w_id
    return wikidata_uri


def lookup_wikipedia_uri(entity_label, dbpedia_uri, logdata_dict):
    if dbpedia_uri in logdata_dict.keys():
        return logdata_dict[dbpedia_uri]
    sparql.setQuery(f"""
        SELECT ?wikidata
        WHERE {{
            <{dbpedia_uri}> <http://www.w3.org/2002/07/owl#sameAs> ?wikidata .
             FILTER (STRSTARTS(STR(?wikidata), "http://www.wikidata.org/entity/"))
        }}
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    wikidata_uri = find_best_wikidata_link(results["results"]["bindings"])
    logdata_dict[dbpedia_uri] = wikidata_uri
    append_to_logfile(entity_label, dbpedia_uri, wikidata_uri)
    time.sleep(1)
    return wikidata_uri


line_nbr = 0
data = []
logdata_dict = read_logfile()
sparql = SPARQLWrapper("https://dbpedia.org/sparql")
first_output_line = True
for line in sys.stdin:
    line_nbr += 1
    line_data = ast.literal_eval(line.strip())
    if "annotations" in line_data.keys():
        for entity_data in line_data["annotations"]:
            entity_label = ""
            if ("http://dbpedia.org/ontology/Location" in entity_data["types"] or 
               "http://dbpedia.org/ontology/Place" in entity_data["types"]):
                entity_label = "LOC"
            if ("http://dbpedia.org/ontology/Person" in entity_data["types"] or
                "http://dbpedia.org/ontology/Animal" in entity_data["types"] or
                "http://dbpedia.org/ontology/Deity" in entity_data["types"]):
                entity_label = "PER"
            if entity_label != "":
                dbpedia_uri = entity_data['lod']['dbpedia']
                wikidata_uri = lookup_wikipedia_uri(entity_label, dbpedia_uri, logdata_dict)
                output_df = pl.DataFrame({"line_nbr": line_nbr,
                                          "entity_label": entity_label,
                                          "entity_text": entity_data['spot'],
                                          "dbpedia_uri": dbpedia_uri,
                                          "wikidata_uri": wikidata_uri})
                if first_output_line:
                   output_df.write_csv(sys.stdout)
                   first_output_line = False
                else:
                   output_df.write_csv(sys.stdout, include_header=False)
