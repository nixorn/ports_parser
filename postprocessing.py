from datetime import datetime
from config import column_map

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

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def pprint(self):
        return map(
            lambda x: x if x else "",
            [self.report_date,
             self.port,
             self.vessel_status,
             self.pier,
             self.vessel_name,
             self.eta,
             self.ets,
             self.grade,
             self.quantity,
             self.last_port,
             self.next_port])

def bring_beauty(target_list):
    if not target_list:
        return acc_list
    acc_list = []
    is_table_row = False
    # print(target_list)
    # default values
    report_date = datetime.fromordinal(1)
    port = "UNPARSED"
    vessel_status = "UNPARSED"
    column_indexes = {}
    for elem in target_list:
        if "report_date" in elem.keys():
            report_date = elem["report_date"]
        elif "vessel_status" in elem.keys():
            vessel_status = elem["vessel_status"]
        elif "port" in elem.keys():
            port = elem["port"]
        else:
            elem["report_date"] = report_date.strftime("%m/%d/%Y")
            elem["port"] = port
            elem["vessel_status"] = vessel_status
            acc_list.append(elem)
    result = [OutputRow(**res_row).pprint() for res_row in acc_list]
    return result
