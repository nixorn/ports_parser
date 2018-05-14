
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


def many(pattern):
    return

def any_of(patterns):
    return

# Row we do not need to structure anchor or data extraction
not_matter = dict(
    pattern=[True],
    getter=labmda x: None
)

title = dict(
    pattern=[True, r"ALGERIAN PORTS SITUATION"],
    getter=labmda x: None)

report_date = dict(
    pattern=[True, r"\d{1,2}/\d{1,2}/\d{4}"],
    getter=labmda x: dict(report_date=x[1])
)

port = dict(
    pattern=[r".+PORTS?"],
    getter=labmda x: dict(port=x[0])
)

vessel_status = dict(
    pattern=[r".+"],
    getter=labmda x: dict(vessel_status=x[0]
)

forthcoming_title = dict(
    pattern=[r"VSLS", r"ETA", r"GRADE", r"QTTY",
             r"LAST PORT", r"NEXT PORT"],
    getter=lambda x: None)

forthcoming_row = dict(
    pattern=[r".+"],
    getter=lambda x: dict(
        vessel_name=x[0],
        eta=x[1],
        grade=x[2],
        quantity=x[3],
        last_port=x[4],
        next_port=x[5]))

drifting_at_anchor_title = dict(
    pattern=[r"VSL", r"GRADE", r"QTTY",
             r"LAST PORT", r"NEXT PORT"],
    getter=lambda x: None))

drifting_at_anchor_row = dict(
    pattern=[r".+"],
    getter=lambda x: dict(
        vessel_name=x[0],
        grade=x[1],
        quantity=x[2],
        last_port=x[3],
        next_port=x[4]))

vessels_alongside_title = dict(
    pattern=[r"PIER"
             r"VSLS",
             r"LAST PORT",
             r"GRADE",
             r"QTTY",
             r"ETS",
             r"NEXT PORT"],
    getter=lambda x: None)

vessels_alongside_row = dict(
    pattern=[r".+"],
    getter=lambda x: dict(
        pier=x[0],
        vessel_name=x[1],
        last_port=x[2],
        grade=x[3],
        quantity=x[4],
        ets=x[5],
        next_port=x[6]))
