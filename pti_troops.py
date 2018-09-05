from header_common import *
from header_items import *
from header_troops import *
from header_skills import *
from ID_factions import *
from ID_scenes import *
from module_constants import *

def blank_troop(id, flags=tf_hero):
	return [id, id, id, flags, 0, 0, fac_player_supporters_faction, [], level(1)|def_attrib, 0, 0, 0x000000000000000036db6db6db6db6db00000000001db6db0000000000000000, 0x000000000000000036db6db6db6db6db00000000001db6db0000000000000000]

troops = [
	# Used for checking when the game has been loaded and activating a trigger
	blank_troop("pti_load_check")
	
	# Mapping new party screen overlays to stack objects/containers
	, blank_troop("pti_nps_overlay_stack_objects")
	, blank_troop("pti_nps_overlay_containers")
	
	# New party screen boolean values
	, blank_troop("pti_nps_is_highlighted")
	, blank_troop("pti_nps_overlay_highlights_on_mouseover")
]

# Mapping new party screen stack objects to overlays
troops.extend([blank_troop("pti_nps_{}_{}_overlays".format(container, obj)) for container in pti_nps_containers for obj in pti_nps_objects])

# Individual troops - these are placeholder troops that have the appearance, name and equipment of an individual applied to them, for use in both battles and presentations
for i in xrange(1000):
	troop = blank_troop("pti_individual_{}".format(i), flags=tf_guarantee_all|tf_no_capture_alive)
	troops.append(troop)

troops.append(blank_troop("pti_individuals_end"))
