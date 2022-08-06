import requests

from django.conf import settings

from bot.helpers.log_catcher import log_catcher

@log_catcher
def make_request_get_clicks(from_date: str,
                            user: str,
                            to_date: str = '') -> int:
    headers = {'Api-Key': settings.KEITARO_TOKEN}
    data = {
        "range": {
            "from": from_date,
            "to": to_date
        },
        "filters": [{
            'name': 'sub_id_6',
            'operator': 'EQUALS',
            'expression': user
        }]
    }
    url = f'{settings.KEITARO_IP}/admin_api/v1/report/build'
    response = requests.post(url=url,
                             headers=headers,
                             json=data)
    response_json = response.json()
    return response_json.get('rows')[0].get('clicks')



