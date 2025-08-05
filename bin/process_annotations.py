#!/usr/bin/env python3
# process_annotations: convert named-entity annotations to text
# expected input format: PERSON: John; GPE: Paris; LOC: Vienna
# usage: process_annotations < file
# 20250718 e.tjongkimsang@esciencecenter.nl

import regex
import sys

count = 1
for line in sys.stdin:
    if regex.search("^\s*Entities:", line):
        tokens = line.strip().split()
        print("{", end="")
        print(f'id="{count}",', end="")
        for i in range(0, len(tokens)):
            if regex.search("^[A-Z]+:$", tokens[i]):
                inc = 1
                tokens[i + inc] = tokens[i + inc].strip(';')
                print(f'"{tokens[i]}": "{tokens[i + inc]}', end="")
                inc = 2
                while i + inc < len(tokens) and not regex.search("^[A-Z]+:$", tokens[i + inc]):
                    tokens[i + inc] = tokens[i + inc].strip(';')
                    print(f' {tokens[i + inc]}', end="")
                    inc += 1
                print('",', end=" ")
                i += inc - 1
        print("}")
        count += 1
