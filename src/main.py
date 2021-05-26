from countries import countries
from requests import get
from json import loads, dumps


url = 'https://stat.ripe.net/data/country-resource-stats/data.json'

for country in countries:
    country_code = country["code"]
    params = {"resource": country_code}
    params['starttime'] = '2020-12-15'
    params['endtime'] = '2020-12-30'
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
