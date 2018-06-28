import datetime


class QueryConstructorService(object):
    """Class for formatting query and donwload sql"""

    @staticmethod
    def format_dataset_query(request, polyname, iso_code, adm1_code=None, adm2_code=None):

        # get parameters from query string. If none specific, default is set
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        period = request.args.get('period', '2001-01-01,{}'.format(today))

        agg_values = request.args.get('aggregate_values', False)
        agg_by = request.args.get('aggregate_by', None)
        fire_type = request.args.get('fire_type', None)

        start_date, end_date = period.split(',')

        groupby_sql = None
        if agg_by == 'day':
            agg_by = 'alert_date'

        select_statement = "SELECT SUM(alerts)"

        # AGGREGATE VALUES
        if agg_values:
            # by admin level
            if 'adm' in agg_by:

                # add adm1 or adm1, adm2 to select statement
                select_groupby_dict = {'adm1': ', adm1', 'adm2': ', adm1, adm2'}

                select_statement += select_groupby_dict[agg_by]

                groupby_sql = select_groupby_dict[agg_by].strip(', ')

                sql = "{0} FROM data " \
                      "WHERE polyname = '{1}' AND " \
                      "iso = '{2}' AND " \
                      "(alert_date >= '{3}' AND alert_date <= '{4}')".format(select_statement,
                                                                             polyname,
                                                                             iso_code,
                                                                             start_date, end_date)

            # by time interval
            else:

                select_statement += ", alert_date"

                # if summing globally, not by admin:
                where_statement = "WHERE polyname = '{}' AND ".format(polyname)

                # if summing by admin, add this to where statement
                if not iso_code == 'global':
                    where_statement += "iso = '{}' AND ".format(iso_code)

                sql = "{0} FROM data " \
                      "{1}" \
                      "(alert_date >= '{2}' AND alert_date <= '{3}')".format(select_statement,
                                                                             where_statement,
                                                                             start_date, end_date)

        # DON'T AGGREGATE VALUES
        else:
            print "DONT AGG VALUES"

            # if summing globally, not by admin:
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
        if fire_type:
            sql += " and fire_type = '{}'".format(fire_type.upper())

        # at the very end, add the GROUP BY statement
        if agg_values:
            if 'adm' in agg_by:
                sql += " GROUP BY " + groupby_sql
            else:
                sql += " GROUP BY alert_date"

        print "FINAL SQL: {}".format(sql)
        return sql
