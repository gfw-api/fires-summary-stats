import unittest
import json
import datetime

from fireSummary import app
from fireSummary.services import QueryConstructorService


class DummyRequest(object):

    def __init__(self,  period=None, aggregate_by=None, fire_type=None):
        self.args = {}
        self.args['period'] = period
        self.args['aggregate_by'] = aggregate_by
        self.args['fire_type'] = fire_type

        if self.args['aggregate_by']:
            self.args['aggregate_values'] = True

        # remove key from dict if period is none, to match request object
        # https://stackoverflow.com/a/12118700/4355916
        self.args = {k: v for k, v in self.args.items() if v is not None}


class SQLTest(unittest.TestCase):

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

    def test_sql_admin0(self):
        # give a valid period
        request = DummyRequest('2012-01-01,2015-01-01')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        correct_sql = "SELECT SUM(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '2015-01-01')"

        self.assertEqual(sql, correct_sql)

    def test_sql_no_period(self):
        # dont give any query parameters
        request = DummyRequest()

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT SUM(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}')".format(today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_day(self):
        request = DummyRequest(None, 'day')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_week(self):
        request = DummyRequest(None, 'week')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_month(self):
        request = DummyRequest(None, 'month')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(today)
        print correct_sql
        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_year(self):
        request = DummyRequest(None, 'year')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(today)
        print correct_sql
        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_adm1(self):
        request = DummyRequest(None, 'adm1')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT sum(alerts), adm1 FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') GROUP BY adm1".format(today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_adm2(self):
        request = DummyRequest(None, 'adm2')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT sum(alerts), adm1, adm2 FROM data WHERE polyname = 'admin' AND iso = 'IDN' " \
                      "AND (alert_date >= '2012-01-01' AND alert_date <= '{}') " \
                      "GROUP BY adm1, adm2".format(today)

        self.assertEqual(sql, correct_sql)

    def test_sql_fire_type(self):
        request = DummyRequest(None, None, 'modis')

        polyname = 'admin'
        iso_code = 'IDN'

        sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code)

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        correct_sql = "SELECT SUM(alerts) FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '{}') and fire_type = 'MODIS'".format(today)
        print correct_sql
        self.assertEqual(sql, correct_sql)
