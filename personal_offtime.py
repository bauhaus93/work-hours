import logging
from datetime import timedelta

import yaml

from util import to_date


def _parse_entries(entries):
    result = {}
    for entry in entries:
        if "reason" not in entry:
            raise ValueError("Expected to find a reason for entry, but got none!")
        if "at" in entry:
            result[entry["at"]] = entry["reason"]
        elif "from" in entry and "to" in entry:
            curr = entry["from"]
            end = entry["to"]
            if curr > end:
                raise ValueError(
                    f"Start date must not be after end date: Got start date={curr}, end date={end}"
                )
            while curr <= end:
                result[curr] = entry["reason"]
                curr += timedelta(days=1)
        else:
            raise ValueError(
                "Expected entry to either have an 'at' or 'from'/'to' fields, but found none!"
            )

    return result


def get_sick_days(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if "sick_days" not in data:
        print(f"No sick days found in {filename}!")
        return {}
    return _parse_entries(data["sick_days"])


def get_personal_holidays(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if "personal_holidays" not in data:
        print(f"No personal holidays found in {filename}!")
        return {}
    return _parse_entries(data["personal_holidays"])
