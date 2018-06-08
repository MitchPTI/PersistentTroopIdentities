# -*- coding: cp1254 -*-
from module_constants import faction_naming_regions
import collections
import os

names = {}

for filename in [f for f in os.listdir("./names") if os.path.isfile("./names/" + f) and f.endswith("_names.txt")]:
	(region, gender) = filename.split("_")[0:2]
	with open("./names/" + filename, "r") as fh:
		names[(region, gender)] = fh.readlines()

strings = []
for gender in ("boy", "girl"):
	for faction, regions in faction_naming_regions.iteritems():
		faction_names = set([])
		for region in regions:
			faction_names.update(names[(region, gender)])
		
		strings.extend([("{}_{}_name_{}".format(faction, gender, i), name.strip()) for i, name in enumerate(sorted(list(faction_names)))])
		end_string = "{}_{}_names_end".format(faction, gender)
		strings.append((end_string, "{!}" + end_string))

strings.extend([
	("pti_name_format_name", "{s1}"),
	("pti_name_format_troop_type_name", "{s0} {s1}"),
	("pti_name_format_name_brackets_troop_type", "{s1} ({s0})"),
	("pti_name_format_name_of_home", "{s1} of {s2}"),
	("pti_name_format_troop_type_name_of_home", "{s0} {s1} of {s2}"),
	("pti_name_format_name_of_home_brackets_troop_type", "{s1} of {s2} ({s0})"),
])
