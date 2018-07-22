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
	
	# This trigger will activate after battles when the player returns to the world map
	(0,
	[
		(try_begin),
			(eq, "$pti_after_battle_check", 1),
			
			(display_message, "@Battle is over, restoring player party"),
			
			(assign, "$pti_after_battle_check", 0),
			(call_script, "script_pti_restore_main_party"),
		(try_end),
	]),
	
	# For testing - trigger to bring up new party screen upon pressing T
	(0, 
	[
		(try_begin),
			(key_clicked, key_t),
			
			(call_script, "script_pti_count_individuals", "p_main_party", "script_cf_pti_true"),
			(assign, ":count", reg0),
			
			(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_true"),
			(try_for_range, ":unused", 0, ":count"),
				(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
				
				Individual.get("$pti_current_individual", "best_kill"),
				(assign, ":best_kill", reg0),
				Individual.get("$pti_current_individual", "knock_out_count"),
				(assign, reg1, reg0),
				Individual.get("$pti_current_individual", "kill_count"),
				(str_store_string, s0, "@{s0} {s1} has {reg0} kills and {reg1} knock outs."),
				(try_begin),
					(gt, ":best_kill", 0),
					
					(str_store_troop_name, s1, reg0),
					(str_store_string, s0, "@{s0} Best kill was of a {s1}"),
				(try_end),
				(display_message, s0),
				(call_script, "script_pti_get_next_individual", "p_main_party", "script_cf_pti_true"),
			(try_end),
			
			#(call_script, "script_pti_restore_main_party"),
		(try_end),
	])
]
