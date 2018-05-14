#!/usr/bin/python3
import argparse
import openpyxl
import re

import patterns


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

