# -*- coding: cp1254 -*-
from header_common import *
from header_dialogs import *
from header_operations import *
from header_parties import *
from header_item_modifiers import *
from header_skills import *
from header_triggers import *
from ID_troops import *
from ID_party_templates import *
from ID_parties import *
##diplomacy start+
from header_troops import ca_intelligence
from header_terrain_types import *
from header_items import * #For ek_food, and so forth
##diplomacy end+
from module_constants import *


####################################################################################################################
# During a dialog, the dialog lines are scanned from top to bottom.
# If the dialog-line is spoken by the player, all the matching lines are displayed for the player to pick from.
# If the dialog-line is spoken by another, the first (top-most) matching line is selected.
#
#  Each dialog line contains the following fields:
# 1) Dialogue partner: This should match the person player is talking to.
#    Usually this is a troop-id.
#    You can also use a party-template-id by appending '|party_tpl' to this field.
#    Use the constant 'anyone' if you'd like the line to match anybody.
#    Appending '|plyr' to this field means that the actual line is spoken by the player
#    Appending '|other(troop_id)' means that this line is spoken by a third person on the scene.
#       (You must make sure that this third person is present on the scene)
#
# 2) Starting dialog-state:
#    During a dialog there's always an active Dialog-state.
#    A dialog-line's starting dialog state must be the same as the active dialog state, for the line to be a possible candidate.
#    If the dialog is started by meeting a party on the map, initially, the active dialog state is "start"
#    If the dialog is started by speaking to an NPC in a town, initially, the active dialog state is "start"
#    If the dialog is started by helping a party defeat another party, initially, the active dialog state is "party_relieved"
#    If the dialog is started by liberating a prisoner, initially, the active dialog state is "prisoner_liberated"
#    If the dialog is started by defeating a party led by a hero, initially, the active dialog state is "enemy_defeated"
#    If the dialog is started by a trigger, initially, the active dialog state is "event_triggered"
# 3) Conditions block (list): This must be a valid operation block. See header_operations.py for reference.
# 4) Dialog Text (string):
# 5) Ending dialog-state:
#    If a dialog line is picked, the active dialog-state will become the picked line's ending dialog-state.
# 6) Consequences block (list): This must be a valid operation block. See header_operations.py for reference.
# 7) Voice-over (string): sound filename for the voice over. Leave here empty for no voice over
####################################################################################################################

new_dialogs = [
	[anyone, "start",
		[
			(store_conversation_troop, "$g_talk_troop"),
			(is_between, "$g_talk_troop", pti_individual_troops_begin, pti_individual_troops_end),
			(call_script, "script_dplmc_print_subordinate_says_sir_madame_to_s0"),
		],
		"Your orders {s0}?", "regular_member_talk", []
	],
]

def get_dialogs(dialogs, state):
	return [dialog for dialog in dialogs if dialog.state == state]

def merge(dialogs):
	# Add individuals to party when getting recruits from the train troops quest
	train_troops_accepted_dialogs = get_dialogs(dialogs, "lord_mission_raise_troops_accepted")
	for dialog in train_troops_accepted_dialogs:
		for i, operation in enumerate(dialog.consequences):
			if type(operation) == tuple and operation[0] == party_add_members and (operation[1] == "p_main_party" or operation[1] == p_main_party):
				troop_id = operation[2]
				size = operation[3]
				dialog.consequences[i] = (call_script, "script_pti_collect_troops_from_train_troop_quest", "p_main_party", troop_id, "$g_talk_troop", size)
	
	if not train_troops_accepted_dialogs:
		print "Could not find lord_mission_raise_troops_accepted dialog"
	
	# Remove individuals from party when handing over trained troops from the train troops quest
	train_troops_thank_dialogs = get_dialogs(dialogs, "lord_active_mission_2")
	for dialog in train_troops_thank_dialogs:
		for i, operation in enumerate(dialog.consequences):
			if type(operation) == tuple and operation[0] == party_remove_members and (operation[1] == "p_main_party" or operation[1] == p_main_party):
				troop_id = operation[2]
				size = operation[3]
				dialog.consequences[i:i+1] = [
					(call_script, "script_pti_count_individuals", "p_main_party", "script_cf_pti_individual_is_from_train_troops_quest"),
					(assign, ":count", reg0),
					
					# First remove all individuals flagged as being given to the player by the quest giver
					(call_script, "script_pti_kill_individuals_in_party", "p_main_party", "script_cf_pti_individual_is_from_train_troops_quest"),
					
					# If some of those have been lost, provide the difference, taking those at the end of the party list first (so by default, the most recently recruited)
					(store_sub, ":difference", size, ":count"),
					(assign, "$pti_selected_troop_id", troop_id),
					(try_for_range, ":unused", 0, ":difference"),
						(call_script, "script_pti_get_last_individual", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
						(call_script, "script_pti_kill_individual_in_party", "$pti_current_individual", "p_main_party"),
					(try_end),
					
					(call_script, "script_pti_restore_party", "p_main_party"),
				]
	
	if not train_troops_thank_dialogs:
		print "Could not find lord_mission_raise_troops_accepted dialog"
	
	start_dialogs = get_dialogs(dialogs, "start")
	start_dialog_indexes = [i for i, dialog in enumerate(dialogs) if dialog.state == "start"]
	for index in reversed(start_dialog_indexes):
		dialogs.remove(index)
	
	dialogs.extend(new_dialogs)
	dialogs.extend(start_dialogs)