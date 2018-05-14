#!/usr/bin/python3
import argparse
import openpyxl
import re

import patterns


class OutputRow(object):
    """Result of parsing."""
    report_date = None
    port = None
    vesselstatus = None
    pier = None
    vesselname = None
    eta = None
    ets = None
    grade = None
    quantity = None
    last_port = None
    next_port = None

def cell_match(cell_pattern, entry):
    return bool(re.match(cell_pattern, entry))

def row_match(row_pattern, row):
    return all([cell_match(patt, cell) for patt, cell in zip(pattern, row)])

def parse_structures():
    pass

def extract_data(path):
    try:
        wb = openpyxl.load_workbook(path)
        for sheet in wb:
            matrix = [[cell.value for cell in row] for row in sheet.iter_rows()]
            print(matrix)
    except:
        print("Incorrect filepath")
        return

PARSER = argparse.ArgumentParser(description='Port situation xls extraction tool.')


PARSER.add_argument('--file', nargs='?',
                    help='Path to source file.')

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    extract_data(ARGS.file)
    if not ARGS.file:
        PARSER.print_help()

