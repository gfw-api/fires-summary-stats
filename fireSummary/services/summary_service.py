import logging

import pandas as pd

from fireSummary.utils import util


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
                logging.info("\n********DF: {} \n".format(df.head()))

                if agg_admin in ['adm1', 'adm2', 'iso']:
                    groupby_dict = {'iso': ['iso'], 'adm1': ['adm1'], 'adm2': ['adm1', 'adm2']}

                    if iso_code == 'global':
                        groupby_dict['adm1'] = ['iso', 'adm1']

                    group_by_list = groupby_dict[agg_admin]

                    # load all possible iso/adm1/adm2 rows for this query
                    dummy_admin_df = util.load_adm_rows(dataset_name, params)

                if agg_time:

                    dummy_date_df = util.build_dummy_date_df(params)
 
                    # convert from unix to datetime, then convert to day/month/year
                    df['alert_date_format'] = pd.to_datetime(df.alert_date, unit='ms')
                    del df['alert_date']

                    df = util.add_time_summaries(df)

                    # start the list of columns to groupby
                    if not group_by_list:
                        group_by_list = ['year']
                    else:
                        group_by_list.append('year')

                    # return string formatted day value if day summary requested
                    if agg_time != 'year':
                        group_by_list.append(agg_time)

                # then build a dummy DF of all possible data
                if agg_admin and agg_time:
                    
                    # https://stackoverflow.com/questions/13269890/
                    dummy_date_df['key'] = 1
                    dummy_admin_df['key'] = 1
                    dummy_df = pd.merge(dummy_date_df, dummy_admin_df, on='key')
                    del dummy_df['key']

                elif agg_admin:
                    dummy_df = dummy_admin_df

                else:
                    dummy_df = dummy_date_df

                # join dummy dataframe to stats dataframe
                common_cols = [x for x in dummy_df.columns if x in df.columns]
                merged = pd.merge(dummy_df, df, on=common_cols, how='left')

                # set alerts to 0 where we should have a record (iso/adm1/adm2 exists)
                # but nothing in elastic
                merged.alerts = merged.alerts.fillna(0)
 
                # group and sum
                grouped = merged.groupby(group_by_list).sum()['alerts'].reset_index()
                grouped = grouped.sort_values(by=group_by_list)

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

