from header_common import *
from header_operations import *
from header_mission_templates import *
from header_animations import *
from header_sounds import *
from header_music import *
from header_items import *
from module_constants import *

####################################################################################################################
#   Each mission-template is a tuple that contains the following fields:
#  1) Mission-template id (string): used for referencing mission-templates in other files.
#     The prefix mt_ is automatically added before each mission-template id
#
#  2) Mission-template flags (int): See header_mission-templates.py for a list of available flags
#  3) Mission-type(int): Which mission types this mission template matches.
#     For mission-types to be used with the default party-meeting system,
#     this should be 'charge' or 'charge_with_ally' otherwise must be -1.
#     
#  4) Mission description text (string).
#  5) List of spawn records (list): Each spawn record is a tuple that contains the following fields:
#    5.1) entry-no: Troops spawned from this spawn record will use this entry
#    5.2) spawn flags.
#    5.3) alter flags. which equipment will be overriden
#    5.4) ai flags.
#    5.5) Number of troops to spawn.
#    5.6) list of equipment to add to troops spawned from here (maximum 8).
#  6) List of triggers (list).
#     See module_triggers.py for infomation about triggers.
#
#  Please note that mission templates is work in progress and can be changed in the future versions.
# 
####################################################################################################################

pilgrim_disguise = [itm_pilgrim_hood,itm_pilgrim_disguise,itm_practice_staff, itm_throwing_daggers]
af_castle_lord = af_override_horse | af_override_weapons| af_require_civilian

battle_templates = [
	"bandits_at_night"
	, "back_alley_kill_local_merchant"
	, "back_alley_revolt"
	, "lead_charge"
	, "village_attack_bandits"
	, "village_raid"
	, "besiege_inner_battle_castle"
	, "besiege_inner_battle_town_center"
	, "castle_attack_walls_defenders_sally"
	, "castle_attack_walls_belfry"
	, "castle_attack_walls_ladder"
	, "bandit_lair"
	, "town_fight"
]

pti_set_after_battle_check = (
  ti_before_mission_start, 0, 0, [],
  [
    (assign, "$pti_after_battle_check", 1),
	])

pti_set_up_individuals = (
  ti_before_mission_start, 0, 0, [],
  [
    (assign, ":pti_current_individual_troop", "trp_pti_individual_1"),
		
		(party_clear, "p_main_party"),
		(call_script, "script_pti_count_individuals", "p_main_party", "script_cf_pti_individual_is_not_wounded"),
		(assign, ":count", reg0),
		(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_individual_is_not_wounded"),
		(try_for_range, ":unused", 0, ":count"),
			(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
			(call_script, "script_pti_set_up_individual_troop", "$pti_current_individual", ":pti_current_individual_troop"),
			(party_add_members, "p_main_party", ":pti_current_individual_troop", 1),
			
			(call_script, "script_pti_get_next_individual", "p_main_party", "script_cf_pti_individual_is_not_wounded"),
			(assign, "$pti_current_individual", reg0),
			(val_add, ":pti_current_individual_troop", 1),
		(try_end),
  ])

pti_set_agent_individuals = (
  ti_on_agent_spawn, 0, 0, [],
  [
		(store_trigger_param, ":agent", 1),
		
		(try_begin),
			(agent_is_human, ":agent"),
			
			(agent_get_troop_id, ":troop_id", ":agent"),
			(troop_get_slot, ":individual", ":troop_id", pti_slot_troop_individual),
			(agent_set_slot, ":agent", pti_slot_agent_individual, ":individual"),
		(try_end),
  ])

pti_get_killer_team = (
  ti_on_agent_killed_or_wounded, 0, 0, [],
  [
		(store_trigger_param, ":agent", 2),
		
		(try_begin),
			(agent_is_human, ":agent"),
			
			(agent_get_team, "$pti_last_killer_team", ":agent"),
			(assign, "$pti_check_if_battle_is_over", 15),
		(try_end),
  ])

pti_restore_main_party = (
  0.1, 0, 0, [],
  [
    (try_begin),
			(gt, "$pti_check_if_battle_is_over", 0),
			
			(val_sub, "$pti_check_if_battle_is_over", 1),
			#(display_message, "@Checking if battle is over..."),
			
			(all_enemies_defeated, "$pti_last_killer_team"),
			
			(get_player_agent_no, ":player_agent"),
			(agent_get_team, ":player_team", ":player_agent"),
			(try_begin),
				(teams_are_enemies, ":player_team", "$pti_last_killer_team"),
				
				(display_message, "@Player's team has lost!"),
			(else_try),
				(display_message, "@Player's team has won!"),
			(try_end),
			
			(call_script, "script_pti_process_battle"),
			
			(display_message, "@Restoring player party"),
			(call_script, "script_pti_restore_main_party"),
			
			(assign, "$pti_check_if_battle_is_over", 0),
		(try_end),
  ])

pti_process_casualty = (
  ti_on_agent_killed_or_wounded, 0, 0, [],
  [
		(store_trigger_param, ":agent", 1),
		(store_trigger_param, ":killer_agent", 2),
		(store_trigger_param, ":wounded", 3),
		
		(try_begin),
			(agent_is_human, ":agent"),
			(agent_get_party_id, ":party", ":agent"),
			(eq, ":party", "p_main_party"),
			
			(call_script, "script_pti_individual_agent_process_casualty", ":agent", ":killer_agent", ":wounded"),
		(try_end),
  ])

pti_process_kill = (
  ti_on_agent_killed_or_wounded, 0, 0, [],
  [
		(store_trigger_param, ":agent", 1),
		(store_trigger_param, ":killer_agent", 2),
		(store_trigger_param, ":wounded", 3),
		
		(try_begin),
			(agent_is_human, ":agent"),
			(agent_is_human, ":killer_agent"),
			(agent_get_party_id, ":party", ":killer_agent"),
			(eq, ":party", "p_main_party"),
			
			(agent_get_troop_id, ":troop_id", ":killer_agent"),
			(neg|troop_is_hero, ":troop_id"),
			
			(agent_get_troop_id, ":troop_id", ":agent"),
			(call_script, "script_pti_troop_get_xp_for_killing", ":troop_id"),
			(assign, ":xp_for_kill", reg0),
			
			(agent_get_slot, ":xp_gained", ":killer_agent", pti_slot_agent_xp_gained),
			(val_add, ":xp_gained", ":xp_for_kill"),
			(agent_set_slot, ":killer_agent", pti_slot_agent_xp_gained, ":xp_gained"),
			
			(val_add, ":wounded", 1),
			(set_trigger_result, ":wounded"),	# This is necessary because script_pti_troop_get_xp_for_killing calls script_game_get_prisoner_price, which calls set_trigger_result and inadvertently overrides all kills to knocked unconscious
		(try_end),
  ])

def merge(mission_templates):
	for template_id in battle_templates:
		mission_templates[template_id].triggers.extend([
			pti_set_after_battle_check
			, pti_set_up_individuals
			, pti_set_agent_individuals
			, pti_get_killer_team
			, pti_restore_main_party
			, pti_process_casualty
			, pti_process_kill
		])
