import unittest
import json
from ps import app
import requests
from httmock import all_requests, response, HTTMock
import datetime


@all_requests
def response_content(url, request):
    headers = {'content-type': 'application/json'}
    content = {'data': 'any value'}
    return response(200, content, headers, None, 5, request)

class BasicTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def deserialize_data(self, response):
        return json.loads(response.data).get('data', None)

    def deserialize_error(self, response):
        return json.loads(response.data)['errors'][0]['detail']


    # def test_v1_hello(self):
    #     with HTTMock(response_content):
    #         response = self.app.get('/api/v1/psone/hello', follow_redirects=True)
    #     status_code = response.status_code
    #     data = self.deserialize(response)
    #     self.assertEqual(status_code, 200)
    #     self.assertEqual(data[0].get('attributes').get('word'), 'hello')
    #     self.assertEqual(data[0].get('attributes').get('propertyThree'), 'any value')
    #
    # def test_v2_hello(self):
    #     response = self.app.get('/api/v1/pstwo/hello', follow_redirects=True)
    #     status_code = response.status_code
    #     data = self.deserialize(response)
    #     self.assertEqual(status_code, 200)
    #     self.assertEqual(data[0].get('attributes').get('word'), 'hello2')

# class TestBogusInputs(unittest.TestCase):
#
#     def setUp(self):
#         app.testing = True
#         app.config['TESTING'] = True
#         app.config['DEBUG'] = False
#         self.app = app.test_client()
#
#     def tearDown(self):
#         pass
#
#     def deserialize(self, response):
#         return json.loads(response.data).get('data', None)

    def test_quotes_in_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period="2013-01-01,2014-01-01"',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

    def test_bogus_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01,2013-01-01',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(error_text, 'Start date must be less than end date')

    def test_one_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-01-01',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(error_text, 'Period needs 2 arguments')

    def test_wrong_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2016-30-01,2016-01-01',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

    def test_early_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2011-01-01,2016-01-01',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(error_text, "Start date can't be earlier than 2012-01-01")

    def test_late_period(self):
        response = self.app.get('/api/v1/fire-alerts/summary-stats/admin/IDN?period=2013-01-01,2019-01-01',
                                follow_redirects=True)
        status_code = response.status_code
        error_text = self.deserialize_error(response)

        self.assertEqual(status_code, 400)
        today = datetime.datetime.now()
        self.assertEqual(error_text, "End year can't be later than {}".format(today.year))
