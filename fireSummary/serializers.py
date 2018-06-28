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


def serialize_response(request, fire_count_response, polyname):
    """ return the fires stats in consistent format"""
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2001-01-01,{}'.format(today))
    return {
        'data': {
            'polyname' : polyname,
            'aggregate_by': request.args.get('aggregate_by', None),
            'aggregate_values': request.args.get('aggregate_values', None),
            'period': period,
            'fire_type': request.args.get('fire_type', 'ALL'),
            'attributes': {
                'value':
                    fire_count_response

            }
        }
    }
