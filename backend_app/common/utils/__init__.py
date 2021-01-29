import datetime
import json


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _json_serial(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def get_api_default_permissions(self):
    from rest_framework.decorators import permission_classes
    from rest_framework.permissions import IsAdminUser, IsAuthenticated
    # print(self.action)
    if self.action in ['list', 'retrieve']:
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsAdminUser]
    return [permission() for permission in permission_classes]


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def get_field_data(qs, index=0, field=''):
    try:
        if index >= 0:
            res = getattr(qs[index], field)
        else:
            res = getattr(qs.latest(field), field)
    except Exception:
        res = None

    return res
