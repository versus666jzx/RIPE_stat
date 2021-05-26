from countries import countries
from requests import get
from json import loads, dumps
from datetime import datetime, timedelta

yesterday = datetime.today().date() - timedelta(days=30)
today = datetime.today().date()

url = 'https://stat.ripe.net/data/country-resource-stats/data.json'

for country in countries:
    country_code = country["code"]
    params = {"resource": country_code}
    params['starttime'] = yesterday
    params['endtime'] = today
    params['resolution'] = '5m'
    try:
        res = get(url, params)
    except Exception as err:
        res = None
        print(f"Ашипка: {err}")

    if res is not None:
        res = loads(res.text)['data']['stats']
        print(dumps(res, indent=4))
    break
