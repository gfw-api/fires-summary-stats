import datetime

from fireSummary.services import QueryConstructorService

dataset_name = "fires"
today = datetime.datetime.today().strftime("%Y-%m-%d")


def build_params(**kwargs):
    params = {}
    params["period"] = kwargs.get("period", f"2001-01-01,{today}")
    params["aggregate_by"] = kwargs.get("aggregate_by")
    params["aggregate_time"] = kwargs.get("aggregate_time")
    params["aggregate_admin"] = kwargs.get("aggregate_admin")
    params["fire_type"] = kwargs.get("fire_type")
    params["polyname"] = kwargs.get("polyname")
    params["iso_code"] = kwargs.get("iso_code")
    params["adm1_code"] = kwargs.get("adm1_code")
    params["adm2_code"] = kwargs.get("adm2_code")

    if params["aggregate_by"] or params["aggregate_time"] or params["aggregate_admin"]:
        params["aggregate_values"] = True
    else:
        params["aggregate_values"] = False

    return params


def test_sql_admin0():
    # give a valid period
    kwargs = {"period": "2012-01-01,2015-01-01", "polyname": "admin", "iso_code": "IDN"}
    params = build_params(**kwargs)

    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        "(alert_date >= '2012-01-01' AND alert_date <= '2015-01-01')"
    )

    assert sql == correct_sql


def test_sql_no_period():
    kwargs = {"polyname": "admin", "iso_code": "IDN"}
    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}')"
    )

    assert sql == correct_sql


def test_sql_agg_by_day():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "day"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY alert_date"
    )

    assert sql == correct_sql


def test_sql_agg_by_week():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "week"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY alert_date"
    )

    assert sql == correct_sql


def test_sql_agg_by_month():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "month"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY alert_date"
    )

    assert sql == correct_sql


def test_sql_agg_by_year():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "year"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY alert_date"
    )

    assert sql == correct_sql


def test_sql_agg_by_adm1():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "adm1"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, adm1 FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY adm1"
    )

    assert sql == correct_sql


def test_sql_agg_by_adm2():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "aggregate_by": "adm2"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, adm1, adm2 FROM data WHERE polyname = 'admin' AND iso = 'IDN' "
        f"AND (alert_date >= '2001-01-01' AND alert_date <= '{today}') "
        "GROUP BY adm1, adm2"
    )

    assert sql == correct_sql


def test_sql_fire_type():
    kwargs = {"polyname": "admin", "iso_code": "IDN", "fire_type": "modis"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') and fire_type = 'MODIS'"
    )

    assert sql == correct_sql


def test_sql_global():
    kwargs = {"polyname": "admin", "iso_code": "global", "aggregate_by": "global"}

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND "
        f"(alert_date >= '2001-01-01' AND alert_date <= '{today}') GROUP BY alert_date"
    )

    assert sql == correct_sql


def test_sql_agg_by_day_adm1():
    kwargs = {
        "polyname": "admin",
        "iso_code": "IDN",
        "aggregate_time": "day",
        "aggregate_admin": "adm1",
    }

    params = build_params(**kwargs)
    sql = QueryConstructorService.format_dataset_query(dataset_name, params)

    correct_sql = (
        "SELECT SUM(alerts) as alerts, adm1, alert_date "
        "FROM data "
        "WHERE polyname = 'admin' AND iso = 'IDN' "
        f"AND (alert_date >= '2001-01-01' AND alert_date <= '{today}') "
        "GROUP BY adm1, alert_date"
    )

    assert sql == correct_sql
