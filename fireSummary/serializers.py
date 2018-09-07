import datetime
"""Serializers"""


def serialize_greeting(greeting):
    """."""
    return {
        'id': None,
        'type': 'greeting',
        'attributes': {
            'word': greeting.get('word', None),
            'propertyTwo': greeting.get('propertyTwo', None),
            'propertyThree': greeting.get('propertyThree', None),
            'something': greeting.get('something', None),
        }
    }


def serialize_response(dataset_name, request, fire_count_response, polyname):
    """ return the fires stats in consistent format"""
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2001-01-01,{}'.format(today))

    filter_dict = {'fires': {'field_name': 'fire_type', 'default_val': 'ALL'}, 'glad': {'field_name': 'gladConfirmOnly',
                                                                                        'default_val': False}}
    field_name = filter_dict[dataset_name]['field_name']

    default_val = filter_dict[dataset_name]['default_val']

    if dataset_name == 'glad':
        if request.args.get(field_name) == 'True':
            field_val = True
        else:
            field_val = False

    else:
        field_val = request.args.get(field_name, default_val)

    agg_values = request.args.get('aggregate_values', None)
    if agg_values == 'True':
        agg_values = True

    return {
        'data': {
            'polyname' : polyname,
            'aggregate_admin': request.args.get('aggregate_admin', None),
            'aggregate_time': request.args.get('aggregate_time', None),
            'aggregate_values': agg_values,
            'period': period,
            field_name: field_val,
            'attributes': {
                'value':
                    fire_count_response

            }
        }
    }
