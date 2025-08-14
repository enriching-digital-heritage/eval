#!/usr/bin/env python3
# disambiguation_baseline.py: convert recognition evaluation file to disambiguation evaluation file
# usage: disambiguation_baseline.py < recognition_evaluation_file > disambiguation_evaluation_file
# 20250811 e.tjongkimsang@esciencecenter.nl


import polars as pl
import regex
import requests
import sys
import time
import utils
from SPARQLWrapper import SPARQLWrapper, JSON


LOGFILE_NAME = "/home/erikt/projects/enriching/data/wikidata_log.txt"
SLEEP_TIME = 5

def read_logfile():
    log_df = pl.read_csv(LOGFILE_NAME)
    log_df_columns = log_df.columns
    log_dict = {}
    for row_list in log_df.iter_rows():
        row_dict = dict(zip(log_df_columns, row_list))
        log_dict[row_dict["entity_text"]] = row_dict
    return log_dict


def append_to_logfile(entity_text, exists_value, wikidata_label, wikidata_lemma, wikidata_id):
    with open(LOGFILE_NAME, "a") as outfile:
        pl.DataFrame([{"exists_value": "True" if exists_value else "",
                       "wikidata_label": wikidata_label,
                       "wikidata_lemma": wikidata_lemma,
                       "wikidata_id": wikidata_id,
                       "entity_text": entity_text}]).write_csv(outfile, include_header=False)
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
    time.sleep(SLEEP_TIME)
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
    time.sleep(SLEEP_TIME)
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


    
def get_wikidata_uri(entity_text, log_dict):
    if entity_text in log_dict:
        exists_value = log_dict[entity_text]["exists_value"]
        wikidata_label = log_dict[entity_text]["wikidata_label"]
        wikidata_lemma = log_dict[entity_text]["wikidata_lemma"]
        wikidata_id = log_dict[entity_text]["wikidata_id"]
        return exists_value, wikidata_id, wikidata_lemma, wikidata_label
    params = {
        'action': 'wbsearchentities',
        'language': 'en',
        'format': 'json',
        'search': entity_text 
    }
    url = 'https://www.wikidata.org/w/api.php'
    time.sleep(SLEEP_TIME)
    r = requests.get(url, params=params)
    if len(r.json()["search"]) < 1:
        exists_value = ""
        wikidata_label = ""
        wikidata_lemma = ""
        wikidata_id = ""
        append_to_logfile(entity_text, exists_value, wikidata_label, wikidata_lemma, wikidata_id)
        return exists_value, wikidata_id, wikidata_lemma, wikidata_label
    
    exists_value = True
    page_info = r.json()["search"][0]
    wikidata_id = page_info["id"]
    wikidata_lemma = page_info["display"]["label"]["value"]

    endpoint = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    wikidata_categories = {"Q5": "PER", "Q178885": "PER", "Q17334923": "LOC", "Q2221906": "LOC"}
    wikidata_label = ""
    for category in wikidata_categories:
        query = f"""
    PREFIX wd:  <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX p:   <http://www.wikidata.org/prop/>
    PREFIX ps:  <http://www.wikidata.org/prop/statement/>
    PREFIX wikibase: <http://wikiba.se/ontology#>

    ASK {{
      VALUES ?item {{ wd:{wikidata_id} }}
      ?item p:P31 ?st .
      ?st ps:P31 ?cls ;
          wikibase:rank ?rank .
      FILTER(?rank != wikibase:DeprecatedRank)
      ?cls wdt:P279* wd:{category} .
    }}
        """
        time.sleep(SLEEP_TIME)
        sparql.setQuery(query)
        results = sparql.query().convert()
        if results['boolean']:
            wikidata_label = wikidata_categories[category]
            break
    append_to_logfile(entity_text, exists_value, wikidata_label, wikidata_lemma, wikidata_id)
    return exists_value, wikidata_id, wikidata_lemma, wikidata_label
    

recognition_entities = utils.read_machine_analysis(sys.stdin)
line_nbr = 0
entities_list = []
log_dict = read_logfile()
for line_dict in recognition_entities:
    line_nbr += 1
    for entity_label in line_dict:
        for entity_text in line_dict[entity_label]:
           for counter in range(0, line_dict[entity_label][entity_text]):
               exists_value, wikidata_id, wikidata_lemma, wikidata_label = get_wikidata_uri(entity_text, log_dict)
               if not exists_value:
                   print(f"Sorry, no page exists for entity: {entity_text}", file=sys.stderr)
               elif wikidata_label != entity_label:
                   print(f"Sorry, page entity label ({wikidata_label}) does not match {entity_label} for entity {entity_text}", file=sys.stderr)
               else:
                   entities_list.append({"line_nbr": line_nbr,
                                         "entity_label": entity_label,
                                         "entity_text": entity_text,
                                         "wikidata_uri": f"https://www.wikidata.org/wiki/{wikidata_id}"})

pl.DataFrame(entities_list).write_csv(sys.stdout.buffer)
