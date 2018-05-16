from grammar import *

column_map = {
    "PIER": "pier",
    "VSLS": "vessel_status",
    "VSL": "vessel_status",
    "ETA": "eta",
    "ETS": "ets",
    "GRADE": "grade",
    "QTTY": "quantity",
    "LAST_PORT": "last_port",
    "NEXT PORT": "next_port"
}


sheet_structure = [
    empty_row, title, report_date, empty_row,
    many([port, any_row, any_row,
          many([
              vessel_status,
              maybe([empty_row]),
              table_title, many([table_row]),
              not_more_than(50, [empty_row]),
              # sometimes are two tables together with no vessel_status subtitle
              maybe([table_title, many([table_row]), not_more_than(50, [empty_row])])
          ])])]
