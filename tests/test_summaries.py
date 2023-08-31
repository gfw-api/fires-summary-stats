import requests_mock
from moto import mock_logs
from RWAPIMicroservicePython.test_utils import mock_request_validation


from tests.fixtures.india_response import india_alerts
from tests.fixtures.fires_group_by_date_adm2 import fires_group_by_day_adm2
from tests.fixtures.adm1_response import adm1_alerts
from tests.fixtures.adm2_response import adm2_alerts
from tests.fixtures.global_response import global_alerts
from tests.utils import (
    mock_query,
    count_time_intervals,
    DEFAULT_DATE_RANGE,
    find_alert_date,
)

mock_headers = {"content-type": "application/json"}


def test_zero_fires_groupby(client):
    # nothing to mock here - first checks poly/iso combos and not finding DEU & mining, returns None
    # even before it gets to dataset query stuff
    # mock_query(mocker, india_alerts)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/mining/DEU?aggregate_values=True&aggregate_by=day",
        follow_redirects=True,
    )

    # check that we return Null instead of 0 - this poly/iso combo doesn't exist
    assert response.status_code == 200
    assert response.json["data"]["aggregate_admin"] is None


@requests_mock.Mocker(kw="mocker")
def test_adm1_stats(client, mocker):
    # simple test - mostly to make sure that simple SUM() queries working
    # and that IDN/1 is a valid endpoint

    mock_query(mocker, india_alerts)

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN/1",
    )

    assert response.json["data"]["attributes"]["value"][0]["alerts"] == 28514


@requests_mock.Mocker(kw="mocker")
def test_group_by_day(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=day"
    )
    data = response.json["data"]["attributes"]["value"]
    # should have one result for each day between 2001-01-01 and today
    assert len(data) == len(DEFAULT_DATE_RANGE)

    # and that the first row is correct
    assert data[0]["alerts"] == 5
    assert data[0]["day"] == "2001-01-01"

    # and the last
    data_aoi = find_alert_date(data, "2018-09-06")
    assert data_aoi["alerts"] == 906


@requests_mock.Mocker(kw="mocker")
def test_group_by_week(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=week"
    )
    data = response.json["data"]["attributes"]["value"]
    # check that we have the correct # of weeks
    assert len(data) == count_time_intervals("week")

    # and that the first row is correct
    assert data[0]["alerts"] == 21
    assert data[0]["week"] == 1

    # and the last
    data_aoi = find_alert_date(data, 36, "week", 2018)
    assert data_aoi["alerts"] == 4561


@requests_mock.Mocker(kw="mocker")
def test_group_by_quarter(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=quarter"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have the proper # of quarters
    assert len(data) == count_time_intervals("quarter")

    # and that the first row is correct
    assert data[0]["alerts"] == 1184
    assert data[0]["quarter"] == 1

    # and the last
    data_aoi = find_alert_date(data, 3, "quarter", 2018)
    assert data_aoi["alerts"] == 83976


@requests_mock.Mocker(kw="mocker")
def test_group_by_month(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=month"
    )
    data = response.json["data"]["attributes"]["value"]
    # check that we have the proper # of months
    assert len(data) == count_time_intervals("month")

    # and that the first row is correct
    assert data[0]["alerts"] == 99
    assert data[0]["month"] == 1

    # and the last
    data_aoi = find_alert_date(data, 9, "month", 2018)
    assert data_aoi["alerts"] == 6226


@requests_mock.Mocker(kw="mocker")
def test_group_by_year(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=year"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have the proper # of years
    assert len(data) == count_time_intervals("year")

    # and that the first row is correct
    assert data[0]["alerts"] == 15534
    assert data[0]["year"] == 2001

    # and the last
    data_aoi = find_alert_date(data, 2018, "year", 2018)
    assert data_aoi["alerts"] == 111936


@requests_mock.Mocker(kw="mocker")
def test_group_by_adm1(client, mocker):
    mock_query(mocker, adm2_alerts)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=adm1"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have 34 rows - one for each adm1 in IDN
    assert len(data) == 34

    # and that the first row is correct
    assert data[0]["alerts"] == 17439
    assert data[0]["adm1"] == 1

    # and the last
    assert data[-1]["alerts"] == 87
    assert data[-1]["adm1"] == 34


@requests_mock.Mocker(kw="mocker")
def test_group_by_adm2(client, mocker):
    mock_query(mocker, adm2_alerts)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=adm2"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have 436 rows - one for each adm2 in IDN
    assert len(data) == 436

    # and that the first row is correct
    assert data[0]["alerts"] == 431
    assert data[0]["adm2"] == 1

    # and the last
    assert data[-1]["alerts"] == 16
    assert data[-1]["adm2"] == 443


@requests_mock.Mocker(kw="mocker")
def test_global_group_by_iso(client, mocker):
    mock_query(mocker, global_alerts)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/global?aggregate_values=True&aggregate_by=iso"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have 257 rows - one for each ISO
    # NB - this includes ISOs that we don't have any fire data for
    assert len(data) == 257

    # and that the first row is correct
    assert data[1]["alerts"] == 386
    assert data[1]["iso"] == "AFG"

    # and the last
    assert data[-2]["alerts"] == 158608
    assert data[-2]["iso"] == "ZWE"


@requests_mock.Mocker(kw="mocker")
def test_global_group_by_adm1(client, mocker):
    mock_query(mocker, adm1_alerts)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/global?aggregate_values=True&aggregate_by=adm1"
    )
    data = response.json["data"]["attributes"]["value"]

    # check that we have 34 rows - one for each ISO/adm1 combo
    assert len(data) == 34

    # and that the first row is correct
    assert data[0]["alerts"] == 17439
    assert data[0]["iso"] == "IDN"

    # and the last
    assert data[-1]["alerts"] == 87
    assert data[-1]["iso"] == "IDN"


@requests_mock.Mocker(kw="mocker")
def test_group_by_day_adm1(client, mocker):
    mock_query(mocker, fires_group_by_day_adm2)
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_admin=adm1&aggregate_time=day"
    )
    data = response.json["data"]["attributes"]["value"]
    # calculate # of days 2001-01-01 to present
    # multiplied by 34 adm1 areas
    total_days = DEFAULT_DATE_RANGE.shape[0] * 34
    assert len(data) == total_days

    # check that an early row (the first with data) is correct
    data_aoi = find_alert_date(data, "2001-01-09", adm1_val=1)
    assert data_aoi["alerts"] == 2

    # and the last with data
    data_aoi = find_alert_date(data, "2018-09-05", adm1_val=34)
    assert data_aoi["alerts"] == 1
