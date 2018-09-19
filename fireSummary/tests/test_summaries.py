import unittest
import json
import logging
import datetime

from httmock import urlmatch, response, HTTMock
import pandas as pd

from fireSummary import app


mock_headers = {'content-type': 'application/json'}


@urlmatch(query=r'.*GROUP%20BY*%20.*alert_date$')
def year_mock(url, request):
    logging.debug('[TEST]: Found URL that matched adm1_alert_date_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # SELECT alert_date, sum(alerts) FROM data WHERE polyname = 'gadm28' AND
    # iso = 'IDN' AND (alert_date >= '2012-01-01' AND alert_date <= '2018-06-12') GROUP BY alert_date
    # run on 2018-06-12
    with open('fireSummary/tests/fixtures/fires_group_by_date_adm2.json') as src:
        content = json.load(src)

    return response(200, content, mock_headers, None, 5, request)


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

    return response(200, content, mock_headers, None, 5, request)


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

    return response(200, content, mock_headers, None, 5, request)


# regex here to match GROUP BY iso and global query
@urlmatch(query=r'.*GROUP%20BY%20iso$')
def iso_mock(url, request):
    logging.debug('[TEST]: Found URL that matched iso_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # "SELECT iso, SUM(alerts) FROM data WHERE polyname = 'wdpa' GROUP BY iso"
    with open('fireSummary/tests/fixtures/global_response.json') as src:
        content = json.load(src)

    return response(200, content, mock_headers, None, 5, request)


# regex here to match GROUP BY adm1 and global query
@urlmatch(query=r'.*GROUP%20BY%20iso.*adm1')
def iso_adm1_mock(url, request):
    logging.debug('[TEST]: Found URL that matched global_adm1_mock - mocking!')

    # this loads a cached response from this query to the production API:
    # "SELECT iso, SUM(alerts) FROM data WHERE polyname = 'wdpa' GROUP BY iso"
    with open('fireSummary/tests/fixtures/adm1_response.json') as src:
        content = json.load(src)

    return response(200, content, mock_headers, None, 5, request)


class SummaryTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

        # we're now filling in empty values
        # so the max date keeps changing
        self.min_date = datetime.date(2001, 1, 1)
        self.max_date = datetime.datetime.today()

        self.default_date_range = pd.date_range(self.min_date, self.max_date)


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

    def find_alert_date(self, alert_response, alert_date_aoi, alert_date_type=None, alert_year=None, adm1_val=None):
        # now that we're filling in missing dates, can't rely on indexes to
        # pull specific dates from the alert response (like data[-1])

        if alert_year:
            filtered_resp = [x for x in alert_response if x['year'] == alert_year and x[alert_date_type] == alert_date_aoi]
                             
        elif adm1_val:
            filtered_resp =  [x for x in alert_response if x['day'] == alert_date_aoi and x['adm1'] == adm1_val]

        else:
            filtered_resp =  [x for x in alert_response if x['day'] == alert_date_aoi]
  
        if len(filtered_resp) > 1:
            raise ValueError('Filtered response has more than one value for particular time period')

        return filtered_resp[0]

    def count_time_intervals(self, time_interval):

        # unclear why pd.date_range(start, end, freq='w') doesn't produce the 
        # same results as the code below (currently off by 4 weeks)
        date_df = pd.DataFrame(self.default_date_range, columns=['alert_date'])
        date_df['year'] = date_df.alert_date.dt.year
        
        # I'd like to use the more flexible date_df.alert_date.dt.to_period(<period_str>) here
        # but it gives different results than the code below, which is more standard
        if time_interval == 'week':
            date_df['time_interval'] = date_df.alert_date.dt.week
        elif time_interval == 'month':
            date_df['time_interval'] = date_df.alert_date.dt.month
        elif time_interval == 'quarter':
            date_df['time_interval'] = date_df.alert_date.dt.quarter
        else:
            date_df['time_interval'] = 1

        grouped = date_df.groupby(['year', 'time_interval']).size().reset_index()

        return len(grouped)

    def test_zero_fires_groupby(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/mining/USA?aggregate_values=True&aggregate_by=day')

        # check that we return Null instead of 0 - this poly/iso combo doesn't exist
        self.assertEqual(data, None)

    def test_group_by_day(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=day')

        # should have one result for each day between 2001-01-01 and today
        self.assertEqual(len(data), len(self.default_date_range))

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 5)
        self.assertEqual(data[0]['day'], '2001-01-01')

        # and the last
        data_aoi = self.find_alert_date(data, '2018-09-06')
        self.assertEqual(data_aoi['alerts'], 906)

    def test_group_by_week(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=week')

        # check that we have the correct # of weeks
        self.assertEqual(len(data), self.count_time_intervals('week'))

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 21)
        self.assertEqual(data[0]['week'], 1)

        # and the last
        data_aoi = self.find_alert_date(data, 36, 'week', 2018)
        self.assertEqual(data_aoi['alerts'], 4561)

    def test_group_by_quarter(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=quarter')

        # check that we have the proper # of quarters
        self.assertEqual(len(data), self.count_time_intervals('quarter'))

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 1184)
        self.assertEqual(data[0]['quarter'], 1)

        # and the last
        data_aoi = self.find_alert_date(data, 3, 'quarter', 2018)
        self.assertEqual(data_aoi['alerts'], 83976)

    def test_group_by_month(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=month')

        # check that we have the proper # of months
        self.assertEqual(len(data), self.count_time_intervals('month'))

        # and that the first row is correct
        self.assertEqual(data[0]['alerts'], 99)
        self.assertEqual(data[0]['month'], 1)

        # and the last
        data_aoi = self.find_alert_date(data, 9, 'month', 2018)
        self.assertEqual(data[-1]['alerts'], 6226)

    def test_group_by_year(self):
        data = self.make_request('/api/v1/fire-alerts/summary-stats/admin/IDN?aggregate_values=True&aggregate_by=year')

        # check that we have the proper # of years
        self.assertEqual(len(data), self.count_time_intervals('year'))

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

        # check that we have 257 rows - one for each ISO
        # NB - this includes ISOs that we don't have any fire data for
        self.assertEqual(len(data), 257)

        # and that the first row is correct
        self.assertEqual(data[1]['alerts'], 386)
        self.assertEqual(data[1]['iso'], 'AFG')

        # and the last
        self.assertEqual(data[-2]['alerts'], 158608)
        self.assertEqual(data[-2]['iso'], 'ZWE')

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

        # calculate # of days 2001-01-01 to present
        # multiplied by 34 adm1 areas
        total_days = self.default_date_range.shape[0] * 34
        self.assertEqual(len(data), total_days)

        # check that an early row (the first with data) is correct
        data_aoi = self.find_alert_date(data, '2001-01-09', adm1_val=1)
        self.assertEqual(data_aoi['alerts'], 2)

        # and the last with data
        data_aoi = self.find_alert_date(data, '2018-09-05', adm1_val=34)
        self.assertEqual(data_aoi['alerts'], 1)

