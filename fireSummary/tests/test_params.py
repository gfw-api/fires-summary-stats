import unittest
import json
import datetime

from fireSummary import app


class ParamsTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def deserialize_error(self, response):
        return json.loads(response.data)['errors'][0]['detail']

    def make_request(self, request):

        response = self.app.get(request, follow_redirects=True)
        error = self.deserialize_error(response)
        status_code = response.status_code

        # and do our check to make sure the error code is correct here
        # that way we don't have to do it every time below
        self.assertEqual(status_code, 400)

        return error

    def test_quotes_in_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period="2013-01-01,2014-01-01"')

        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

    def test_bogus_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01,2013-01-01')

        self.assertEqual(error_text, 'Start date must be less than end date')

    def test_one_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01')

        self.assertEqual(error_text, 'Period needs 2 arguments')

    def test_wrong_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-30-01,2016-01-01')

        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

    def test_early_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period=1999-01-01,2016-01-01')

        self.assertEqual(error_text, "Start date can't be earlier than 2001-01-01")

    def test_late_period(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2013-01-01,2025-01-01')

        today = datetime.datetime.now()
        self.assertEqual(error_text, "End year can't be later than {}".format(today.year))

    def test_bad_global(self):
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/wdpa/global/1')
        self.assertEqual(error_text, "if requesting globally summarized statistics, you cannot choose additional "
                                     "administrative units.")

    def test_bad_global_agg(self):
        agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'iso']
        error_text = self.make_request('/api/v1/fire-alerts/summary-stats/wdpa/global?aggregate_values=True&aggregate_by=adm2')
        self.assertEqual(error_text, "aggregate_by or aggregate_time or "
                                     "aggregate_admin must be specified as one of: {} ".format(", ".join(agg_list)))
