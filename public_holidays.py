from datetime import datetime, timedelta

from util import INTERNAL_DATE_FORMAT

EASTER_SUNDAY = {"2024": "03-31", "2025": "04-20"}
FIXED_DAYS = {
    "01-01": "Neujahr",
    "01-06": "Hl. 3 Könige",
    "03-19": "St. Josef",
    "05-01": "Staatsfeiertag",
    "08-15": "Mariä Himmelfahrt",
    "10-26": "Nationalfeiertag",
    "11-01": "Allerheiligen",
    "12-08": "Mariä Empfängnis",
    "12-25": "Weihnachtstag",
    "12-26": "Stefanitag",
}


def get_public_holidays(start_date):
    result = {}
    for year in range(start_date.year, datetime.now().year + 1):
        for dm, reason in FIXED_DAYS.items():
            dt = datetime.strptime(f"{year}-{dm}", INTERNAL_DATE_FORMAT).date()
            result[dt] = reason
        for dt, reason in _get_easter_dependend_days(year).items():
            result[dt] = reason
    return result


def _get_easter_dependend_days(year):
    offsets = {
        1: "Ostermontag",
        39: "Christi Himmelfahrt",
        50: "Pfingsten",
        60: "Fronleichnam",
    }
    easter_sunday = datetime.strptime(
        f"{year}-{EASTER_SUNDAY[str(year)]}", INTERNAL_DATE_FORMAT
    )
    return dict(
        ((easter_sunday + timedelta(days=o)).date(), r) for o, r in offsets.items()
    )
