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
			
			## CHECK PARTY MEMBERS
			
			(display_message, "@Party members:"),
			
			(call_script, "script_pti_party_get_num_individuals", "p_main_party"),
			(assign, ":size", reg0),
			(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_true"),
			(try_for_range, ":unused", 0, ":size"),
				Individual.get("$pti_current_individual", "home"),
				(assign, ":home", reg0),
				(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
				(str_store_party_name, s2, ":home"),
				(call_script, "script_pti_individual_get_days_of_service", "$pti_current_individual"),
				(display_message, "@{s1} is a {s0} from {s2} who has been in service for {reg0} days"),
				
				(call_script, "script_pti_get_next_individual", "p_main_party", "script_cf_pti_true"),
			(try_end),
		(try_end),
	])
]