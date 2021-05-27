import calendar
from countries import countries
from requests import get, adapters
from json import loads, dumps
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from classes import Country
import os


def get_country_info():
    adapters.DEFAULT_RETRIES = 3
    # текущая дата
    today = datetime.today().date()
    # начало месяца
    yesterday = datetime.today().date().replace(day=1)
    get_country_stats_url = 'https://stat.ripe.net/data/country-resource-stats/data.json'
    get_country_resource_list_url = 'https://stat.ripe.net/data/country-resource-list/data.json'
    get_country_asns_url = 'https://stat.ripe.net/data/country-asns/data.json'

    for country_data_from_file in countries:
        country = Country(country_code=country_data_from_file["code"],
                          country_name=country_data_from_file["name"],
                          ipv4_prefix_stats=[],
                          ipv4_prefix_ris=[],
                          ipv6_prefix_stats=[],
                          ipv6_prefix_ris=[],
                          asns=[],
                          asns_stats=[],
                          asns_ris=[],
                          asns_registered=[],
                          asns_routed="",
                          asns_non_routed="",
                          days=[],
                          months=[],
                          months_human_read=[],
                          years=[]
                          )

        country_code = country_data_from_file["code"]
        params = {"resource": country_code, 'starttime': yesterday, 'endtime': today, 'resolution': '5m'}
        try:
            country_stats_from_ripe = get(get_country_stats_url, params, timeout=10)
        except Exception as err:
            country_stats_from_ripe = None
            print(f"Ашипка апи, блэт: {err}")

        if country_stats_from_ripe is not None:
            country_stats_from_ripe = loads(country_stats_from_ripe.text)['data']['stats']
            print(dumps(country_stats_from_ripe, indent=4))
            for data_from_ripe in country_stats_from_ripe:
                country.years.append(data_from_ripe['stats_date'].split('T')[0].split('-')[0])
                country.months.append(data_from_ripe['stats_date'].split('T')[0].split('-')[1])
                country.months_human_read.append(
                    calendar.month_name[int(data_from_ripe['stats_date'].split('T')[0].split('-')[1])]
                )
                country.days.append(data_from_ripe['stats_date'].split('T')[0].split('-')[2])
                country.ipv4_prefix_ris.append(data_from_ripe['v4_prefixes_ris'])
                country.ipv6_prefix_ris.append(data_from_ripe['v6_prefixes_ris'])
                country.ipv4_prefix_stats.append(data_from_ripe['v4_prefixes_stats'])
                country.ipv6_prefix_stats.append(data_from_ripe['v6_prefixes_stats'])
                country.asns_ris.append(data_from_ripe['asns_ris'])
                country.asns_stats.append(data_from_ripe['asns_stats'])

        params = {"resource": country_code}
        try:
            country_resource_list_from_ripe = get(get_country_resource_list_url, params)
        except Exception as err:
            country_resource_list_from_ripe = None
            print(f"Ашипка апи, блэт: {err}")

        if country_resource_list_from_ripe is not None:
            country_resource_list_from_ripe = loads(country_resource_list_from_ripe.text)["data"]
            print(dumps(country_resource_list_from_ripe, indent=4))
            country.asns_routed = country_resource_list_from_ripe['resources']['asn']
            country.ipv6 = country_resource_list_from_ripe['resources']['ipv4']
            country.ipv4 = country_resource_list_from_ripe['resources']['ipv6']

        params = {"resource": country_code, "lod": 1}
        try:
            country_asns_data_from_ripe = get(get_country_asns_url, params)
        except Exception as err:
            country_asns_data_from_ripe = None
            print(f"Ашипка апи, блэт: {err}")
        if country_asns_data_from_ripe is not None:
            country_asns_data_from_ripe = loads(country_asns_data_from_ripe.text)
            country.asns_registered_count = country_asns_data_from_ripe["data"]["countries"][0]["stats"]["registered"]
            country.asns_routed_count = country_asns_data_from_ripe["data"]["countries"][0]["stats"]["routed"]
            if 'set()' not in country_asns_data_from_ripe["data"]["countries"][0]["routed"]:
                country.asns_routed = country_asns_data_from_ripe["data"]["countries"][0]["routed"]
            if 'set()' not in country_asns_data_from_ripe["data"]["countries"][0]["non_routed"]:
                country.asns_routed = country_asns_data_from_ripe["data"]["countries"][0]["non_routed"]

        print(country.__dict__)
        exit()


get_country_info()