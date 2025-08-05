#!/usr/bin/env python3
# select_column.pl: select column from csv file by name
# usage: select_column.pl column_name < file_in.csv
# 20250715 e.tjongkimsang@esciencecenter.nl

import argparse
import pandas as pd
import polars as pl
import random
import sys

def remove_newlines(df):
    return df.with_columns([pl.col(col).str.replace_all(r" *\r?\n *", ". ")
                            for col in df.columns
                            if df[col].dtype == pl.String
                           ])

def read_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("column_name")
    parser.parse_args()
    return parser.parse_args()


def read_csv_file_from_stdin():
    df_pd = pd.read_csv(sys.stdin, quotechar='"', engine="python") # expects header
    return pl.from_pandas(df_pd)

args = read_command_line_args()
df = read_csv_file_from_stdin()
df = remove_newlines(df)
df[[args.column_name]].write_csv(sys.stdout)
        
sys.exit(0)
