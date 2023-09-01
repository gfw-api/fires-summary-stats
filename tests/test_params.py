import datetime
import os

import requests_mock
from RWAPIMicroservicePython.test_utils import mock_request_validation


@requests_mock.Mocker(kw="mocker")
def test_quotes_in_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        '/api/v1/fire-alerts/summary-stats/admin/IDN?period="2013-01-01,2014-01-01"',
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)"
    )


@requests_mock.Mocker(kw="mocker")
def test_bogus_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01,2013-01-01",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"] == "Start date must be less than end date"
    )


@requests_mock.Mocker(kw="mocker")
def test_one_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert response.json["errors"][0]["detail"] == "Period needs 2 arguments"


@requests_mock.Mocker(kw="mocker")
def test_wrong_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-30-01,2016-01-01",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD"
    )


@requests_mock.Mocker(kw="mocker")
def test_early_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=1999-01-01,2016-01-01",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "Start date can't be earlier than 2001-01-01"
    )


@requests_mock.Mocker(kw="mocker")
def test_late_period(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/admin/IDN?period=2013-01-01,2025-01-01",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    today = datetime.datetime.now()
    assert response.json["errors"][0][
        "detail"
    ] == "End year can't be later than {}".format(today.year)


@requests_mock.Mocker(kw="mocker")
def test_bad_global(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    response = client.get(
        "/api/v1/fire-alerts/summary-stats/wdpa/global/1",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == "if requesting globally summarized statistics, you cannot choose additional "
        "administrative units."
    )


@requests_mock.Mocker(kw="mocker")
def test_bad_global_agg(client, mocker):
    mock_request_validation(
        mocker,
        microservice_token=os.getenv("MICROSERVICE_TOKEN"),
    )
    agg_list = ["day", "week", "quarter", "month", "year", "adm1", "iso"]

    response = client.get(
        "/api/v1/fire-alerts/summary-stats/wdpa/global?aggregate_values=True&aggregate_by=adm2",
        headers={"x-api-key": "api-key-test"},
    )

    assert response.status_code == 400
    assert (
        response.json["errors"][0]["detail"]
        == (
            "aggregate_by or aggregate_time or "
            f"aggregate_admin must be specified as one of: {', '.join(agg_list)}"
        ),
    )
