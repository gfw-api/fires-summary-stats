import datetime
"""Serializers"""


def serialize_response(dataset_name, agg_data, params):
    """ return the fires stats in consistent format"""
    period = params['period']
    agg_values = params['aggregate_values']
    agg_admin = params['aggregate_admin']
    agg_time = params['aggregate_time']
    agg_list = [x for x in [agg_admin, agg_time] if x is not None]

    if dataset_name == 'glad':
        field_name = 'gladConfirmOnly'
    else:
        field_name = 'fire_type'

    if len(agg_list) == 2:
        aggregate_by = agg_list
    elif len(agg_list) == 1:
        aggregate_by = agg_list[0]
    else:
        aggregate_by = params['aggregate_by']

    return {
        'data': {
            'polyname' : params['polyname'],
            'aggregate_admin': agg_admin,
            'aggregate_time': agg_time,
            'aggregate_by': aggregate_by,
            'aggregate_values': agg_values,
            'period': period,
            field_name: params[field_name],
            'attributes': {
                'value':
                    agg_data
            }
        }
    }

