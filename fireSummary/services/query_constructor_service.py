import datetime


class QueryConstructorService(object):
    """Class for formatting query and download sql"""

    @staticmethod
    def format_dataset_query(dataset_name, params):

        agg_by = params['aggregate_by']
        agg_values = params['aggregate_values']
        agg_admin = params['aggregate_admin']
        agg_time = params['aggregate_time']
        polyname = params['polyname']
        iso_code = params['iso_code']
        adm1_code = params['adm1_code']
        adm2_code = params['adm2_code']
        
        if agg_by in ['iso', 'adm1', 'adm2', 'global']:
            agg_admin = agg_by
        if agg_by in ['day', 'week', 'month', 'quarter', 'year']:
            agg_time = agg_by

        start_date, end_date = params['period'].split(',')

        groupby_sql = None
        if agg_time == 'day':
            agg_time = 'alert_date'

        select_statement = "SELECT SUM(alerts) as alerts"
        if dataset_name == 'fires':
            where_statement = "WHERE polyname = '{}' AND ".format(polyname)
        else:
            where_statement = 'WHERE '

        # AGGREGATE VALUES
        if agg_values:

            # by admin level
            if agg_admin in ['adm1', 'adm2', 'iso']:

                # add adm1 or adm1, adm2 to select statement
                select_groupby_dict = {'iso': ', iso', 'adm1': ', adm1', 'adm2': ', adm1, adm2'}
                if iso_code == 'global':

                    select_groupby_dict['adm1'] = ', iso, adm1'

                select_statement += select_groupby_dict[agg_admin]

                groupby_sql = select_groupby_dict[agg_admin].strip(', ')

                # if summing by admin, add this to where statement
                if not iso_code == 'global':
                    where_statement += "iso = '{}' AND ".format(iso_code)

                sql = "{0} FROM data " \
                      "{1}" \
                      "(alert_date >= '{2}' AND alert_date <= '{3}')".format(select_statement,
                                                                             where_statement,
                                                                             start_date, end_date)

            # by time interval
            if agg_time or agg_admin == 'global':

                select_statement += ", alert_date"

                # if summing by admin, add this to where statement
                if not iso_code == 'global':
                    if "iso = '{}' AND ".format(iso_code) not in where_statement:
                        where_statement += "iso = '{}' AND ".format(iso_code)

                sql = "{0} FROM data " \
                      "{1}" \
                      "(alert_date >= '{2}' AND alert_date <= '{3}')".format(select_statement,
                                                                             where_statement,
                                                                             start_date, end_date)

        # DON'T AGGREGATE VALUES
        else:

            # if summing globally, not by admin:
            if dataset_name == 'fires':
                where_statement = "WHERE polyname = '{}' AND ".format(polyname)

            # if summing by admin, add this to where statement
            if not iso_code == 'global':
                where_statement += "iso = '{}' AND ".format(iso_code)

            sql = "{0} FROM data " \
                  "{1}" \
                  "(alert_date >= '{3}' AND alert_date <= '{4}')".format(select_statement,
                                                                         where_statement,
                                                                         iso_code,
                                                                         start_date, end_date)

        # add the select query for admin levels
        if adm1_code:
            sql += " and adm1 = {}".format(adm1_code)
        if adm2_code:
            sql += " and adm2 = {}".format(adm2_code)

        if dataset_name == 'fires' and params['fire_type']:
            sql += " and fire_type = '{}'".format(params['fire_type'].upper())

        if dataset_name == 'glad' and params['gladConfirmOnly']:
            sql += " and confidence = '3'"

        # at the very end, add the GROUP BY statement
        if agg_values:
            if agg_time or agg_admin == 'global':
                if not groupby_sql:
                    groupby_sql = 'alert_date'
                else:
                    groupby_sql += ', alert_date'

            sql += " GROUP BY " + groupby_sql

        return sql
