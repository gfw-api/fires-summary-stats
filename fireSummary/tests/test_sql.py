import unittest
import json
import datetime

from fireSummary import app
from fireSummary.services import QueryConstructorService


class SQLTest(unittest.TestCase):

    # test dataset has COD, ABW and a lot of polynamnes (gadm, ifl_2013, wdpa, etc)
    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.dataset_name = 'fires'
        self.today = datetime.datetime.today().strftime('%Y-%m-%d')

    def tearDown(self):
        pass

    def deserialize_data(self, response):
        return json.loads(response.data).get('data', None)

    def deserialize_error(self, response):
        return json.loads(response.data)['errors'][0]['detail']

    def build_params(self, **kwargs):

        params = {}
        params['period'] = kwargs.get('period', '2001-01-01,{}'.format(self.today))
        params['aggregate_by'] = kwargs.get('aggregate_by')
        params['aggregate_time'] = kwargs.get('aggregate_time')
        params['aggregate_admin'] = kwargs.get('aggregate_admin')
        params['fire_type'] = kwargs.get('fire_type')
        params['polyname'] = kwargs.get('polyname')
        params['iso_code'] = kwargs.get('iso_code')
        params['adm1_code'] = kwargs.get('adm1_code')
        params['adm2_code'] = kwargs.get('adm2_code')

        if params['aggregate_by'] or params['aggregate_time'] or params['aggregate_admin']:
            params['aggregate_values'] = True
        else:
            params['aggregate_values'] = False
    
        return params

    def test_sql_admin0(self):

        # give a valid period
        kwargs = {'period': '2012-01-01,2015-01-01',
                  'polyname': 'admin',
                  'iso_code': 'IDN'}
        params = self.build_params(**kwargs)

        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2012-01-01' AND alert_date <= '2015-01-01')"

        self.assertEqual(sql, correct_sql)

    def test_sql_no_period(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN'
                 }
        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}')".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_day(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'day'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_week(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'week'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_month(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'month'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_year(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'year'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_adm1(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'adm1'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, adm1 FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY adm1".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_adm2(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_by': 'adm2'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, adm1, adm2 FROM data WHERE polyname = 'admin' AND iso = 'IDN' " \
                      "AND (alert_date >= '2001-01-01' AND alert_date <= '{}') " \
                      "GROUP BY adm1, adm2".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_fire_type(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'fire_type': 'modis'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts FROM data WHERE polyname = 'admin' AND iso = 'IDN' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') and fire_type = 'MODIS'".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_global(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'global',
          'aggregate_by': 'global'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = "SELECT SUM(alerts) as alerts, alert_date FROM data WHERE polyname = 'admin' AND " \
                      "(alert_date >= '2001-01-01' AND alert_date <= '{}') GROUP BY alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

    def test_sql_agg_by_day_adm1(self):

        kwargs = {
          'polyname': 'admin',
          'iso_code': 'IDN',
          'aggregate_time': 'day',
          'aggregate_admin': 'adm1'
                 }

        params = self.build_params(**kwargs)
        sql = QueryConstructorService.format_dataset_query(self.dataset_name, params)

        correct_sql = \
            "SELECT SUM(alerts) as alerts, adm1, alert_date " \
            "FROM data " \
            "WHERE polyname = 'admin' AND iso = 'IDN' " \
            "AND (alert_date >= '2001-01-01' AND alert_date <= '{}') " \
            "GROUP BY adm1, alert_date".format(self.today)

        self.assertEqual(sql, correct_sql)

