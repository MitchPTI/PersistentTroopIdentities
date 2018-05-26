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
	
	# This trigger will activate upon the game being loaded
	(0,
	[
		(try_begin),
			(store_item_kind_count, reg0, "itm_no_item", "trp_pti_load_check"),
			(eq, reg0, 0),
			
			(call_script, "script_pti_initialise"),
			
			(troop_add_item, "trp_pti_load_check", "itm_no_item"),
		(try_end),
	]),
	
	(0, 
	[
		(try_begin),
			(key_clicked, key_t),
			
			(assign, "$pti_nps_selected_troop_id", -1),
			(start_presentation, "prsnt_new_party_screen"),
			
			#(call_script, "script_pti_get_first_individual", "script_cf_pti_true"),
			#(try_for_range, ":unused", 0, "$pti_num_individuals"),
			#	(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
			#	
			#	Individual.get("$pti_current_individual", "home"),
			#	(str_store_party_name, s2, reg0),
			#	
			#	(display_message, "@{s0} {s1} from {s2}"),
			#	
			#	(call_script, "script_pti_get_next_individual", "script_cf_pti_true"),
			#(try_end),
		(try_end),
	])
]