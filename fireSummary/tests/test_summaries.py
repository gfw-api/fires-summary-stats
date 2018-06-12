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

# regex below used to matched "anything, then GROUP, then BY, then polyname, then anything"
# important to note that this @urlmatch targets query parameters (query=) only
# this is necessary to handle the request to check all polynames available to group by
# currently done in validators.py
@urlmatch(query=r'.*GROUP.*BY.*polyname.*')
def polyname_mock(url, request):
    logging.debug('[TEST]: Found URL that matched polyname_mock - mocking!')
    with open('fireSummary/tests/fixtures/polyname_response.json') as src:
        content = json.load(src)

    headers = {'content-type': 'application/json'}
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

        with HTTMock(polyname_mock):
            with HTTMock(year_mock):
                with HTTMock(adm_mock):
                    response = self.app.get(request, follow_redirects=True)
                    data = self.deserialize_data(response)

                    return data

    # TODO add other tests to check year, quarter, day
    def test_group_by_week(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=week')

        # check that we have 337 weeks of data
        self.assertEqual(len(data), 337)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 413)
        self.assertEqual(data[0]['week'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 485)
        self.assertEqual(data[-1]['week'], 23)

    # TODO add other tests to check adm2
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

