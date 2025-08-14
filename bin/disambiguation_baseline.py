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
    log_df_columns = log_df.columns
    log_dict = {}
    for row_list in log_df.iter_rows():
        row_dict = dict(zip(log_df_columns, row_list))
        log_dict[row_dict["dbpedia_uri"]] = row_dict
    return log_dict


def append_to_logfile(dbpedia_uri, exists_value, entity_label, lemma):
    with open(LOGFILE_NAME, "a") as outfile:
        pl.DataFrame([{"exists_value": "True" if exists_value else "",
                       "entity_label": entity_label,
                       "lemma": lemma,
                       "dbpedia_uri": dbpedia_uri}]).write_csv(outfile, include_header=False)
        outfile.close()


def make_dbpedia_uri(entity_text):
    """Convert entity text to DBpedia uri and return it"""
    page_name = regex.sub(" ", "_", entity_text)
    return f"https://dbpedia.org/page/{page_name}"


def check_dbpedia_redirect(lemma):
    endpoint = "https://dbpedia.org/sparql"
    page_name = regex.sub(" ", "_", lemma)
    query = f"""
    SELECT ?target ?label WHERE {{
      <http://dbpedia.org/resource/{page_name}> (dbo:wikiPageRedirects)+ ?target .
      FILTER NOT EXISTS {{ ?target dbo:wikiPageRedirects ?next . }}
      OPTIONAL {{ ?target rdfs:label ?label FILTER (lang(?label) = 'en') }}
    }}
    LIMIT 1
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    try:
        target_lemma = results["results"]["bindings"][0]["label"]["value"]
    except:
        target_lemma = lemma
    time.sleep(1)
    return target_lemma


def get_dbpedia_entity_label(lemma):
    endpoint = "https://dbpedia.org/sparql"
    target_lemma = check_dbpedia_redirect(lemma)

    query = f"""
        SELECT DISTINCT ?type
        WHERE {{
          ?s rdfs:label "{target_lemma}"@en .
          ?s rdf:type ?type .
        }}
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
        
    results = sparql.query().convert()
    types = [binding['type']['value'] for binding in results["results"]["bindings"]]
    if 'http://dbpedia.org/ontology/Person' in types or 'http://dbpedia.org/ontology/Animal' in types or 'http://dbpedia.org/ontology/Deity' in types:
        entity_label = "PER"
    elif 'http://dbpedia.org/ontology/Location' in types or 'http://dbpedia.org/ontology/Place' in types:
        entity_label = "LOC"
    else:
        entity_label = ""
    time.sleep(1)
    return entity_label, target_lemma


def get_dbpedia_exists_value(lemma):
    endpoint = "https://dbpedia.org/sparql"
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
    return exists_value


    
def check_dbpedia_uri(dbpedia_uri, log_dict):
    if dbpedia_uri in log_dict:
        entity_label_dbpedia = log_dict[dbpedia_uri]["entity_label"]
        exists_value = log_dict[dbpedia_uri]["exists_value"]
        lemma = log_dict[dbpedia_uri]["lemma"]
    else:
        lemma = dbpedia_uri.split("/")[-1]
        lemma = regex.sub("_", " ", lemma)
        exists_value = get_dbpedia_exists_value(lemma)
        entity_label_dbpedia = ""
        if exists_value:
            entity_label_dbpedia, lemma = get_dbpedia_entity_label(lemma)
        log_dict[dbpedia_uri] = {"entity_label": entity_label_dbpedia,
                                 "exists_value": exists_value,
                                 "lemma": lemma}
        append_to_logfile(dbpedia_uri, exists_value, entity_label_dbpedia, lemma)
        time.sleep(1)
    return exists_value, entity_label_dbpedia, lemma


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
               exists_value, entity_label_dbpedia, lemma = check_dbpedia_uri(dbpedia_uri, log_dict)
               if not exists_value:
                   print(f"Sorry, this page does not exist: {dbpedia_uri}", file=sys.stderr)
               elif entity_label_dbpedia != entity_label:
                   print(f"Sorry, page entity label ({entity_label_dbpedia}) does not match {entity_label}: {dbpedia_uri}", file=sys.stderr)
               else:
                   entities_list.append({"line_nbr": line_nbr,
                                         "entity_label": entity_label,
                                         "entity_text": entity_text,
                                         "dbpedia_uri": make_dbpedia_uri(lemma)})

pl.DataFrame(entities_list).write_csv(sys.stdout.buffer)
