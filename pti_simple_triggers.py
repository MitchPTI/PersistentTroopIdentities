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

new_simple_triggers = [
	
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
			
			#(display_message, "@Battle is over, restoring player party"),
			
			(assign, "$pti_after_battle_check", 0),
			(call_script, "script_pti_restore_party", "p_main_party"),
		(try_end),
	]),
	
	# Every hour, apply party healing to individuals
	(1,
	[
		(call_script, "script_pti_apply_wound_treatment_to_individuals", "p_main_party"),
	]),
	
	# Every 6 hours, remove the recent prisoner attribute from all individuals if there are none scheduled to potentially run away tonight (as indicated by g_prisoner_recruit_troop_id)
	(6,
	[
		(try_begin),
			(le, "$g_prisoner_recruit_troop_id", 0),
			
			pti_count_individuals(),
			(assign, ":count", reg0),
			
			pti_get_first_individual(),
			(try_for_range, ":unused", 0, ":count"),
				Individual.set("$pti_current_individual", "is_recent_prisoner", 0),
				
				pti_get_next_individual(),
			(try_end),
		(try_end),
	]),
	
	# For testing - trigger activated upon pressing T
	(0, 
	[
		(try_begin),
			(key_clicked, key_t),
			
			# Do stuff here
		(try_end),
	]),
	
	(24,
	[
		(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":troop_id", "p_main_party", ":stack"),
			(troop_is_hero, ":troop_id"),
			
			(store_skill_level, ":trainer_level", skl_trainer, ":troop_id"),
			(gt, ":trainer_level", 0),
			
			#(str_store_troop_name, s0, ":troop_id"),
			#(display_message, "@Applying trainer from {s0}"),
			
			(call_script, "script_pti_get_trainer_amount_for_level", ":trainer_level"),
			(assign, "$pti_xp_to_add", reg0),
			(store_character_level, ":level", ":troop_id"),
			(call_script, "script_pti_xp_needed_to_reach_level", ":level"),
			(assign, "$pti_comparison_xp", reg0),
			(call_script, "script_pti_apply_script_to_party_members_meeting_condition", "p_main_party", "script_pti_individual_add_xp", "script_cf_pti_individual_xp_lt"),
		(try_end),
	]),
]

def merge(simple_triggers):
	# Inject pti code into desertion of recently recruited prisoners to remove individuals
	for trigger in simple_triggers:
		for i, operation in enumerate(trigger.operations):
			if type(operation) == tuple and operation[0] == party_remove_members and (operation[1] == "p_main_party" or operation[1] == p_main_party) and operation[2] == "$g_prisoner_recruit_troop_id":
				# Delete (assign, ":num_escaped", reg0), which updates the num_escaped variable to the value returned by the party_remove_members operation
				if trigger.operations[i+1][0] == assign and trigger.operations[i+1][2] == reg0:
					del trigger.operations[i+1]
				
				# Replace the party_remove_members with pti code
				num_escaped = operation[3]
				trigger.operations[i:i+1] = [
					# Randomly "kill" the escaped number of individuals (just removes them from party and game)
					#(assign, reg0, num_escaped),
					#(display_message, "@Randomly choosing {reg0} individuals to be marked for killing"),
					pti_apply_script_randomly_to_party_members("script_pti_mark_individual_for_killing", num_escaped, condition = "script_cf_pti_individual_is_recent_prisoner"),
					(call_script, "script_pti_kill_individuals_in_party", "p_main_party", "script_cf_pti_individual_is_marked_for_killing"),
					
					# Remove the recent prisoner tag from the rest of the individuals, so no more are at risk of running away
					pti_count_individuals(),
					(assign, ":count", reg0),
					
					pti_get_first_individual(),
					(try_for_range, ":unused", 0, ":count"),
						Individual.set("$pti_current_individual", "is_recent_prisoner", 0),
						
						pti_get_next_individual(),
					(try_end),
				]
	
	simple_triggers.extend(new_simple_triggers)