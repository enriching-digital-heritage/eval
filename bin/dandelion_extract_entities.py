#!/usr/bin/env python3
# dandelion_extract_entities.pl: extract entities from json output of dandelion
# usage dandelion_extract_entities.pl < dandelion_output.json
# 20250723 e.tjongkimsang@esciencecenter.nl

import ast
import sys

for line in sys.stdin:
    line_data = ast.literal_eval(line.strip())
    if "annotations" in line_data.keys():
        print("Entities:", end=" ")
        for entity_data in line_data["annotations"]:
            if ("http://dbpedia.org/ontology/Location" in entity_data["types"] or 
               "http://dbpedia.org/ontology/Place" in entity_data["types"]):
                print(f"LOC: {entity_data['spot']};", end=" ")
            if ("http://dbpedia.org/ontology/Person" in entity_data["types"] or
                "http://dbpedia.org/ontology/Animal" in entity_data["types"] or
                "http://dbpedia.org/ontology/Deity" in entity_data["types"]):
                print(f"PER: {entity_data['spot']};", end=" ")
        print("")

