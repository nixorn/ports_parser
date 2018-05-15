#!/usr/bin/python3
import argparse
import openpyxl
import re

from grammar import parse_sheet


def extract_data(path):
    wb = openpyxl.load_workbook(path)
    for sheet in wb:
        matrix = [[cell.value for cell in row] for row in sheet.iter_rows()]
        # print(parse_sheet(matrix))
        res = parse_sheet(matrix)
        print(res)
        break

PARSER = argparse.ArgumentParser(description='Port situation xls extraction tool.')


PARSER.add_argument('--file', nargs='?',
                    help='Path to source file.')

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    extract_data(ARGS.file)
    if not ARGS.file:
        PARSER.print_help()

