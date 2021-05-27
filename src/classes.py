class Country:
	def __init__(self, data, *args, **kwargs):
		self.country_code = data[0] or kwargs.get("country_code")
		self.ipv4_prefix_stats = data[1] or kwargs.get("ipv4_prefix_stats")
		self.ipv4_prefix_ris = data[2] or kwargs.get("ipv4_prefix_ris")
		self.ipv6_prefix_stats = data[3] or kwargs.get("ipv6_prefix_stats")
		self.ipv6_prefix_ris = data[4] or kwargs.get("ipv6_prefix_ris")
		self.asns = data[5] or kwargs.get("asns")
		self.asns_stat = data[7] or kwargs.get("asns_stats")
		self.asns_ris = data[7] or kwargs.get("asns_ris")
