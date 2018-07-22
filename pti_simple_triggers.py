from header_common import *
from header_operations import *
from header_parties import *
from header_items import *
from header_skills import *
from header_triggers import *
from header_troops import *
from header_music import *
from ID_troops import *
from ID_parties import *

from module_constants import *

####################################################################################################################
# Simple triggers are the alternative to old style triggers. They do not preserve state, and thus simpler to maintain.
#
#  Each simple trigger contains the following fields:
# 1) Check interval: How frequently this trigger will be checked
# 2) Operation block: This must be a valid operation block. See header_operations.py for reference.
####################################################################################################################

simple_triggers = [
	
	# This trigger will activate each time the game is loaded
	(0,
	[
		(try_begin),
			(store_item_kind_count, reg0, "itm_no_item", "trp_pti_load_check"),
			(eq, reg0, 0),
			
			(troop_add_item, "trp_pti_load_check", "itm_no_item"),
		(try_end),
	]),
	
	# This trigger will activate once (having as trigger instead of addition to script_game_start will hopefully allow some degree of save game compatibility with other mods)
	(0,
	[
		(try_begin),
			(eq, "$pti_initialised", 0),
			
			(call_script, "script_pti_initialise"),
			
			(assign, "$pti_initialised", 1),
		(try_end),
	]),
	
	# For testing - trigger to bring up new party screen upon pressing T
	(0, 
	[
		(try_begin),
			(key_clicked, key_t),
			
			(call_script, "script_pti_linked_list_init"),
			(assign, ":list", reg0),
			
			(str_store_string, s0, "@Adding numbers to linked list:"),
			(try_for_range, reg0, 0, 10),
				(str_store_string, s0, "@{s0} {reg0}"),
				(call_script, "script_pti_linked_list_append", ":list", reg0),
			(try_end),
			
			(display_message, s0),
			
			(store_random_in_range, reg0, 0, 10),
			(display_message, "@Removing {reg0}"),
			(call_script, "script_pti_linked_list_remove", ":list", reg0),
			
			(str_store_string, s0, "@Numbers after removal:"),
			
			(party_get_slot, ":size", ":list", pti_slot_array_size),
			(call_script, "script_pti_linked_list_get_head_node", ":list"),
			(try_for_range, ":unused", 0, ":size"),
				(str_store_string, s0, "@{s0} {reg0}"),
				(call_script, "script_pti_linked_list_get_node", ":list", reg1),
			(try_end),
			
			(display_message, s0),
		(try_end),
	])
]
