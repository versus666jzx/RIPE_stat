import calendar
import queue
import psycopg2
import classes
from countries import countries
from requests import get, adapters
from json import loads, dumps
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from classes import Country
import os


def get_country_info(
        queue: queue.Queue
) -> queue.Queue:

    adapters.DEFAULT_RETRIES = 5
    # дата начала сбора данных
    start_time = str(datetime.today().date().replace(day=1)) + "T00:00"
    # дата завершения сбора данных
    end_time = str(datetime.today().date()) + "T23:59"
    print(start_time, end_time)
    # источники данных
    get_country_stats_url = 'https://stat.ripe.net/data/country-resource-stats/data.json'
    get_country_resource_list_url = 'https://stat.ripe.net/data/country-resource-list/data.json'
    get_country_asns_url = 'https://stat.ripe.net/data/country-asns/data.json'

    country_count = len(countries)

    # для каждой страны из списка
    for country_data_from_file in countries:
        print(f"Получаем данные по {country_data_from_file['name']}")
        country_count -= 1
        print(f"Осталось стран {country_count} из 197")
        # создаем объект класса
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
                          years=[],
                          ipv4=[],
                          ipv6=[]
                          )

        # получаем код страны
        country_code = country_data_from_file["code"]

        # задаем параметры для api
        # Возможные значения для resolution:
        # "5m" - 5 minutes
        # "1h" - 1 hour
        # "1d" - 1 day
        # "1w" - 1 week
        params = {"resource": country_code, 'starttime': start_time, 'endtime': end_time, 'resolution': '1d'}

        # пытаемся получить данные по api
        try:
            country_stats_from_ripe = get(get_country_stats_url, params, timeout=30)
        except Exception as err:
            country_stats_from_ripe = None
            print(f"Ашипка апи, блэт: {err}")

        if country_stats_from_ripe is not None:
            country_stats_from_ripe = loads(country_stats_from_ripe.text)['data']['stats']
            # print(dumps(country_stats_from_ripe, indent=4))
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

        # задаем параметры для api
        params = {"resource": country_code}

        # пытаемся получить данные по api
        try:
            country_resource_list_from_ripe = get(get_country_resource_list_url, params, timeout=30)
        except Exception as err:
            country_resource_list_from_ripe = None
            print(f"Ашипка апи, блэт: {err}")

        if country_resource_list_from_ripe is not None:
            country_resource_list_from_ripe = loads(country_resource_list_from_ripe.text)["data"]
            # print(dumps(country_resource_list_from_ripe, indent=4))
            country.asns_routed = country_resource_list_from_ripe['resources']['asn']
            country.ipv4 = country_resource_list_from_ripe['resources']['ipv4']
            country.ipv6 = country_resource_list_from_ripe['resources']['ipv6']

        # задаем параметры для api
        params = {"resource": country_code, "lod": 1}

        # пытаемся получить данные по api
        try:
            country_asns_data_from_ripe = get(get_country_asns_url, params, timeout=30)
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

        queue.put(country)
    return queue


def insert_data_to_db(
        conn: psycopg2.connect,
        queue: queue.Queue
):
    cursor = conn.cursor()

    if create_table(cursor) == 0:

        queue_size = queue.qsize()
        while not queue.empty():
            country_data: classes.Country = queue.get()
            sql = """
            INSERT INTO country_data (
                country_code, 
                country_name, 
                ipv4_prefix_stats, 
                ipv4_prefix_ris, 
                ipv6_prefix_stats, 
                ipv6_prefix_ris, 
                asns_routed, 
                asns_stats, 
                asns_ris, 
                asns_registered_count, 
                asns_routed_count, 
                asns_non_routed, 
                days, 
                months, 
                months_human_read, 
                years, 
                ipv4, 
                ipv6
            ) 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            record_to_insert = (
                country_data.country_code + "2",
                country_data.country_name,
                country_data.ipv4_prefix_stats,
                country_data.ipv4_prefix_ris,
                country_data.ipv6_prefix_stats,
                country_data.ipv6_prefix_ris,
                [int(asns) for asns in country_data.asns_routed],
                country_data.asns_stats,
                country_data.asns_ris,
                country_data.asns_registered_count,
                country_data.asns_routed_count,
                [int(non_routed_asn) for non_routed_asn in country_data.asns_non_routed],
                list(set([int(day) for day in country_data.days])),
                list(set([int(month) for month in country_data.months])),
                list(set(country_data.months_human_read)),
                list(set([int(year) for year in country_data.years])),
                country_data.ipv4,
                country_data.ipv6,
            )

            cursor.execute(sql, record_to_insert)
            conn.commit()
            queue.task_done()

            queue_size -= 1
            print(f"Осталось вставить {queue_size} записей")


def create_table(cursor):
    create_table_sql = """
    create table country_data(
    country_code          text,
    country_name          text,
    ipv4_prefix_stats     integer[],
    ipv4_prefix_ris       integer[],
    ipv6_prefix_stats     integer[],
    ipv6_prefix_ris       integer[],
    asns_routed           integer[],
    asns_stats            integer[],
    asns_ris              integer[],
    asns_registered_count integer,
    asns_routed_count     integer,
    asns_non_routed       integer[],
    days                  integer[],
    months                integer[],
    months_human_read     text[],
    years                 integer[],
    ipv4                  text[],
    ipv6                  text[],
    asns_neighbour_count  integer,
    asns_neighbours       integer[]
    );

    alter table country_data
        owner to postgres;
    """

    check_table_exist = "SELECT table_name FROM information_schema.tables where table_name = 'country_data';"
    try:
        cursor.execute(check_table_exist)
        res = cursor.fetchall()
    except Exception as err:
        print(f"Не удалось выполнить запрос к БД: {check_table_exist}")
    if len(res) == 0:
        try:
            cursor.execute(create_table_sql)
            return 0
        except Exception as err:
            print(f"Не удалось создать таблицу в БД: {err}")
    else:
        return 0
