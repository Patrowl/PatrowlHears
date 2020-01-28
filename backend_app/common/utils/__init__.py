import datetime


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _json_serial(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
