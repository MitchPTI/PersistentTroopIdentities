# -*- coding: cp1254 -*-
import collections
import math

from module_constants import *
from header_common import *
from header_operations import *
from header_items import *
from header_parties import *
from header_skills import *
from header_mission_templates import *
from header_items import *
from header_triggers import *
from header_terrain_types import *
from header_troops import *
from header_music import *
from header_map_icons import *
from header_presentations import *
from ID_items import *
from ID_animations import *
from ID_meshes import *

def set_names_operations(factions):
	operations = []
	for faction in factions:
		if faction.startswith("fac_"):
			operations.extend([
				(faction_set_slot, faction, pti_slot_faction_boy_names_begin, "str_{}_{}_name_1".format(faction, "boy"))
				, (faction_set_slot, faction, pti_slot_faction_boy_names_end, "str_{}_{}_names_end".format(faction, "boy"))
				, (faction_set_slot, faction, pti_slot_faction_girl_names_begin, "str_{}_{}_name_1".format(faction, "girl"))
				, (faction_set_slot, faction, pti_slot_faction_girl_names_end, "str_{}_{}_names_end".format(faction, "girl"))
			])
	
	return operations

new_scripts = [
	
	# script_pti_initialise
	("pti_initialise",
	set_names_operations(faction_naming_regions.keys()) + \
	[
		
	]),
	
	## ITERATION AND COUNTING SCRIPTS
	
	# script_pti_get_first_individual
	("pti_get_first_individual",
	[
		(store_script_param, ":condition_script", 1),
		
		(assign, "$pti_current_attributes_array", "$pti_first_attributes_array"),
		(assign, "$pti_current_individual_slot", len(array_slots)),
		
		(call_script, "script_pti_create_individual_reference", "$pti_current_attributes_array", "$pti_current_individual_slot"),
		(assign, "$pti_current_individual", reg0),
		
		(try_begin),
			(gt, ":condition_script", 0),
			
			(try_begin),
				(call_script, ":condition_script", "$pti_current_individual"),
			(else_try),
				(call_script, "script_pti_get_next_individual", ":condition_script"),
			(try_end),
		(try_end),
	]),
	
	# script_pti_get_next_individual
	("pti_get_next_individual",
	[
		(store_script_param, ":condition_script", 1),
		
		(call_script, "script_pti_pti_get_next_individual_array_and_slot", "$pti_current_attributes_array", "$pti_current_individual_slot"),
		(assign, "$pti_current_attributes_array", reg0),
		(assign, "$pti_current_individual_slot", reg1),
		
		(try_begin),
			(neg|party_slot_eq, "$pti_current_attributes_array", "$pti_current_individual_slot", 0),
			
			(call_script, "script_pti_create_individual_reference", "$pti_current_attributes_array", "$pti_current_individual_slot"),
			(assign, "$pti_current_individual", reg0),
		(else_try),
			(assign, "$pti_current_individual", 0),
		(try_end),
		
		(try_begin),
			(gt, ":condition_script", 0),
			(gt, "$pti_current_individual", 0),
			
			(try_begin),
				(call_script, ":condition_script", "$pti_current_individual"),
			(else_try),
				(call_script, "script_pti_get_next_individual", ":condition_script"),
			(try_end),
		(try_end),
	]),
	
	# script_pti_get_last_individual
	("pti_get_last_individual",
	[
		(assign, "$pti_current_attributes_array", "$pti_latest_attributes_array"),
		(party_get_slot, "$pti_current_individual_slot", "$pti_latest_attributes_array", pti_slot_array_size),
		(val_sub, "$pti_current_individual_slot", len(array_slots)),
		
		(call_script, "script_pti_create_individual_reference", "$pti_current_attributes_array", "$pti_current_individual_slot"),
		(assign, "$pti_current_individual", reg0),
	]),
	
	# script_pti_count_individuals
	("pti_count_individuals",
	[
		(store_script_param, ":condition_script", 1),
		
		(assign, ":count", 0),
		(assign, ":end_cond", "$pti_num_individuals"),
		(call_script, "script_pti_get_first_individual", ":condition_script"),
		(try_for_range, ":unused", 0, ":end_cond"),
			(gt, "$pti_current_individual", 0),
			
			(val_add, ":count", 1),
			(call_script, "script_pti_get_next_individual", ":condition_script"),
		(else_try),
			(assign, ":end_cond", 0),
		(try_end),
		
		(assign, reg0, ":count"),
	]),
	
	## INDIVIDUAL CONDITION SCRIPTS
	
	# script_cf_pti_false
	("cf_pti_false",
	[
		(eq, 0, 1),
	]),
	
	# script_cf_pti_true
	("cf_pti_true",
	[
		(eq, 1, 1),
	]),
	
	# script_cf_pti_individual_is_of_selected_troop
	("cf_pti_individual_is_of_selected_troop",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(this_or_next|eq, reg0, "$pti_nps_selected_troop_id"),
		(le, "$pti_nps_selected_troop_id", 0),
	]),
	
	## MISCELLANEOUS
	
	# script_pti_troop_get_name_range
	("pti_troop_get_name_range",
	[
		(store_script_param, ":troop_id", 1),
		
		(store_faction_of_troop, ":faction", ":troop_id"),
		(troop_get_type, ":gender", ":troop_id"),
		(try_begin),
			(eq, ":gender", tf_female),
			
			(faction_get_slot, ":names_begin", ":faction", pti_slot_faction_girl_names_begin),
			(faction_get_slot, ":names_end", ":faction", pti_slot_faction_girl_names_end),
			
			(try_begin),
				(eq, ":names_begin", 0),
				
				(assign, ":names_begin", "str_default_boy_name_1"),
				(assign, ":names_end", "str_default_boy_names_end"),
			(try_end),
		(else_try),
			(faction_get_slot, ":names_begin", ":faction", pti_slot_faction_boy_names_begin),
			(faction_get_slot, ":names_end", ":faction", pti_slot_faction_boy_names_end),
			
			(try_begin),
				(eq, ":names_begin", 0),
				
				(assign, ":names_begin", "str_default_girl_name_1"),
				(assign, ":names_end", "str_default_girl_names_end"),
			(try_end),
		(try_end),
		
		(assign, reg0, ":names_begin"),
		(assign, reg1, ":names_end"),
	]),
	
	# script_pti_create_individual_of_type
	("pti_create_individual_of_type",
	[
		(store_script_param, ":troop_id", 1),
		
		(call_script, "script_pti_create_individual"),
		(assign, ":individual", reg0),
		
		Individual.set(":individual", "troop_type", ":troop_id"),
		
		(call_script, "script_pti_troop_get_name_range", ":troop_id"),
		(assign, ":names_begin", reg0),
		(assign, ":names_end", reg1),
		
		(store_random_in_range, ":name", ":names_begin", ":names_end"),
		(val_sub, ":name", ":names_begin"),
		Individual.set(":individual", "name", ":name"),
		
		(assign, reg0, ":individual"),
	]),
	
	# script_pti_hire_troops_from_fief
	("pti_hire_troops_from_fief",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":num_troops", 3),
		(store_script_param, ":fief", 4),
		
		(party_add_members, ":party", ":troop_id", ":num_troops"),
		(try_for_range, ":individual", 0, ":num_troops"),
			(call_script, "script_pti_create_individual_of_type", ":troop_id"),
			(assign, ":individual", reg0),
			
			Individual.set(":individual", "home", ":fief"),
		(try_end),
	]),
	
	# script_pti_individual_get_type_and_name
	("pti_individual_get_type_and_name",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		Individual.get(":individual", "name"),
		(assign, ":name", reg0),
		(call_script, "script_pti_troop_get_name_range", ":troop_id"),
		(val_add, ":name", reg0),
		
		(str_store_troop_name, s0, ":troop_id"),
		(str_store_string, s1, ":name"),
		
		(assign, reg0, ":troop_id"),
		(assign, reg1, ":name"),
	]),
	
	## NEW PARTY SCREEN SCRIPTS ##
	
	# script_pti_nps_create_upper_left_stack_container
	("pti_nps_create_upper_left_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 29, 298, 262, 388),
	]),
	
	# script_pti_nps_create_upper_right_stack_container
	("pti_nps_create_upper_right_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 685, 298, 262, 388),
	]),
	
	# script_pti_nps_add_stacks_to_container
	("pti_nps_add_stacks_to_container",
	[
		(store_script_param, ":container", 1),
		(store_script_param, ":num_stacks", 2),
		(store_script_param, ":stack_init_script", 3),
		(store_script_param, ":highlight_condition_script", 4),
		(store_script_param, ":x_offset", 5),
		
		(set_container_overlay, ":container"),
		
		(store_mul, ":cur_y", 26, ":num_stacks"),
		(try_for_range, ":i", 0, ":num_stacks"),
			#(display_message, s0),
			(val_sub, ":cur_y", 26),
			
			# Call script to set the associated stack object (e.g. a troop id) and string (e.g. troop name)
			(call_script, ":stack_init_script", ":i"),
			(assign, ":stack_object", reg0),
			
			# Stack overlay
			(call_script, "script_gpu_create_image_button", mesh_party_member_button, mesh_party_member_button_pressed, ":x_offset", ":cur_y", 435),
			(assign, ":stack_button", reg1),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":stack_button", ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_containers", ":stack_button", ":container"),
			(troop_set_slot, "trp_pti_nps_overlay_is_stack_button", ":stack_button", 1),
			
			# Highlight overlay (initially invisible, made visible if stack highlighted)
			(call_script, "script_gpu_create_image_button", mesh_party_member_button_pressed, mesh_party_member_button_pressed, ":x_offset", ":cur_y", 435),
			(assign, ":highlight_button", reg1),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":highlight_button", ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_containers", ":highlight_button", ":container"),
			(troop_set_slot, "trp_pti_nps_stack_button_highlight_overlays", ":stack_button", ":highlight_button"),
			#(overlay_set_color, ":highlight_button", 0x000088),
			#(overlay_set_alpha, ":highlight_button", 0x44),
			(try_begin),
				(call_script, ":highlight_condition_script", ":stack_object"),
				#(display_message, "@Highlighting {s0}"),
				(overlay_set_display, ":stack_button", 0),
			(else_try),
				(overlay_set_display, ":highlight_button", 0),
			(try_end),
			
			# Stack text
			(store_add, ":text_y", ":cur_y", 2),
			(store_add, ":text_x", ":x_offset", 100),
			(call_script, "script_gpu_create_text_overlay", "str_s0", ":text_x", ":text_y", 900, 262, 26, tf_center_justify),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", reg1, ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", reg1, 1),
			(troop_set_slot, "trp_pti_nps_overlay_containers", reg1, ":container"),
			(troop_set_slot, "trp_pti_nps_stack_object_text_overlays", ":stack_object", reg1),
		(try_end),
		
		(set_container_overlay, -1),
	]),
	
	# script_cf_pti_troop_is_selected
	("cf_pti_troop_is_selected",
	[
		(store_script_param, ":troop_id", 1),
		
		(eq, ":troop_id", "$pti_nps_selected_troop_id"),
	]),
	
	# script_pti_nps_troop_stack_init
	("pti_nps_troop_stack_init",
	[
		(store_script_param, ":stack_no", 1),
		
		(party_stack_get_troop_id, ":troop_id", "p_main_party", ":stack_no"),
		(str_store_troop_name, s0, ":troop_id"),
		
		(try_begin),
			(troop_is_hero, ":troop_id"),
			
			(store_troop_health, reg0, ":troop_id"),
			(str_store_string, s0, "@{s0} ({reg0}%)"),
		(else_try),
			(party_stack_get_size, reg0, "p_main_party", ":stack_no"),
			(party_stack_get_num_wounded, reg1, "p_main_party", ":stack_no"),
			(gt, reg1, 0),
			
			(store_sub, reg2, reg0, reg1),
			(str_store_string, s0, "@{s0} ({reg2}/{reg0})"),
		(else_try),
			(str_store_string, s0, "@{s0} ({reg0})"),
		(try_end),
		
		(assign, reg0, ":troop_id"),
	]),
	
	# script_pti_nps_troop_stack_init
	("pti_nps_prisoner_troop_stack_init",
	[
		(store_script_param, ":stack_no", 1),
		
		(party_prisoner_stack_get_troop_id, ":troop_id", "p_main_party", ":stack_no"),
		(str_store_troop_name, s0, ":troop_id"),
		
		(try_begin),
			(troop_is_hero, ":troop_id"),
			
			(store_troop_health, reg0, ":troop_id"),
			(str_store_string, s0, "@{s0} ({reg0}%)"),
		(else_try),
			(party_prisoner_stack_get_size, reg0, "p_main_party", ":stack_no"),
			(str_store_string, s0, "@{s0} ({reg0})"),
		(try_end),
		
		(assign, reg0, ":troop_id"),
	]),
	
	# script_pti_nps_individual_stack_init
	("pti_nps_individual_stack_init",
	[
		(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
		(str_store_string_reg, s0, s1),
		
		(call_script, "script_pti_get_next_individual", "script_cf_pti_individual_is_of_selected_troop"),
	]),
	
	## LOW LEVEL SCRIPTS ##
	
	# script_pti_create_array
	("pti_create_array",
	[
		(spawn_around_party, "p_main_party", "pt_none"),
		(disable_party, reg0),
		(party_set_slot, reg0, pti_slot_array_size, len(array_slots)),
	]),
	
	# script_pti_create_individual
	("pti_create_individual",
	[
		(party_get_slot, ":next_slot", "$pti_latest_attributes_array", pti_slot_array_size),
		(try_begin),
			(eq, "$pti_latest_attributes_array", 0),
			
			(call_script, "script_pti_create_array"),
			(assign, "$pti_latest_attributes_array", reg0),
			(assign, "$pti_first_attributes_array", reg0),
			(assign, ":next_slot", len(array_slots)),
		(else_try),
			(gt, ":next_slot", Individual.attributes_slot_max),
			
			(call_script, "script_pti_create_array"),
			(assign, "$pti_latest_attributes_array", reg0),
			(assign, ":next_slot", len(array_slots)),
		(try_end),
		
		(store_add, ":new_size", ":next_slot", Individual.num_attribute_slots),
		(party_set_slot, "$pti_latest_attributes_array", pti_slot_array_size, ":new_size"),
		#(assign, reg0, "$pti_latest_attributes_array"),
		#(assign, reg1, ":next_slot"),
		#(display_message, "@Creating individual at party {reg0} slot {reg1}"),
		(call_script, "script_pti_create_individual_reference", "$pti_latest_attributes_array", ":next_slot"),
		
		(val_add, "$pti_num_individuals", 1),
	]),
	
	# script_pti_pti_get_next_individual_array_and_slot
	("pti_pti_get_next_individual_array_and_slot",
	[
		(store_script_param, reg0, 1),
		(store_script_param, reg1, 2),
		
		(val_add, reg1, Individual.num_attribute_slots),
		(try_begin),
			(gt, reg1, Individual.attributes_slot_max),
			
			(party_get_slot, reg0, reg0, pti_slot_array_next_array),
			(assign, reg1, len(array_slots)),
		(try_end),
	]),
	
	# script_pti_create_individual_reference
	("pti_create_individual_reference",
	[
		(store_script_param, reg0, 1),
		(store_script_param, reg1, 2),
		
		(val_lshift, reg0, Individual.attribute_slots_bitshift),
		(val_or, reg0, reg1),
	]),
	
	# script_pti_break_down_individual_reference
	("pti_break_down_individual_reference",
	[
		(store_script_param, reg1, 1),
		
		(assign, reg0, reg1),
		(val_rshift, reg0, Individual.attribute_slots_bitshift),
		(val_and, reg1, (2 ** Individual.attribute_slots_bitshift) - 1),
	]),
	
	# script_pti_individual_get_attribute
	# Should only be called from the method Individual.get(individual, attribute) in pti_constants
	# Given the relevant data transformation values from that method, this script returns the value of an attribute for an individual
	("pti_individual_get_attribute",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":offset", 2),
		(store_script_param, ":bitshift", 3),
		(store_script_param, ":bitmask", 4),
		
		(call_script, "script_pti_break_down_individual_reference", ":individual"),
		(val_add, reg0, ":offset"),
		(party_get_slot, ":data", reg0, reg1),
		#(assign, reg2, ":data"),
		#(display_message, "@Getting attribute from party {reg0} slot {reg1}. Data: {reg2}"),
		(val_rshift, ":data", ":bitshift"),
		(val_and, ":data", ":bitmask"),
		
		(assign, reg0, ":data"),
	]),
	
	# script_pti_individual_get_attribute
	# Should only be called from the method Individual.get(individual, attribute) in pti_constants
	# Given the relevant data transformation values from that method, this script returns the value of an attribute for an individual
	("pti_individual_set_attribute",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":offset", 2),
		(store_script_param, ":bitshift", 3),
		(store_script_param, ":bitmask", 4),
		(store_script_param, ":clear_mask", 5),
		(store_script_param, ":value", 6),
		
		(try_begin),
			(le, ":value", ":bitmask"),
			
			(call_script, "script_pti_break_down_individual_reference", ":individual"),
			(val_add, reg0, ":offset"),
			(party_get_slot, ":data", reg0, reg1),
			(val_and, ":data", ":clear_mask"),
			
			(val_lshift, ":value", ":bitshift"),
			(val_or, ":data", ":value"),
			#(assign, reg2, ":value"),
			#(display_message, "@Setting slot {reg1} for party {reg0} to {reg2}"),
			(party_set_slot, reg0, reg1, ":data"),
		(else_try),
			(assign, reg0, ":value"),
			(assign, reg1, ":bitmask"),
			(display_log_message, "@ERROR: Tried to add value of {reg0} to attribute for which the maximum value is {reg1}", 0xFF0000),
		(try_end),
	]),
]

def merge(scripts):
	for i, operation in enumerate(scripts["village_recruit_volunteers_recruit"].operations):
		if operation[0] == party_add_members:
			scripts["village_recruit_volunteers_recruit"].operations[i] = (call_script, "script_pti_hire_troops_from_fief", operation[1], operation[2], operation[3], "$current_town")
	
	scripts.extend(new_scripts)