import re
from datetime import datetime

column_map = {
    "PIER": "pier",
    "Pier": "pier",
    "PIER N": "pier",
    "VSLS": "vessel_name",
    "VSL": "vessel_name",
    "Vessel": "vessel_name",
    "VESSEL": "vessel_name",
    "ETA": "eta",
    "ETS": "ets",
    "GRADE": "grade",
    "Grade": "grade",
    "QTTY": "quantity",
    "LAST_PORT": "last_port",
    "LAST PORT": "last_port",
    "LAST PORT ": "last_port",
    "NEXT PORT": "next_port",
    "Destination": "next_port",
    "DESTINATION": "next_port",
    "SAILED": "not_matter",
    "Sailed": "not_matter",
    "ETB": "not_matter",
    "Account": "not_matter"
}

# When column names not defined in config
class IllegalColumnNames(Exception):
    pass

class RowNotMatch(Exception):
    pass

# End of input
class EOI(Exception):
    pass

# basic parsers machinery
def cell_match(cell_pattern, entry):
    if type(cell_pattern) == bool:
        return cell_pattern
    elif entry == None or cell_pattern == None:
        return cell_pattern == entry
    return bool(re.match(cell_pattern, str(entry)))

def row_match(row_pattern, row):
    return all([cell_match(patt, cell)
                for patt, cell in zip(row_pattern, row)])

# Parsers have api:
# 1. all parsers get sequence to parse as single argument
# 2. all parsers return pair with parsed value(wrapped into list) and rest of parsed sequence,
#    which have to be processed by next parser
# 3. any parser can throw one of three exceptions - EOI or RowNotMatch
# table parser also can throw IllegalColumnNames.

# Row-level parsers
def any_row(seq):
    if not seq:
        raise EOI()
    seq.pop(0)
    return [], seq

def empty_row(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if r[:3] == [None, None, None]:
        return [], seq
    else:
        raise RowNotMatch("Row {} do not match empty row pattern".format(r))

def title(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([True, r"ALGERIAN PORTS SITUATION"], r):
        return [], seq
    else:
        raise RowNotMatch("Row {} do not match title pattern".format(r))

def report_date(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if type(r[1]) == datetime:
        return [{"report_date": r[1]}], seq
    else:
        raise RowNotMatch("Row {} do not match report date pattern".format(r))

def port(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([r".*PORTS?", None], r):
        return [{"port": r[0]}], seq
    else:
        raise RowNotMatch("Row {} do not match port pattern".format(r))

def port_status(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([True, r"(OPEN|CLOSED.*)"], r):
        return [], seq
    else:
        raise RowNotMatch("Row {} do not match port_status pattern".format(r))

def vessel_status(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    if row_match([r".+", None], r):
        return [{"vessel_status": r[0]}], seq
    else:
        raise RowNotMatch("Row {} do not match vessel_status pattern".format(r))


def table_title(seq):
    if not seq:
        raise EOI()
    r = seq.pop(0)
    possible_col_names = set(column_map.keys())
    mb_title = set(r[:4])
    if mb_title - possible_col_names == set():
        return [r], seq
    else:
        raise RowNotMatch("Row {} do not match table_title pattern."
                          "More likely because {} column names not defined in "
                          "grammar.column_map".format(r, mb_title - possible_col_names))

def table_row(seq):
    if not seq:
        raise EOI
    r = seq.pop(0)
    if r[:2] != [None, None]:
        return [[str(c) for c in r]], seq
    else:
        raise RowNotMatch("Row {} do not match table_row pattern".format(r))

##################
# contextual parsers.
# 1. get list of row parsers or list of contextual parsers or mixed as argument
# 2. returns regular parser with api described above

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

def not_more_than_force(n, patterns):
    # from one to n structures which match this pattern list
    def _not_more_than_force(n, seq):
        acc = []
        for patt in patterns:
            val, seq = patt(seq)
            acc += val
        parser = not_more_than(n-1, patterns)
        rest, seq = parser(seq)
        return acc + rest, seq
    return lambda seq: _not_more_than_force(n, seq)


# from 1 to 100 structures, which match this parser list
many = lambda it: not_more_than_force(100, it)

# Table is regular parser, but using contextual
def table(seq):
    result = []
    title, seq = table_title(seq)
    title = list(filter(None, title.pop()))
    column_indexes = {}
    for idx, k in enumerate(title):
        column_name = column_map.get(k)
        if not column_name:
            raise IllegalColumnNames(
                "Don't know what table header {} means."
                "Define it in grammar.column_names please."\
                .format(k))
        column_indexes[column_name] = idx
    row_parser = not_more_than(1000, ([table_row]))
    rows, seq = row_parser(seq)
    empty_row_parser = not_more_than(50, [empty_row])
    _, seq = empty_row_parser(seq)
    for row in rows:
        result_dict = {}
        for name, index in column_indexes.items():
            result_dict[name] = row[index]
        result.append(result_dict)
    return result, seq

# Top level parser with different api.
# Does not return rest of parsed sequence.
def parser(definition, seq, sheet_name):
    acc = []
    try:
        for parser in definition:
            vals, seq = parser(seq)
            acc += vals
    except EOI:
        print("Done.")
    except RowNotMatch:
        raise Exception("Can not parse sheet {}. Possibly reasons:"
                        "\n1.Malformed data in sheet. Fix data."
                        "\n2.Inadequate structure definition in config.py"\
                        .format(sheet_name))
    except IllegalColumnNames as e:
        raise Exception("Illegal column exception while parsing {} sheet.".format(sheet_name))
    return acc
