#!/usr/bin/env python3
# annotations_to_iob.py: convert annotation format to iob1 format
# usage: annotations_to_iob.py < file_in.txt > file_out.txt
# note: as far was we know our data does not contain successive entities of the same type
# 20250808 e.tjongkimsang@esciencecenter.nl

import sys

for line in sys.stdin:
    line = line.strip()
    if line == "":
        print(line)
    else:
        label, token = line.split()
        if label == "p":
            print(f"{token} I-PER")
        elif label == "l":
            print(f"{token} I-LOC")
        else:
            print(f"{token} O")
