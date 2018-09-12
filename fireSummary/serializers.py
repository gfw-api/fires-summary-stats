import datetime
"""Serializers"""


def serialize_response(dataset_name, request, fire_count_response, polyname):
    """ return the fires stats in consistent format"""
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2001-01-01,{}'.format(today))

    filter_dict = {'fires': {'field_name': 'fire_type', 'default_val': 'ALL'}, 
                   'glad':  {'field_name': 'gladConfirmOnly', 'default_val': False}}
                                                                                       
    field_name = filter_dict[dataset_name]['field_name']

    default_val = filter_dict[dataset_name]['default_val']

    if dataset_name == 'glad':
        if request.args.get(field_name) == 'True':
            field_val = True
        else:
            field_val = False

    else:
        field_val = request.args.get(field_name, default_val)

    agg_values = request.args.get('aggregate_values')
    if agg_values and agg_values.lower() == 'true':
        agg_values = True

    agg_admin = request.args.get('aggregate_admin')
    agg_time = request.args.get('aggregate_time')
    agg_list = [x for x in [agg_admin, agg_time] if x is not None]

    if len(agg_list) == 2:
        aggregate_by = agg_list
    elif len(agg_list) == 1:
        aggregate_by = agg_list[0]
    else:
        aggregate_by = request.args.get('aggregate_by')

    return {
        'data': {
            'polyname' : polyname,
            'aggregate_admin': agg_admin,
            'aggregate_time': agg_time,
            'aggregate_by': aggregate_by,
            'aggregate_values': agg_values,
            'period': period,
            field_name: field_val,
            'attributes': {
                'value':
                    fire_count_response

            }
        }
    }

