import datetime
import pandas as pd
import re

min_date = datetime.date(2001, 1, 1)
max_date = datetime.datetime.today()
DEFAULT_DATE_RANGE = pd.date_range(min_date, max_date)


def mock_query(mocker, response):
    return mocker.get(
        re.compile(".*query/None*."),
        request_headers={
            "content-type": "application/json",
            "x-api-key": "api-key-test",
        },
        json=response,
    )


def find_alert_date(
    alert_response, alert_date_aoi, alert_date_type=None, alert_year=None, adm1_val=None
):
    # now that we're filling in missing dates, can't rely on indexes to
    # pull specific dates from the alert response (like data[-1])

    if alert_year:
        filtered_resp = [
            x
            for x in alert_response
            if x["year"] == alert_year and x[alert_date_type] == alert_date_aoi
        ]

    elif adm1_val:
        filtered_resp = [
            x
            for x in alert_response
            if x["day"] == alert_date_aoi and x["adm1"] == adm1_val
        ]

    else:
        filtered_resp = [x for x in alert_response if x["day"] == alert_date_aoi]

    if len(filtered_resp) > 1:
        raise ValueError(
            "Filtered response has more than one value for particular time period"
        )

    return filtered_resp[0]


def count_time_intervals(time_interval):
    # unclear why pd.date_range(start, end, freq='w') doesn't produce the
    # same results as the code below (currently off by 4 weeks)
    date_df = pd.DataFrame(DEFAULT_DATE_RANGE, columns=["alert_date"])
    date_df["year"] = date_df.alert_date.dt.year

    # I'd like to use the more flexible date_df.alert_date.dt.to_period(<period_str>) here
    # but it gives different results than the code below, which is more standard
    if time_interval == "week":
        date_df["time_interval"] = date_df.alert_date.dt.week
    elif time_interval == "month":
        date_df["time_interval"] = date_df.alert_date.dt.month
    elif time_interval == "quarter":
        date_df["time_interval"] = date_df.alert_date.dt.quarter
    else:
        date_df["time_interval"] = 1

    grouped = date_df.groupby(["year", "time_interval"]).size().reset_index()

    return len(grouped)
