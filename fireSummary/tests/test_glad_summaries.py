import unittest
import json
import logging
from httmock import response, HTTMock, all_requests

from fireSummary import app

mock_headers = {'content-type': 'application/json'}


@all_requests
def iso_total_mock(url, request):
    return load_src_json('fireSummary/tests/fixtures/BRA_response.json')


def load_src_json(src_json):
    logging.debug('[TEST]: loading mock response from {}'.format(src_json))
    with open(src_json) as src:
        content = json.load(src)

    return response(200, content, mock_headers)
    

class SummaryTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def make_request(self, request):
        # rstrip is important - seems like httmock doesn't work if a trailing slash is added
        # which is awkward . . . this is a library designed to mock web requests after all
        response = self.app.get(request.rstrip('/'), follow_redirects=True)
        return json.loads(response.data)['data']['attributes']['value']

    def test_glad_summary_stats_for_iso(self):
        with HTTMock(iso_total_mock):
            data = self.make_request('/api/v1/glad-alerts/summary-stats/admin/BRA')

        self.assertEqual(data[0]['alerts'], 173023338)

