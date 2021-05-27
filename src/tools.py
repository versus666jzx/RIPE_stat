import calendar
from countries import countries
from requests import get, adapters
from json import loads, dumps
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import os


def GetResourceStats():
	adapters.DEFAULT_RETRIES = 3
	# yesterday = datetime.today().date() - timedelta(days=30)
	yesterday = datetime.today().date().replace(day=1)
	today = datetime.today().date()
	my_path = os.path.pardir

	url = 'https://stat.ripe.net/data/country-resource-stats/data.json'

	# asns_ris 	            number of ASNs seen in routing data
	# asns_stats 	        number of ASNs seen in registration data
	# v4_prefixes_ris 	    number of v4 prefixes seen in routing data
	# v4_prefixes_stats 	number of v4 prefixes seen in registration data
	# v6_prefixes_ris 	    number of v6 prefixes seen in routing data
	# v6_prefixes_stats 	number of v6 prefixes seen in registration data
	# stats_data 	        timestamp of the RIR stat file that is used for the registration data
	## timeline
	# starttime 	        Start time of this validity period.
	# endtime 	            End time of this validity period.

	for country in countries:

		t_keys = 'starttime', 'endtime',
		v4_prefixes_ris = []
		v6_prefixes_ris = []
		v4_prefixes_stats = []
		v6_prefixes_stats = []
		asns_ris = []
		asns_stats = []
		stats_date = []
		x = []
		n = 1

		country_code = country["code"]
		params = {"resource": country_code}
		params['starttime'] = yesterday
		params['endtime'] = today
		params['resolution'] = '5m'
		try:
			res = get(url, params, timeout=10)
		except Exception as err:
			res = None
			print(f"Ашипка апи, блэт: {err}")
			continue

		if res is not None:
			res = loads(res.text)['data']['stats']
			print(dumps(res, indent=4))
		for country_data in res:
			year = country_data['stats_date'].split('T')[0].split('-')[0]
			month_number = country_data['stats_date'].split('T')[0].split('-')[1]
			month = calendar.month_name[int(month_number)]
			day = country_data['stats_date'].split('T')[0].split('-')[2]
			v4_prefixes_ris.append(country_data['v4_prefixes_ris'])
			v6_prefixes_ris.append(country_data['v6_prefixes_ris'])
			v4_prefixes_stats.append(country_data['v4_prefixes_stats'])
			v6_prefixes_stats.append(country_data['v6_prefixes_stats'])
			asns_ris.append(country_data['asns_ris'])
			asns_stats.append(country_data['asns_stats'])
			stats_date.append(day)
			x.append(n)
			n += 1

		fig, axs = plt.subplots(3, 1, constrained_layout=True)

		fig.suptitle(f"ASNS and PREFIXES stat for {country['name']} in {month}", ha='center', size='x-large',
		             style='italic', color='C2')
		fig.set_figwidth(18)
		fig.set_figheight(13)

		axs[0].plot(stats_date, asns_ris, label="asns_ris")
		axs[0].plot(stats_date, asns_stats, label="asns_stats")
		axs[0].set_xlabel("Date")
		axs[0].set_ylabel("Number of AS")
		axs[0].set_title(f"ASNS stat")
		axs[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)

		axs[1].set_title(f"PREFIXES stat")
		axs[1].plot(stats_date, v4_prefixes_ris, label="v4_prefixes_ris")
		axs[1].plot(stats_date, v6_prefixes_ris, label="v6_prefixes_ris")
		axs[1].set_xlabel("Date")
		axs[1].set_ylabel("Number of prefixes")
		axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)

		axs[2].set_title(f"PREFIXES delete/add count")
		axs[2].plot(stats_date, v4_prefixes_stats, label="v4_prefixes_stat")
		axs[2].plot(stats_date, v6_prefixes_stats, label="v6_prefixes_stat")
		axs[2].set_xlabel("Date")
		axs[2].set_ylabel("Number of delete/add prefixes")
		axs[2].legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)

		plt.show()
		fig.savefig(fr"{my_path}\plots\{country['name']}-stat.png")


def GetCountryResourceList():
	url = "https://stat.ripe.net/data/country-resource-list/data.json"

	for country in countries:
		v4_prefixes_ris = []
		v6_prefixes_ris = []
		v4_prefixes_stats = []
		v6_prefixes_stats = []
		asns_ris = []
		asns_stats = []
		stats_date = []
		x = []
		n = 1

		country_code = country["code"]
		params = {"resource": country_code}

		try:
			res = get(url, params)
		except Exception as err:
			print(f"Ашипка апи, блэт: {err}")
		res = loads(res.text)["data"]
		print(dumps(res, indent=4))



GetCountryResourceList()
