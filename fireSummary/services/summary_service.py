import pandas as pd
import logging


class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals
    (day, week, month, year)"""

    @staticmethod
    def create_time_table(dataset_name, data, params):


        agg_by = params['aggregate_by']
        agg_values = params['aggregate_values']
        agg_admin = params['aggregate_admin']
        agg_time = params['aggregate_time']
        iso_code = params['iso_code']
        polyname = params['polyname']

        if agg_by in ['iso', 'adm1', 'adm2', 'global']:
            agg_admin = agg_by
        if agg_by in ['day', 'week', 'month', 'quarter', 'year']:
            agg_time = agg_by

        if not data['data']:
            return []

        else:
            df = pd.DataFrame(data['data'])
            df = df.rename(columns={'SUM(alerts)': 'alerts'})
            group_by_list = None

            if agg_values:
                if agg_admin in ['adm1', 'adm2', 'iso']:
                    groupby_dict = {'iso': ['iso'], 'adm1': ['adm1'], 'adm2': ['adm1', 'adm2']}
                    if iso_code == 'global':
                        groupby_dict['adm1'] = ['iso', 'adm1']

                    group_by_list = groupby_dict[agg_admin]

                    logging.info("\n********DF: {} \n".format(df.head()))

                if agg_time:
                    # convert from unix to datetime
                    df['fire_date_format'] = pd.to_datetime(df.alert_date, unit='ms')

                    # extract month and quarter values from datetime object
                    df['year'] = df.fire_date_format.dt.year
                    df['month'] = df.fire_date_format.dt.month
                    df['quarter'] = df.fire_date_format.dt.quarter
                    df['week'] = df.fire_date_format.dt.week
                    df['day'] = df.fire_date_format.dt.strftime('%Y-%m-%d')

                    # start the list of columns to groupby
                    if not group_by_list:
                        group_by_list = ['year']
                    else:
                        group_by_list.append('year')

                    # return string formatted day value if day summary requested
                    if agg_time != 'year' and agg_time != "None":
                        group_by_list.append(agg_time)

                grouped = df.groupby(group_by_list).sum()['alerts'].reset_index()
                grouped = grouped.sort_values(by=group_by_list)
                # grouped['iso'] = iso_code

                # grouped = df.groupby(groupby_dict[agg_admin]).sum()['alerts'].reset_index()
            else:
                grouped = df

            if iso_code != 'global':
                grouped['iso'] = iso_code

            grouped['polyname'] = polyname

            if dataset_name == 'fires':
                grouped['fire_type'] = params['fire_type'].upper() if params['fire_type'] else 'all'
            if dataset_name == 'glad':
                grouped['gladConfirmOnly'] = params['gladConfirmOnly']

            return grouped.to_dict(orient='records')

