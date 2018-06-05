from flask import jsonify, request
import os
import datetime


class QueryConstructorService(object):
    """Class for formatting query and donwload sql"""

    @staticmethod
    def format_dataset_query(request, polyname, iso_code, adm1_code=None, adm2_code=None):

        # get parameters from query string
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        period = request.args.get('period', '2015-01-01,{}'.format(today))
        agg_values = request.args.get('aggregate_values', False)
        agg_by = request.args.get('aggregate_by', None)
        fire_type = request.args.get('fire_type', None)

        dates = period.split(',')
        start_date = dates[0].replace('-', '/')
        end_date = dates[1].replace('-', '/')

        groupby_sql = None

        # AGGREGATE VALUES
        if agg_values:
            select_statement = "SELECT fire_date, sum(fire_count)"

            # by admin level
            if 'adm' in agg_by:

                select_groupby_dict = {'adm1': 'adm1', 'adm2': 'adm1, adm2'}

                # add adm1 or adm1, adm2 to select statement
                select_statement += select_groupby_dict[agg_by]
                groupby_sql = select_groupby_dict[agg_by]

                sql = "{0} FROM data " \
                      "WHERE polyname = '{1}' AND " \
                      "iso = '{2}' AND " \
                      "(fire_date >= '{3}' AND fire_date <= '{4}')".format(select_statement,
                                                                           polyname,
                                                                           iso_code,
                                                                           start_date, end_date)

            # by time interval
            else:
                sql = "{0} FROM data " \
                      "WHERE polyname = '{1}' AND " \
                      "iso = '{2}' AND " \
                      "(fire_date >= '{3}' AND fire_date <= '{4}')".format(select_statement,
                                                                           polyname,
                                                                           iso_code,
                                                                           start_date, end_date)

        # DON'T AGGREGATE VALUES
        else:
            sql = "SELECT SUM(fire_count) FROM data " \
                  "WHERE polyname = '{0}' AND " \
                  "iso = '{1}' AND " \
                  "(fire_date >= '{2}' AND fire_date <= '{3}')".format(polyname,
                                                                       iso_code,
                                                                       start_date, end_date)

        # add the select query for admin levels
        if adm1_code:
            sql += " and adm1 = {}".format(adm1_code)
        if adm2_code:
            sql += " and adm2 = {}".format(adm2_code)
        if fire_type:
            sql += " and fire_type = '{}'".format(fire_type.upper())

        # at the very end, add the GROUP BY statement
        if agg_values:
            if 'adm' in agg_by:
                sql += "  GROUP BY {}, fire_date".format(groupby_sql)
            else:
                sql += " GROUP BY fire_date"

        return sql
