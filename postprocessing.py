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
        if type(elem) == dict:
            if "report_date" in elem.keys():
                report_date = elem["report_date"]
            if "vessel_status" in elem.keys():
                vessel_status = elem["vessel_status"]
            if "port" in elem.keys():
                port = elem["port"]
            # Next elem is not table row
            is_table_row = False
        elif type(elem) == list and not is_table_row:
            # looks like this row is table title, so next elem
            # more likely is first row of table body
            is_table_row = True
            # should not be None's in table title
            elem = filter(None, elem)
            column_indexes = {}
            for idx, k in enumerate(elem):
                column_name = column_map.get(k)
                if not column_name:
                    raise Exception("Don't know what table header {} means."
                                    "Define it in config.py please."\
                                    .format(k))
                column_indexes[column_name] = idx
        elif type(elem) == list and is_table_row:
            result_dict = {}
            for name, index in column_indexes.items():
                result_dict[name] = elem[index]
            result_dict["report_date"] = report_date.strftime("%m/%d/%Y")
            result_dict["port"] = port
            result_dict["vessel_status"] = vessel_status
            acc_list.append(result_dict)
        else:
            raise Exception("Results of parsing contains not list or dict values."
                            "Should never happen.")
    result = [OutputRow(**res_row).pprint() for res_row in acc_list]
    return result
