import pandas as pd
import logging


class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals
    (day, week, month, year)"""

    @staticmethod
    def create_time_table(dataset, data, agg_type):

        if not data['data']:
            return []

        else:
            df = pd.DataFrame(data['data'])
            # df = df.rename(columns={'COUNT(*)': 'count'})

            # standardize the output table to use julian_day
            if dataset == 'terrai':
                df = df.rename(columns={'day': 'julian_day'})

            if agg_type == 'day':
                agg_type = 'julian_day'

            # create datetime column in pandas so we can use its datetime
            # methods to easily summarize our results
            df['fire_date_format'] = pd.to_datetime(df.fire_date, format='%Y/%m/%d')

            # extract month and quarter values from datetime object
            df['year'] = df.fire_date_format.dt.year
            df['month'] = df.fire_date_format.dt.month
            df['quarter'] = df.fire_date_format.dt.quarter
            df['week'] = df.fire_date_format.dt.week

            # start the list of columns to groupby
            groupby_list = ['year']

            # return string formatted day value if day summary requested
            if agg_type != 'year':
                groupby_list.append(agg_type)

            grouped = df.groupby(groupby_list).sum()['fire_count'].reset_index()

            return grouped.to_dict(orient='records')
