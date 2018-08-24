from header_game_menus import *
from header_parties import *
from header_items import *
from header_mission_templates import *
from header_music import *
from header_terrain_types import *
from header_troops import *

from ID_skills import *
from ID_troops import *
from ID_parties import *

from module_constants import *

####################################################################################################################
#  (menu-id, menu-flags, menu_text, mesh-name, [<operations>], [<options>]),
#
#   Each game menu is a tuple that contains the following fields:
#
#  1) Game-menu id (string): used for referencing game-menus in other files.
#     The prefix menu_ is automatically added before each game-menu-id
#
#  2) Game-menu flags (int). See header_game_menus.py for a list of available flags.
#     You can also specify menu text color here, with the menu_text_color macro
#  3) Game-menu text (string).
#  4) mesh-name (string). Not currently used. Must be the string "none"
#  5) Operations block (list). A list of operations. See header_operations.py for reference.
#     The operations block is executed when the game menu is activated.
#  6) List of Menu options (List).
#     Each menu-option record is a tuple containing the following fields:
#   6.1) Menu-option-id (string) used for referencing game-menus in other files.
#        The prefix mno_ is automatically added before each menu-option.
#   6.2) Conditions block (list). This must be a valid operation block. See header_operations.py for reference.
#        The conditions are executed for each menu option to decide whether the option will be shown to the player or not.
#   6.3) Menu-option text (string).
#   6.4) Consequences block (list). This must be a valid operation block. See header_operations.py for reference.
#        The consequences are executed for the menu option that has been selected by the player.
#
#
# Note: The first Menu is the initial character creation menu.
####################################################################################################################

party_screen_option = (
	"party_screen", [], "Open Party Screen",
	[
		(assign, "$pti_nps_open_agent_screen", 0),
		(assign, "$pti_nps_selected_troop_id", "trp_player"),
		(assign, "$pti_nps_selected_individual", -1),
		(start_presentation, "prsnt_new_party_screen"),
	])

quick_start_option = (
	"quick_start", [], "Quick Start",
	[
		(assign, "$pti_quick_start", 1),
		
		(troop_raise_attribute, "trp_player", ca_strength, 11),
		(troop_raise_attribute, "trp_player", ca_agility, 5),
		(troop_raise_skill, "trp_player", skl_power_draw, 6),
		(troop_raise_skill, "trp_player", skl_power_strike, 5),
		(troop_raise_skill, "trp_player", skl_riding, 5),
		(troop_raise_skill, "trp_player", skl_leadership, 5),
		(troop_raise_skill, "trp_player", skl_prisoner_management, 5),
		(troop_add_item, "trp_player", "itm_heraldic_mail_with_surcoat"),
		(troop_add_item, "trp_player", "itm_great_helmet"),
		(troop_add_item, "trp_player", "itm_iron_greaves"),
		(troop_add_item, "trp_player", "itm_gauntlets"),
		(troop_add_item, "trp_player", "itm_great_sword"),
		(troop_add_item, "trp_player", "itm_war_bow"),
		(troop_add_item, "trp_player", "itm_bodkin_arrows"),
		(troop_add_item, "trp_player", "itm_steel_shield"),
		(troop_add_item, "trp_player", "itm_charger"),
		(troop_add_item, "trp_player", "itm_bread"),
		(troop_add_item, "trp_player", "itm_bread"),
		(troop_add_item, "trp_player", "itm_bread"),
		(call_script, "script_troop_add_gold", "trp_player", 50000),
		
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_swadian_recruit, p_village_1, 5),
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_vaegir_recruit, p_village_16, 5),
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_khergit_tribesman, p_village_44, 5),
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_nord_recruit, p_village_66, 5),
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_rhodok_tribesman, p_village_40, 5),
		#(call_script, "script_pti_recruit_troops_from_center", "p_main_party", trp_sarranid_recruit, p_village_91, 5),
		
		(party_relocate_near_party, "p_main_party", "p_town_6", 2),
		(jump_to_menu, "mnu_start_phase_2"),
	])

def merge(game_menus):
	game_menus["camp"].options.append(party_screen_option)
	
	game_menus["start_game_0"].options.append(quick_start_option)
	game_menus["start_phase_2"].operations[0:0] = [
		(try_begin),
			(eq, "$pti_quick_start", 1),
			
			(change_screen_return),
		(try_end),
	]