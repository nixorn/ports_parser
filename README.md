# Ports parser

Script for extracting information from .xlsx of certain format. Code inspired by haskell parsers.

## Requirements
1. python3
2. openpyxl

You can install openpyxl via command:
`pip3 install openpyxl`

## Using
```
cd ports_parser
python3 port_parse.py --file Cases\ to\ be\ extracted.xlsx >> result.csv
```

## Constraints
### No empty rows in tables body
In Cases to be extracted.xlsx lot of places which looks like:


| VSLS            | GRADE  |  QTTY | LAST PORT | NEXT PORT |
| --------------- | ------ | ----- | --------- | --------- |
|                 |        |       |           |           |
| NISSOS HERACLEA | NAPHTA | 85000 |           |          |


Row after title is empty. Empty row may be between two filled rows. I have no idea how to handle these rows. Script throws error while encounter this. If you see error like
```
Exception: Can not parse sheet P1. Possibly reasons:
1.Malformed data in sheet. Fix data.
2.Inadequate structure definition in config.py
```
you have to go into your file and delete all empty rows in tables bodies by hand.

### xlsx only
I used openpyxl, it does not support xls.

### You should mention all column names from file you parse in grammar.column_map

Lets imagine, we have fragment like this somewhere in file:


| VESSELS SAILED |       |         |        |      |             |
| -------------- | ----- | ------- | ------ | ---- | ----------- |
| Vessel         | Grade | Account | Sailed | QTTY | Destination |


If any of column names (Vessel, Grade, etc) not described in grammar.column_map parser SILENTLY will no extract data from this occurrence to end of sheet. Have to fix this in next versions.
