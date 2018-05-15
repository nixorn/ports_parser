import re
from datetime import datetime
"""
Patterns is things we matching rows. Pattern have two parts
1. Pattern itself, to understand match row to this pattern or not.
2. Getter, which get from row values.

True means default match."""


class RowNotMatch(Exception):
    pass

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
    elif cell_pattern == None:
        return cell_pattern == entry
    return bool(re.match(cell_pattern, entry))

def row_match(row_pattern, row):
    return all([cell_match(patt, cell)
                for patt, cell in zip(row_pattern, row)])

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


def maybe(patterns):
    # Zero or one structure which match pattern list
    def _maybe(it):
        # have to reassemle iterator if pattern do not match
        it_lst = list(it)
        it = iter(it_lst)
        try:
            for patt in patterns:
                for res in patt(it):
                    yield res
        except RowNotMatch:
            # pattern not match. return origin iterator
            yield None, iter(it_lst)
    return _maybe

def not_more_than(n, patterns):
    # from zero to n structures which match this pattern list
    def _not_more_than(n, it):
        last_success_match = list(it)
        if n >= 0:
            it = iter(last_success_match)
            try:
                acc = []
                for patt in patterns:
                    for res in patt(it):
                        yield res
                # parse next structure matches
                for val, _it in _not_more_than(n-1, it):
                    yield val, it
            except RowNotMatch:
                yield None, iter(last_success_match)
        else:
            yield None, iter(last_success_match)
    return lambda it: _not_more_than(n, it)

many = lambda it: not_more_than(100, it)

def any_row(it):
    it.__next__()
    yield None, it

def empty_row(it):
    r = it.__next__()
    print("empty_row", r)
    if r[:3] == [None, None, None]:
        yield None, it
    else:
        raise RowNotMatch("Row do not match empty row pattern")

def title(it):
    r = it.__next__()
    print("title", r)
    if row_match([True, r"ALGERIAN PORTS SITUATION"], r):
        yield None, it
    else:
        raise RowNotMatch("Row do not match title pattern")

def report_date(it):
    r = it.__next__()
    print("report_date", r)
    if type(r[1]) == datetime:
        yield {"report_date": r[1]}, it
    else:
        raise RowNotMatch("Row do not match report date pattern")

def port(it):
    r = it.__next__()
    print("port", r)
    if row_match([r".+PORTS?", None], r):
        yield {"port": r[0]}, it
    else:
        raise RowNotMatch("Row do not match port pattern")

def vessel_status(it):
    r = it.__next__()
    print("vessel_status", r)
    if row_match([r".+", None], r):
        yield {"vessel_status": r[0]}, it
    else:
        raise RowNotMatch("Row do not match vessel_status pattern")

def table_title(it):
    r = it.__next__()
    print("table_title", r)
    if row_match([r".+", r".+", r".+"]):
        yield None, it
    else:
        raise RowNotMatch("Row do not match table_title pattern")

def table_row(it):
    r = it.__next__()
    print("table_row", r)
    if row_match([r".+", r".+", r".+"]):
        yield r, it
    else:
        raise RowNotMatch("Row do not match table_row pattern")

sheet_structure = [
    empty_row, title, report_date, empty_row,
    many([port, any_row, any_row,
          many([
              vessel_status, maybe([empty_row]),
              table_title, many([table_row]), not_more_than(20, [empty_row])])])]

def parse_sheet(matrix):
    it = iter(matrix)
    for parser in sheet_structure:
        list(parser(it))
