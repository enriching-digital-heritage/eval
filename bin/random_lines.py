#!/usr/bin/env python3
# random_lines: generate n random lines from csv file on STDIN
# usage: random_lines max_selected column_name < file_in.csv > file_out.csv
# arguments: max_selected: number of rows/lines to select
#            column_name: column_name where to avoid duplicates
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
    parser.add_argument("max_selected")
    parser.add_argument("column_name")
    parser.parse_args()
    return parser.parse_args()


def read_csv_file_from_stdin():
    df_pd = pd.read_csv(sys.stdin, quotechar='"', engine="python") # expects header
    return pl.from_pandas(df_pd)

def select_lines_from_df(df, n, column_name):
    selected_list = len(df) * [False]
    nbr_of_selected = 0
    seen_list = []
    while nbr_of_selected < n and nbr_of_selected < len(df):
        random_id = random.randint(0, len(df) - 1)
        if not selected_list[random_id] and not df[column_name][random_id] is None: 
            column_value = df[column_name][random_id][:-10]
            if not column_value in seen_list:
                selected_list[random_id] = True
                if column_name != "":
                     seen_list.append(column_value)
                nbr_of_selected += 1
    return df.filter(selected_list)


args = read_command_line_args()
df = read_csv_file_from_stdin()
df_selected = select_lines_from_df(df, int(args.max_selected), args.column_name)
remove_newlines(df_selected).write_csv(sys.stdout)
        
sys.exit(0)
