import requests_mock
from moto import mock_logs

from tests.utils import mock_query
from tests.fixtures.brazil_response import brazil_alerts

mock_headers = {"content-type": "application/json"}


@requests_mock.Mocker(kw="mocker")
def test_glad_summary_stats_for_iso(client, mocker):
    mock_query(mocker, brazil_alerts)
    response = client.get("/api/v1/glad-alerts/summary-stats/admin/BRA")
    data = response.json["data"]["attributes"]["value"]
    assert data[0]["alerts"] == 173023338
