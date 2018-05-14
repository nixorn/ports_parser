
"""
Patterns is things we matching rows. Pattern have two parts
1. Pattern itself, to understand match row to this pattern or not.
2. Getter, which get from row values.

True means default match."""


class OutputRow(object):
    """Result of parsing."""
    report_date = None
    port = None
    vessel_status = None
    pier = None
    vessel_name = None
    eta = None
    ets = None
    grade = None
    quantity = None
    last_port = None
    next_port = None

def cell_match(cell_pattern, entry):
    if type(cell_pattern) == bool:
        return cell_pattern
    return bool(re.match(cell_pattern, entry))

def row_match(row_pattern, row):
    return all([cell_match(patt, cell) for patt,
                cell in zip(pattern, row)])

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

def maybe(pattern):
    return

def many(pattern):
    return

# Row we do not need to structure anchor or data extraction
not_matter = [True]

empty_line = ["", "", ""]

title = [True, r"ALGERIAN PORTS SITUATION"]

report_date = [True, r"\d{1,2}/\d{1,2}/\d{4}"]

port = [r".+PORTS?", None]

vessel_status = [r".+"]

table_title = []
table_row = []


sheet = [empty_line, title, report_date, empty_line,
         many([port, not_matter, not_matter,
               many([
                   vessel_status, maybe(empty_line), table_title,
                   many(table_row), many(empty_line)
               ])])]

def parse_structure(matrix):
    it = iter(matrix)
    def _parse_structure(definition, it):
        if

        else: _parse_structure(definition, it)
