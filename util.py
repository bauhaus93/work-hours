from datetime import datetime

INTERNAL_DATE_FORMAT = "%Y-%m-%d"


def to_date(date_str):
    return datetime.strptime(date_str, INTERNAL_DATE_FORMAT).date()
