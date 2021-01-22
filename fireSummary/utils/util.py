import os
import json
import datetime

import pandas as pd
from RWAPIMicroservicePython import request_to_microservice

from fireSummary.errors import Error


def query_microservice(sql, analysis_type):

    if analysis_type == 'glad':
        dataset_id = os.getenv('GLAD_DATASET_ID')
    elif analysis_type == 'fires':
        dataset_id = os.getenv('FIRES_DATASET_ID')
    else:
        raise Error('unknown analyis type: {}'.format(analysis_type))

    config = {
        'uri': '/query/{}?sql={}'.format(dataset_id, sql),
        'method': 'GET',
    }

    response = request_to_microservice(config)

    if response.get('errors'):
        raise Error(**response['errors'][0])

    else:
        return response


def load_valid_poly_iso(dataset_name):

    if dataset_name == 'fires':
        gadm_version = 28
    else:
        gadm_version = 36

    gadm_src = 'fireSummary/data/gadm{}.json'.format(gadm_version)
    with open(gadm_src) as thedata:
        return json.load(thedata)


def load_adm_rows(dataset_name, params):

    valid_rows = load_valid_poly_iso(dataset_name)

    # looks like [<iso>] or [iso, adm1] or [iso, adm1, adm2]
    # None values are not present
    input_combo = filter_input_combo(params)
    input_combo_offset = len(input_combo) + 2

    # filter first for the polyname we want
    valid_rows = [x[1:input_combo_offset] for x in valid_rows if x[0] == params['polyname']]

    # if we aren't dealing with a global dataset, need to filter at least to iso level
    if params['iso_code'] == 'global':
        valid_rows = [x[0] for x in valid_rows]
        col_names = ['iso']

    else:
        valid_rows = [x for x in valid_rows if x[0] == params['iso_code']]
        col_names = ['adm1']

        if params['adm1_code']:
            col_names.append('adm2')
            valid_rows = [x for x in valid_rows if x[1] == params['adm1_code']]

        if params['adm2_code']:
            valid_rows = [x for x in valid_rows if x[2] == params['adm2_code']]

        # drop iso from our table - this isn't included in the table that comes back from elastic
        valid_rows = [x[1:] for x in valid_rows] 

    # convert to df, group to remove duplicate iso/adm1/adm2 combinations
    df = pd.DataFrame(valid_rows, columns=col_names)
    grouped = df.groupby(df.columns.tolist()).size().reset_index()
    del grouped[0]

    return grouped


def filter_input_combo(params):

    input_combo = [params['iso_code'], params['adm1_code'], params['adm2_code']]

    # get rid of None values
    return [x for x in input_combo if x is not None]


def build_dummy_date_df(params):

    start_date, end_date = params['period'].split(',') 

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    df = pd.DataFrame(pd.date_range(start_date, end_date), columns=['alert_date_format'])
 
    # also add time summaries
    df = add_time_summaries(df)

    return df


def add_time_summaries(df):

    # extract month and quarter values from datetime object
    df['year'] = df.alert_date_format.dt.year
    df['month'] = df.alert_date_format.dt.month
    df['quarter'] = df.alert_date_format.dt.quarter
    df['week'] = df.alert_date_format.dt.week
    df['day'] = df.alert_date_format.dt.strftime('%Y-%m-%d')

    return df

