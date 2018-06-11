import pandas as pd
import logging


class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals
    (day, week, month, year)"""

    @staticmethod
    def create_time_table(data, polyname, request, iso_code):

        fire_type = request.args.get('fire_type', 'all')
        agg_values = request.args.get('aggregate_values', False)
        agg_by = request.args.get('aggregate_by', None)

        if not data['data']:
            return []

        else:
            df = pd.DataFrame(data['data'])
            logging.info(df.head())
            df = df.rename(columns={'SUM(alerts)': 'alerts'})

            if agg_values:
                # convert from unix to datetime
                df['fire_date_format'] = pd.to_datetime(df.alert_date, unit='ms')

                if 'adm' in agg_by:
                    groupby_dict = {'adm1': ['adm1'], 'adm2': ['adm1', 'adm2']}
                    grouped = df.groupby(groupby_dict[agg_by]).sum()['alerts'].reset_index()

                else:
                    # extract month and quarter values from datetime object
                    df['year'] = df.fire_date_format.dt.year
                    df['month'] = df.fire_date_format.dt.month
                    df['quarter'] = df.fire_date_format.dt.quarter
                    df['week'] = df.fire_date_format.dt.week

                    # start the list of columns to groupby
                    groupby_list = ['year']

                    # return string formatted day value if day summary requested
                    if agg_by != 'year':
                        groupby_list.append(agg_by)

                    grouped = df.groupby(groupby_list).sum()['alerts'].reset_index()

            else:
                grouped = df

            grouped['iso'] = iso_code
            grouped['polyname'] = polyname
            grouped['fire_type'] = fire_type.upper()

            return grouped.to_dict(orient='records')
