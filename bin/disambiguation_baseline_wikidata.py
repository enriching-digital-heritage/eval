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
SLEEP_TIME_GET_LABEL = 61
SLEEP_TIME_FETCH_PAGE = 5

def read_logfile():
    """Read previously looked up Wikidata data from logfile and return them in a dict"""
    log_df = pl.read_csv(LOGFILE_NAME)
    return {row_dict["entity_text"]: row_dict for row_dict in log_df.to_dicts()}


def append_to_logfile(entity_text, exists_value, wikidata_id, wikidata_label, wikidata_lemma, log_dict):
    """Add new Wikidata information to logfile and current log dictionary"""
    log_dict[entity_text] = {"exists_value": "True" if exists_value else "",
                             "wikidata_label": wikidata_label,
                             "wikidata_lemma": wikidata_lemma,
                             "wikidata_id": wikidata_id,
                             "entity_text": entity_text}
    with open(LOGFILE_NAME, "a") as outfile:
        pl.DataFrame([log_dict[entity_text]]).write_csv(outfile, include_header=False)
        outfile.close()


def get_data_from_wikidata(entity_text):
    """Read Wikidata data on entity_text and return it"""
    params = {
        'action': 'wbsearchentities',
        'language': 'en',
        'format': 'json',
        'search': entity_text 
    }
    url = 'https://www.wikidata.org/w/api.php'
    print(entity_text, url)
    time.sleep(SLEEP_TIME_FETCH_PAGE)
    wikidata_data = requests.get(url, params=params)
    return wikidata_data


def get_wikidata_label(wikidata_id, entity_label):
    """Find out possible entity label (PER/LOC) of Wikidata page with id wikidata_id. Expensive"""
    endpoint = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    if entity_label == "PER":
        wikidata_categories = {"Q5": "PER", "Q178885": "PER"} 
    elif entity_label == "LOC":
        wikidata_categories = {"Q123349660": "LOC", "Q17334923": "LOC", "Q2221906": "LOC"}
    else:
        wikidata_categories = {}
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
        time.sleep(SLEEP_TIME_GET_LABEL)
        sparql.setQuery(query)
        print(f"firing sparql query for {wikidata_id} with category {category} after sleeping {SLEEP_TIME_GET_LABEL} seconds")
        results = sparql.query().convert()
        if results['boolean']:
            wikidata_label = wikidata_categories[category]
            break
    return wikidata_label


def get_wikidata_data(entity_text, entity_label, log_dict):
    """Get Wikidata data for entity_text and return them. Lookup up to two alternatives if the entity label does not match. Very expensive"""
    if entity_text in log_dict:
        return(log_dict[entity_text]["exists_value"],
               log_dict[entity_text]["wikidata_id"],
               log_dict[entity_text]["wikidata_label"],
               log_dict[entity_text]["wikidata_lemma"])
    wikidata_data = get_data_from_wikidata(entity_text)
    print("1")
    if len(wikidata_data.json()["search"]) < 1:
        print("2")
        append_to_logfile(entity_text, "", "", "", "", log_dict)
        return "", "", "", ""
    print("3")
    exists_value = True
    wikidata_data_id = 0
    page_info = wikidata_data.json()["search"][0]
    wikidata_id = page_info["id"]
    wikidata_label = get_wikidata_label(wikidata_id, entity_label)
    wikidata_lemma = page_info["display"]["label"]["value"]
    print([x["id"] for x in wikidata_data.json()["search"]])
    print("4", wikidata_data_id, entity_label, f'"{wikidata_label}"', wikidata_lemma, wikidata_id)
    if wikidata_label != entity_label and entity_label in ["LOC", "PER"] and len(wikidata_data.json()["search"]) > 1:
        page_info = wikidata_data.json()["search"][1]
        reserve_label = get_wikidata_label(page_info["id"], entity_label)
        print(f"5 also tested {page_info['id']}: \"{reserve_label}\"") 
        if reserve_label == entity_label:
            wikidata_id = page_info["id"]
            wikidata_label = reserve_label
            wikidata_lemma = page_info["display"]["label"]["value"]
        elif len(wikidata_data.json()["search"]) > 2:
            page_info = wikidata_data.json()["search"][2]
            reserve_label = get_wikidata_label(page_info["id"], entity_label)
            print(f"6 also tested {page_info['id']}: \"{reserve_label}\"")
            if reserve_label == entity_label:
                wikidata_id = page_info["id"]
                wikidata_label = reserve_label
                wikidata_lemma = page_info["display"]["label"]["value"]

    print("7", wikidata_data_id, entity_label, f'"{wikidata_label}"', wikidata_lemma, wikidata_id)
    append_to_logfile(entity_text, exists_value, wikidata_id, wikidata_label, wikidata_lemma, log_dict)
    return exists_value, wikidata_id, wikidata_label, wikidata_lemma
    

recognition_entities = utils.read_machine_analysis(sys.stdin)
line_nbr = 0
entities_list = []
log_dict = read_logfile()
for line_dict in recognition_entities:
    line_nbr += 1
    for entity_label in line_dict:
        for entity_text in line_dict[entity_label]:
           for counter in range(0, line_dict[entity_label][entity_text]):
               exists_value, wikidata_id, wikidata_label, wikidata_lemma = get_wikidata_data(entity_text, entity_label, log_dict)
               if not exists_value:
                   print(f"Sorry, no page exists for entity: {entity_text}", file=sys.stderr)
               elif wikidata_label != entity_label:
                   print(f"Sorry, page entity label ({wikidata_label}) does not match {entity_label} for entity {entity_text}/{wikidata_lemma}", file=sys.stderr)
               else:
                   entities_list.append({"line_nbr": line_nbr,
                                         "entity_label": entity_label,
                                         "entity_text": entity_text,
                                         "wikidata_uri": f"https://www.wikidata.org/wiki/{wikidata_id}"})

pl.DataFrame(entities_list).write_csv(sys.stdout.buffer)
