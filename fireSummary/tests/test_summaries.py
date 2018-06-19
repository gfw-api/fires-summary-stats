import unittest
import json
import logging

from httmock import urlmatch, response, HTTMock

from fireSummary import app


# regex says match any request that ends with
# GROUP BY alert_date
# thinking here is that only aggregate_by={date part}
# queries will end like this
@urlmatch(query=r'.*GROUP%20BY%20alert_date')
def year_mock(url, request):
    logging.debug('[TEST]: Found URL that matched year_mock - mocking!')
    headers = {'content-type': 'application/json'}

    # this loads a cached response from this query to the production API:
    # SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'gadm28' AND 
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY alert_date
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/fires_group_by_date_idn.json') as src:
        content = json.load(src)

    return response(200, content, headers, None, 5, request)

# regex here to match GROUP BY adm1 or adm2
@urlmatch(query=r'.*GROUP%20BY%20adm.*')
def adm_mock(url, request):
    logging.debug('[TEST]: Found URL that matched adm_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # SELECT adm1, adm2, sum(alerts) FROM data WHERE polyname = 'gadm28' AND 
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY adm1, adm2
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/adm2_response.json') as src:
        content = json.load(src)

    headers = {'content-type': 'application/json'}
    return response(200, content, headers, None, 5, request)


class SummaryTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def deserialize_data(self, response):
        return json.loads(response.data)['data']['attributes']['value']

    def make_request(self, request):

        with HTTMock(year_mock):
            with HTTMock(adm_mock):
                response = self.app.get(request, follow_redirects=True)
                data = self.deserialize_data(response)

                return data

    def test_zero_fires_groupby(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/oil_palm/UZB?aggregate_values=True&aggregate_by=day')

        # check that we have 2344 days of data
        self.assertEqual(data, None)

    def test_group_by_day(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=day')

        # check that we have 2344 days of data
        self.assertEqual(len(data), 2344)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 129)
        self.assertEqual(data[0]['day'], '2012-01-01')

        # and the last
        self.assertEqual(data[-1]['alerts'], 243)
        self.assertEqual(data[-1]['day'], '2018-06-05')

    def test_group_by_week(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=week')

        # check that we have 337 weeks of data (grouped by year and week)
        self.assertEqual(len(data), 337)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 413)
        self.assertEqual(data[0]['week'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 485)
        self.assertEqual(data[-1]['week'], 23)

    def test_group_by_quarter(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=quarter')

        # check that we have 26 quarters of data (grouped by yer and quarter)
        self.assertEqual(len(data), 26)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 3683)
        self.assertEqual(data[0]['quarter'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 8826)
        self.assertEqual(data[-1]['quarter'], 2)

    def test_group_by_month(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=month')

        # check that we have 78 months of data (grouped by year and month)
        self.assertEqual(len(data), 78)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 1474)
        self.assertEqual(data[0]['month'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 1007)
        self.assertEqual(data[-1]['month'], 6)

    def test_group_by_year(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=year')

        # check that we have 7 years of data
        self.assertEqual(len(data), 7)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 71932)
        self.assertEqual(data[0]['year'], 2012)

        # and the last
        self.assertEqual(data[-1]['alerts'], 22871)
        self.assertEqual(data[-1]['year'], 2018)

    def test_group_by_adm1(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=adm1')

        # check that we have 34 rows - one for each adm1 in IDN
        self.assertEqual(len(data), 34)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 17439)
        self.assertEqual(data[0]['adm1'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 87)
        self.assertEqual(data[-1]['adm1'], 34)

    def test_group_by_adm2(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=adm2')

        # check that we have 436 rows - one for each adm2 in IDN
        self.assertEqual(len(data), 436)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 431)
        self.assertEqual(data[0]['adm2'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 16)
        self.assertEqual(data[-1]['adm2'], 443)
