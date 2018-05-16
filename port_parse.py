#!/usr/bin/python3
import argparse
import openpyxl
import re

from config import sheet_structure
from grammar import parser
from postprocessing import bring_beauty


def extract_data(path):
    wb = openpyxl.load_workbook(path)
    parsed_sheets = []
    for sheet, sheet_name in zip(wb, wb.sheetnames):
        matrix = [[cell.value for cell in row] for row in sheet.iter_rows()]
        parsed_sheets += parser(sheet_structure, matrix, sheet_name)
    return parsed_sheets


PARSER = argparse.ArgumentParser(description='Port situation xls extraction tool.')


PARSER.add_argument('--file', nargs='?',
                    help='Path to source file.')

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    weekly_formatted = extract_data(ARGS.file)
    print(
        "ReportDate;" +\
        "Port;" +\
        "Vesselstatus;" +\
        "Pier;" +\
        "Vesselname;" +\
        "ETA;" +\
        "ETS;" +\
        "Grade;" +\
        "Quantity;" +\
        "LastPort;" +\
        "NextPort")
    for row in bring_beauty(weekly_formatted):
        print(";".join(row))
    if not ARGS.file:
        PARSER.print_help()

