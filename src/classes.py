from matplotlib import pyplot as plt


class Country:
	def __init__(self, *args, **kwargs):
		self.country_code: str = kwargs.get("country_code")
		self.country_name: str = kwargs.get("country_name")
		self.ipv4_prefix_stats: list = kwargs.get("ipv4_prefix_stats")
		self.ipv4_prefix_ris: list = kwargs.get("ipv4_prefix_ris")
		self.ipv6_prefix_stats: list = kwargs.get("ipv6_prefix_stats")
		self.ipv6_prefix_ris: list = kwargs.get("ipv6_prefix_ris")
		self.asns_routed: list = kwargs.get("asns_routed")
		self.asns_stats: list = kwargs.get("asns_stats")
		self.asns_ris: list = kwargs.get("asns_ris")
		self.asns_registered_count: str or int = kwargs.get("asns_registered_count")
		self.asns_routed_count: str or int = kwargs.get("asns_routed_count")
		self.asns_non_routed: str or int = kwargs.get("asns_non_routed")
		self.days: list = kwargs.get("days")
		self.months: list = kwargs.get("months")
		self.months_human_read: list = kwargs.get("months_human_read")
		self.years: list = kwargs.get("years")
		self.ipv4: list = kwargs.get("ipv4")
		self.ipv6: list = kwargs.get("ipv6")

