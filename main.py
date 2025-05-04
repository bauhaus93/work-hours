#!/usr/bin/env python3

import pandas as pd

from attendance import get_attendance_weekly, get_attendance_daily

def main():
    with pd.ExcelWriter("output.xlsx") as writer:
        df = get_attendances_daily()
        df_cw = get_attendances_weekly()
        df_cw.to_excel(writer, sheet_name="Weeks", index=True)
        df.to_excel(writer, sheet_name="Raw", index=False)

if __name__ == "__main__":
    main()
