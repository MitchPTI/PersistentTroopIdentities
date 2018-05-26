from header_common import *
from header_items import *
from header_troops import *
from header_skills import *
from ID_factions import *
from ID_scenes import *
from module_constants import *

def blank_troop(id, flags=tf_hero):
	return [id, id, id, flags, 0, 0, fac_player_supporters_faction, [], level(1)|def_attrib, 0, 0, 0, 0]

troops = [
	blank_troop("pti_load_check")
	, blank_troop("pti_nps_overlay_stack_objects")
	, blank_troop("pti_nps_overlay_containers")
	, blank_troop("pti_nps_is_highlighted")
	, blank_troop("pti_nps_stack_button_highlight_overlays")
	, blank_troop("pti_nps_overlay_highlights_on_mouseover")
	, blank_troop("pti_nps_stack_object_text_overlays")
	, blank_troop("pti_nps_overlay_is_stack_button")
]