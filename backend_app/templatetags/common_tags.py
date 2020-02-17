from django import template
from django.utils import timezone
from cpe import CPE as _CPE
register = template.Library()


@register.filter
def cvss_color(value):
    """Return the default color for CVSS score"""
    if float(value) >= 9.0: return '#B71C1C'  # red darken-4
    elif float(value) >= 7.0: return '#F44336'  # red
    elif float(value) >= 4.0: return '#FF9800'  # orange
    elif float(value) >= 0.1: return '#FFEB3B'  # yellow
    return '#9E9E9E'  # grey


@register.filter
def rating_color(value):
    """Return the default color for Rating score"""
    if not str(value).isnumeric():
        return '#9E9E9E'
    if int(value) >= 80: return '#F44336'  # red
    elif int(value) >= 60: return '#FF9800'  # orange
    elif int(value) >= 40: return '#FFEB3B'  # yellow
    elif int(value) >= 0: return '#03A9F4'  # light-blue
    return '#9E9E9E'  # grey


@register.filter
def parse_cpe(cpe):
    """Return the CPE parsed data"""
    return _CPE(cpe)


@register.filter
def keyvalue(dict, key):
    """Return the value in a dict using supplied key."""
    if key not in dict.keys():
        return None
    return dict[key]


@register.filter
def smartdate(date):
    """Return a formated datetime."""
    if date.date() == timezone.now().date():
        return timezone.localtime(date).strftime("%H:%M:%S")
    else:
        return date.date().isoformat()


@register.filter
def sort_by(queryset, order_args):
    """Return a queryset sorted by supplied args."""
    if isinstance(queryset, set):
        return sorted(queryset)
    if order_args is None:
        return queryset
    orders = [arg.strip() for arg in order_args.split(',')]
    return queryset.order_by(*orders)


@register.filter
def joinby(value, arg):
    """Return the joined strings."""
    if value:
        return arg.join(value)
    else:
        return ""


@register.filter
def get_time_diff(finish_at, started_at):
    """Return the timedelta betweed 2 dates."""
    if finish_at is None or started_at is None:
        return "-"

    return finish_at - started_at
