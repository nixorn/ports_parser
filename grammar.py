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
            acc = []
            for patt in patterns:
                acc.append(patt(it))
            for val, _it in acc:
                yield val, _it
        except RowNotMatch:
            # pattern not match. return original iterator
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
                    acc.append(patt(it))
                for res in acc:
                    yield acc
                # parse next structure matches
                for res in _not_more_than(n-1, it):
                    yield res
            except RowNotMatch:
                yield None, iter(last_success_match)
        else:
            yield None, iter(last_success_match)
    return lambda it : _not_more_than(n, it)

many = lambda it: not_more_than(500, it)

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
    if row_match([r".+", r""], r):
        yield {"vessel_status": r[0]}, it
    else:
        raise RowNotMatch("Row do not match vessel_status pattern")

# table = [table_title, many(table_row)]
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
              vessel_status, maybe(empty_row),
              table_title, many(table_row), not_more_than(20, empty_row)])])]

def parse_sheet(matrix):
    it = iter(matrix)
    for parser in sheet_structure:
        print(list(parser(it)))
    # def parse_struct(getters, it, acc):
    #     if getters:
    #         getter = getters.pop(0)
    #         result = getter(it)
    #         if callable(result):
    #             yield parse_struct(result, it, acc)
    #         elif type(result) == NoneType:
    #             yield None
    #         elif type(result) == dict:
    #             yield parse_struct(getters, it, acc + [result])
    #     else:
    #         yield acc
    # return parse_struct(sheet_structure, it, [])
