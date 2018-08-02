import pandas as pd
import logging


class SummaryService(object):
    """Class for creating summary stats on glad data
    Takes data from the router and aggregates alerts by user specified intervals
    (day, week, month, year)"""

    @staticmethod
    def create_time_table(dataset_name, data, polyname, request, iso_code):

        fire_type = request.args.get('fire_type', 'all')
        confidence = request.args.get('gladConfirmedOnly', False)

        if confidence == 'True':
            confidence = True
        if confidence == 'False':
            confidence = False

        agg_values = request.args.get('aggregate_values', False)
        agg_by = request.args.get('aggregate_by', None)

        if not data['data']:
            return []

        else:
            df = pd.DataFrame(data['data'])
            df = df.rename(columns={'SUM(alerts)': 'alerts'})

            if agg_values:
                if agg_by in ['adm1', 'adm2', 'iso']:
                    groupby_dict = {'iso': ['iso'], 'adm1': ['adm1'], 'adm2': ['adm1', 'adm2']}
                    if iso_code == 'global':
                        groupby_dict['adm1'] = ['iso', 'adm1']
                    logging.info("\n********DF: {} \n".format(df.head()))
                    grouped = df.groupby(groupby_dict[agg_by]).sum()['alerts'].reset_index()

                else:
                    # convert from unix to datetime
                    df['fire_date_format'] = pd.to_datetime(df.alert_date, unit='ms')

                    # extract month and quarter values from datetime object
                    df['year'] = df.fire_date_format.dt.year
                    df['month'] = df.fire_date_format.dt.month
                    df['quarter'] = df.fire_date_format.dt.quarter
                    df['week'] = df.fire_date_format.dt.week
                    df['day'] = df.fire_date_format.dt.strftime('%Y-%m-%d')

                    # start the list of columns to groupby
                    groupby_list = ['year']

                    # return string formatted day value if day summary requested
                    logging.info('AGGBY: {}'.format(agg_by))
                    if agg_by != 'year' and agg_by != "None":
                        groupby_list.append(agg_by)

                    logging.info("GROUPBY LIST: {}".format(groupby_list))
                    grouped = df.groupby(groupby_list).sum()['alerts'].reset_index()
                    grouped.sort_values(by=groupby_list)
                    grouped['iso'] = iso_code

            else:
                grouped = df

            if iso_code != 'global':
                grouped['iso'] = iso_code
            grouped['polyname'] = polyname

            if dataset_name == 'fires':
                grouped['fire_type'] = fire_type.upper()
            if dataset_name == 'glad':
                grouped['gladConfirmedOnly'] = confidence

            return grouped.to_dict(orient='records')
