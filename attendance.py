#!/usr/bin/env python3

from datetime import datetime, timedelta

import pandas as pd

from personal_offtime import get_personal_holidays, get_sick_days
from public_holidays import get_public_holidays
from util import INTERNAL_DATE_FORMAT

START_DATE = datetime(year=2024, month=4, day=1).date()

DATETIME_FORMAT = "%d %b %Y"
DATETIME_FORMAT_ALT = "%d %b. %Y"


def read_days(filename):
    with open(filename, "r") as f:
        return set(
            datetime.strptime(e.strip(), INTERNAL_DATE_FORMAT).date()
            for e in f
            if (e.strip() and "#" not in e)
        )


SICK_DAYS = get_sick_days("personal_offtime.yml")
PERSONAL_HOLIDAYS = get_personal_holidays("personal_offtime.yml")
PUBLIC_HOLIDAYS = get_public_holidays(START_DATE)

OFF_DAYS = SICK_DAYS | PUBLIC_HOLIDAYS | PERSONAL_HOLIDAYS


def format_date(row):
    try:
        return datetime.strptime(row["Date"].strip(), DATETIME_FORMAT).date()
    except ValueError:
        return datetime.strptime(row["Date"].strip(), DATETIME_FORMAT_ALT).date()


def to_calendar_week(row):
    return f"{row['Date'].year}_KW{int(row['Date'].strftime('%W')) + 1:02d}"


def to_reason(row):
    if row["Date"] in SICK_DAYS:
        return "SICK"
    if row["Date"] in PUBLIC_HOLIDAYS:
        return "PUBLIC_HOLIDAY"
    if row["Date"] in PERSONAL_HOLIDAYS:
        return "PERSONAL_HOLIDAY"
    return ""


def to_details(row):
    return OFF_DAYS.get(row["Date"], "")


def to_attendance_target(row):
    if row["Date"] in OFF_DAYS:
        return 0

    dow = int(datetime.strftime(row["Date"], "%w"))
    if dow in {0, 6}:
        return 0
    if dow == 5:
        return 6
    return 8.5


def to_delta(row):
    return row["Worked Hours"] - row["Target Hours"]


def get_missing_dates(df):
    def _iter_dates():
        d = START_DATE
        end = datetime.now().date()
        while d <= end:
            yield d
            d = d + timedelta(days=1)

    return sorted(list(set((_iter_dates())) - set(df["Date"])))


def add_missing_dates(df):
    missing_dates = get_missing_dates(df)

    df_missing = pd.DataFrame(
        {"Date": missing_dates, "Worked Hours": [0] * len(missing_dates)}
    )

    return pd.concat([df, df_missing]).reset_index(drop=True)


def get_attendance_daily(filename):
    with pd.ExcelFile(filename) as file:
        df = pd.read_excel(file, "Worked Hours", skiprows=range(1, 3))

        df.columns = ["Date", "Worked Hours"]
        df["Date"] = df.apply(format_date, axis=1)
        df["Worked Hours"] = df["Worked Hours"].round(3)
        df = add_missing_dates(df)
        df.set_index("Date")
        df = df.sort_values("Date")
        df["CW"] = df.apply(
            to_calendar_week,
            axis=1,
        )
        df["DOW"] = df.apply(lambda row: datetime.strftime(row["Date"], "%A"), axis=1)
        df = df[["Date", "CW", "DOW", "Worked Hours"]]

        df["Target Hours"] = df.apply(to_attendance_target, axis=1)
        df["Delta"] = df.apply(to_delta, axis=1)
        df["Reason"] = df.apply(to_reason, axis=1)
        df["Details"] = df.apply(to_details, axis=1)
        return df

def get_attendance_weekly(filename=None, df=None):
    if df is None:
        df = get_attendance_daily(filename)
    grp = df.groupby("CW")
    df_cw = grp["Target Hours"].sum().to_frame()
    df_cw["Worked Hours"] = grp["Worked Hours"].sum()
    df_cw["Delta"] = grp["Delta"].sum()
    return df_cw
