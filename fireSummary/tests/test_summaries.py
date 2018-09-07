import unittest
import json
import logging

from httmock import urlmatch, response, HTTMock

from fireSummary import app


@urlmatch(query=r'.*GROUP%20BY*%20.*alert_date$')
def year_mock(url, request):
    logging.debug('[TEST]: Found URL that matched adm1_alert_date_mock - mocking!')
    headers = {'content-type': 'application/json'}

    # this loads a cached response from this query to the production API:
    # SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'gadm28' AND
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY alert_date
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/fires_group_by_date_adm2.json') as src:
        content = json.load(src)

    return response(200, content, headers, None, 5, request)


# regex here to match GROUP BY adm1 or adm2
@urlmatch(query=r'.*GROUP%20BY%20adm1$')
def adm1_mock(url, request):
    logging.debug('[TEST]: Found URL that matched adm1_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # SELECT adm1, adm2, sum(alerts) FROM data WHERE polyname = 'gadm28' AND 
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY adm1, adm2
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/adm2_response.json') as src:
        content = json.load(src)

    headers = {'content-type': 'application/json'}
    return response(200, content, headers, None, 5, request)


# regex here to match GROUP BY adm1 or adm2
@urlmatch(query=r'.*GROUP%20BY%20adm1,%20adm2')
def adm2_mock(url, request):
    logging.debug('[TEST]: Found URL that matched adm2_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # SELECT adm1, adm2, sum(alerts) FROM data WHERE polyname = 'gadm28' AND
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY adm1, adm2
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/adm2_response.json') as src:
        content = json.load(src)

    headers = {'content-type': 'application/json'}
    return response(200, content, headers, None, 5, request)


# regex here to match GROUP BY iso and global query
@urlmatch(query=r'.*GROUP%20BY%20iso$')
def iso_mock(url, request):
    logging.debug('[TEST]: Found URL that matched iso_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # "SELECT iso, SUM(alerts) FROM data WHERE polyname = 'wdpa' GROUP BY iso"
    with open('fireSummary/tests/fixtures/global_response.json') as src:
        content = json.load(src)

    headers = {'content-type': 'application/json'}
    return response(200, content, headers, None, 5, request)


# regex here to match GROUP BY adm1 and global query
@urlmatch(query=r'.*GROUP%20BY%20iso.*adm1')
def iso_adm1_mock(url, request):
    logging.debug('[TEST]: Found URL that matched global_adm1_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # "SELECT iso, SUM(alerts) FROM data WHERE polyname = 'wdpa' GROUP BY iso"
    with open('fireSummary/tests/fixtures/adm1_response.json') as src:
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
            with HTTMock(adm1_mock):
                with HTTMock(adm2_mock):
                    with HTTMock(iso_mock):
                        with HTTMock(iso_adm1_mock):
                            response = self.app.get(request, follow_redirects=True)
                            data = self.deserialize_data(response)

                            return data

    def test_zero_fires_groupby(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/mining/USA?aggregate_values=True&aggregate_by=day')

        # check that we return Null instead of 0 - this poly/iso combo doesn't exist
        self.assertEqual(data, None)

    def test_group_by_day(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=day')

        # check that we have 19161 days of data
        self.assertEqual(len(data), 6387)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 5)
        self.assertEqual(data[0]['day'], '2001-01-01')

        # and the last
        self.assertEqual(data[-1]['alerts'], 906)
        self.assertEqual(data[-1]['day'], '2018-09-06')
    #

    def test_group_by_week(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=week')

        # check that we have 924 weeks of data (grouped by year and week)
        self.assertEqual(len(data), 924)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 21)
        self.assertEqual(data[0]['week'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 4561)
        self.assertEqual(data[-1]['week'], 36)

    def test_group_by_quarter(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=quarter')

        # check that we have 71 quarters of data (grouped by yer and quarter)
        self.assertEqual(len(data), 71)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 1184)
        self.assertEqual(data[0]['quarter'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 83976)
        self.assertEqual(data[-1]['quarter'], 3)

    def test_group_by_month(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=month')

        # check that we have 213 months of data (grouped by year and month)
        self.assertEqual(len(data), 213)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 99)
        self.assertEqual(data[0]['month'], 1)

        # and the last
        self.assertEqual(data[-1]['alerts'], 6226)
        self.assertEqual(data[-1]['month'], 9)

    def test_group_by_year(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=year')

        # check that we have 18 years of data
        self.assertEqual(len(data), 18)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 15534)
        self.assertEqual(data[0]['year'], 2001)

        # and the last
        self.assertEqual(data[-1]['alerts'], 111936)
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

    def test_global_group_by_iso(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/global?aggregate_values=True&aggregate_by=iso')

        # check that we have 205 rows - one for each ISO
        self.assertEqual(len(data), 205)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 386)
        self.assertEqual(data[0]['iso'], 'AFG')

        # and the last
        self.assertEqual(data[-1]['alerts'], 158608)
        self.assertEqual(data[-1]['iso'], 'ZWE')

    def test_global_group_by_adm1(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/global?aggregate_values=True&aggregate_by=adm1')

        # check that we have 34 rows - one for each ISO/adm1 combo
        self.assertEqual(len(data), 34)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 17439)
        self.assertEqual(data[0]['iso'], 'IDN')

        # and the last
        self.assertEqual(data[-1]['alerts'], 87)
        self.assertEqual(data[-1]['iso'], 'IDN')

    def test_group_by_day_adm1(self):

        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_admin=adm1&aggregate_time=day')

        self.assertEqual(len(data), 82486)

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 2)
        self.assertEqual(data[0]['adm1'], 1)
        self.assertEqual(data[0]['day'], '2001-01-09')

        # and the last
        self.assertEqual(data[-1]['alerts'], 1)
        self.assertEqual(data[-1]['adm1'], 34)
        self.assertEqual(data[-1]['day'], '2018-09-05')
