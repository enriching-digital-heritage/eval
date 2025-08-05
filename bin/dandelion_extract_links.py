#!/usr/bin/env python3
# dandelion_extract_entities.pl: extract entities from json output of dandelion
# usage dandelion_extract_entities.pl < dandelion_output.json
# 20250723 e.tjongkimsang@esciencecenter.nl

import ast
import regex
import sys

for line in sys.stdin:
    line_data = ast.literal_eval(line.strip())
    if "annotations" in line_data:
        for entity_data in line_data["annotations"]:
            if regex.search("^[A-Z]", entity_data['spot']):
                print(entity_data['spot'], entity_data['lod'])

