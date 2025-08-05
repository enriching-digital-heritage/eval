#!/usr/bin/env python3
# check_selected_rows.pl: sanity check of randomly selected csv file rows
# usage: checl_selected_rows.pl column_name < file.csv
# 20250727 e.tjongkimsang@esciencecenter.nl

import argparse
import pandas as pd
import polars as pl
import pyarrow
import sys

parser = argparse.ArgumentParser()
parser.add_argument("column_name")
parser.parse_args()
args = parser.parse_args()

df_pd = pd.read_csv(sys.stdin, quotechar='"', engine="python")
df = pl.from_pandas(df_pd)
df_column = df[[args.column_name]]
df_column_duplicated = df_column.is_duplicated()

if not True in df_column_duplicated:
    print(f"no duplicated values in column {args.column_name}")
else:
    print(df_column_duplicated.unique(),
          df_column.filter(df_column_duplicated).sort("Description"))
