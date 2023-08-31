import datetime


def test_quotes_in_period(client):
    response = client.get(
        '/api/v1/fire-alerts/summary-stats/admin/IDN?period="2013-01-01,2014-01-01"'
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)"
    )


def test_bogus_period(client):
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01,2013-01-01"
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"] == "Start date must be less than end date"
    )


def test_one_period(client):
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01"
    )

    assert response.status_code == 400
    assert response.json["errors"][0]["detail"] == "Period needs 2 arguments"


def test_wrong_period(client):
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-30-01,2016-01-01"
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD"
    )


def test_early_period(client):
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=1999-01-01,2016-01-01"
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Start date can't be earlier than 2001-01-01"
    )


def test_late_period(client, mocker):
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2013-01-01,2025-01-01"
    )

    assert response.status_code == 400
    today = datetime.datetime.now()
    assert response.json["errors"][0][
        "detail"
    ] == "End year can't be later than {}".format(today.year)


def test_bad_global(client):
    response = client.get("/api/v1/fire-alerts/summary-stats/wdpa/global/1")

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "if requesting globally summarized statistics, you cannot choose additional "
        "administrative units."
    )


def test_bad_global_agg(client, mocker):
    agg_list = ["day", "week", "quarter", "month", "year", "adm1", "iso"]

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/wdpa/global?aggregate_values=True&aggregate_by=adm2"
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == (
            "aggregate_by or aggregate_time or "
            f"aggregate_admin must be specified as one of: {', '.join(agg_list)}"
        ),
    )
