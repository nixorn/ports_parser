from grammar import *

sheet_structure = [
    empty_row, title, report_date, empty_row,
    # First record
    port, any_row, port_status,
    many([
        vessel_status,
        maybe([empty_row]),
        table,
        # sometimes are two tables together with no vessel_status subtitle
        maybe([table])]),
    many([port, port_status, empty_row,
          many([
              vessel_status,
              maybe([empty_row]),
              table,
              maybe([table])
          ])])]
