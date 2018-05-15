import re
from datetime import datetime

class RowNotMatch(Exception):
    pass

class EOI(Exception):
    """End of input"""
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
    elif entry == None or cell_pattern == None:
        return cell_pattern == entry
    return bool(re.match(cell_pattern, str(entry)))

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


def parser(definition, seq):
    """Top level parser. Should not fall"""
    acc = []
    for parser in definition:
        vals, seq = parser(seq)
        acc += vals
    return acc

def maybe(patterns):
    # Zero or one structure which match pattern list
    def _maybe(seq):
        # have to reassemle iterator if pattern do not match
        seq_ = seq.copy()
        try:
            acc = []
            for patt in patterns:
                # seq in left part should be redifined by patt(seq) call
                # in next loop step patched seq to be used
                vals, seq = patt(seq)
                acc += vals
            return acc, seq
        except RowNotMatch:
            # pattern not match. return origin iterator
            return [], seq_
        except EOI:
            return [], []
    return _maybe

def not_more_than(n, patterns):
    # from zero to n structures which match this pattern list
    def _not_more_than(n, seq):
        last_success_match = seq.copy()
        if n >= 0:
            try:
                acc = []
                for patt in patterns:
                    vals, seq = patt(seq)
                    acc += vals
            except (RowNotMatch, EOI):
                return [], last_success_match
            # parse next structure matches
            vals, seq = _not_more_than(n-1, seq)
            return acc + vals, seq 
        else:
            return [], last_success_match
    return lambda seq: _not_more_than(n, seq)

many = lambda it: not_more_than(100, it)

#######################
# Row patterns
def any_row(seq):
    if not seq:
        raise EOI()
    # print("any row")
    seq.pop(0)
    return [], seq

def empty_row(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if r[:3] == [None, None, None]:
        # print("empty row", r)
        return [], seq
    else:
        raise RowNotMatch("Row do not match empty row pattern")

def title(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([True, r"ALGERIAN PORTS SITUATION"], r):
        # print("title", r)
        return [], seq
    else:
        raise RowNotMatch("Row do not match title pattern")

def report_date(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if type(r[1]) == datetime:
        # print("report_date", r)
        return [{"report_date": r[1]}], seq
    else:
        raise RowNotMatch("Row do not match report date pattern")

def port(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([r".+PORTS?", None], r):
        # print("port", r)
        return [{"port": r[0]}], seq
    else:
        raise RowNotMatch("Row do not match port pattern")

def vessel_status(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([r".+", None], r):
        # print("vessel_status", r)
        return [{"vessel_status": r[0]}], seq
    else:
        raise RowNotMatch("Row do not match vessel_status pattern")

def table_title(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([r".+", r".+", r".+"], r):
        # print("table_title", r)
        return [], seq
    else:
        raise RowNotMatch("Row do not match table_title pattern")

def table_row(seq):
    if not seq:
        raise EOI
    r = seq.pop(0)
    if row_match([r".+", r".+"], r):
        # print("table_row", r)
        return [r], seq
    else:
        raise RowNotMatch("Row do not match table_row pattern")

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

# Нужно сделать так чтобы парсер был одной функцией принимающей одну строку и
# возвращающей либо удачу(значение и остаток ввода) либо неудачу
# Неудача может быть двух видов - несовпадение строки и конец ввода
# У нас есть последовательность строк и последовательность функций, но проблема в том, что последовательность функций не детерминирована
# и зависит от результата парсинга предыдущей функции.
# Таким образом, у нас должен быть некий контроллер, который решает, какой паттерн подавать следующим.
# То есть сидит контроллер и стреляет функциями парсинга, которые применяясь на следующий элемент списка возвращают контроллеру либо значение либо причину по которой облом.
# Должны ли many и maybe быть такими контроллерами? я полагаю да.
# Нужно ли определение рекурсивного контроллера? Я полагаю да.

def parse_sheet(matrix):
    return parser(sheet_structure, matrix)
