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
from header_presentations import *
from ID_items import *
from ID_animations import *
from ID_meshes import *

def set_names_operations(factions):
	operations = []
	for faction in factions:
		if faction.startswith("fac_"):
			operations.extend([
				(faction_set_slot, faction, pti_slot_faction_male_names_begin, get_start_name(faction, "male"))
				, (faction_set_slot, faction, pti_slot_faction_male_names_end, get_end_name(faction, "male"))
				, (faction_set_slot, faction, pti_slot_faction_female_names_begin, get_start_name(faction, "female"))
				, (faction_set_slot, faction, pti_slot_faction_female_names_end, get_end_name(faction, "male"))
			])
	
	return operations

def individual_get_item(equipment_type="base"):
	weapons_attribute = "{}_weapons".format(equipment_type)
	armour_attribute = "{}_armour".format(equipment_type)
	return ("pti_individual_get_{}_item".format(equipment_type),
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":slot", 2),
		
		(try_begin),
			(lt, ":slot", ek_head),
			
			(store_mul, ":bitshift", ITEM_BITS, ":slot"),
			(val_add, ":bitshift", Individual.attribute_bitshifts[weapons_attribute]),
			(call_script, "script_pti_individual_get_attribute", ":individual", Individual.attribute_offsets[weapons_attribute], ":bitshift", mask(ITEM_BITS)),
		(else_try),
			(lt, ":slot", ek_horse),
			
			(store_sub, ":bitshift", ":slot", ek_head),
			(val_mul, ":bitshift", ITEM_BITS),
			(val_add, ":bitshift", Individual.attribute_bitshifts[armour_attribute]),
			(call_script, "script_pti_individual_get_attribute", ":individual", Individual.attribute_offsets[armour_attribute], ":bitshift", mask(ITEM_BITS)),
		(else_try),
			(eq, ":slot", ek_horse),
			
			Individual.get(":individual", "{}_horse".format(equipment_type)),
		(try_end),
	])

def individual_set_item(equipment_type="base"):
	weapons_attribute = "{}_weapons".format(equipment_type)
	armour_attribute = "{}_armour".format(equipment_type)
	return ("pti_individual_set_{}_item".format(equipment_type),
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":slot", 2),
		(store_script_param, ":item", 3),
		
		(try_begin),
			(lt, ":slot", ek_head),
			
			(store_mul, ":bitshift", ITEM_BITS, ":slot"),
			(val_add, ":bitshift", Individual.attribute_bitshifts[weapons_attribute]),
			(assign, ":mask", mask(ITEM_BITS)),
			(val_lshift, ":mask", ":bitshift"),
			(store_sub, ":clear_mask", mask(63), ":mask"),
			(call_script, "script_pti_individual_set_attribute", ":individual", Individual.attribute_offsets[weapons_attribute], ":bitshift", mask(ITEM_BITS), ":clear_mask", ":item"),
		(else_try),
			(lt, ":slot", ek_horse),
			
			(store_sub, ":bitshift", ":slot", ek_head),
			(val_mul, ":bitshift", ITEM_BITS),
			(val_add, ":bitshift", Individual.attribute_bitshifts[armour_attribute]),
			(assign, ":mask", mask(ITEM_BITS)),
			(val_lshift, ":mask", ":bitshift"),
			(store_sub, ":clear_mask", mask(63), ":mask"),
			(call_script, "script_pti_individual_set_attribute", ":individual", Individual.attribute_offsets[armour_attribute], ":bitshift", mask(ITEM_BITS), ":clear_mask", ":item"),
		(else_try),
			(eq, ":slot", ek_horse),
			
			Individual.set(":individual", "{}_horse".format(equipment_type), ":item"),
		(try_end),
	])

new_scripts = [
	
	# script_pti_initialise
	("pti_initialise",
	set_names_operations(faction_naming_regions.keys()) + \
	[
		(call_script, "script_pti_linked_list_init"),
		(party_set_slot, "p_main_party", pti_slot_party_individuals, reg0),
		(party_set_name, reg0, "@Player Party Individuals Array - You should not be seeing this"),
		
		(call_script, "script_pti_linked_list_init"),
		(assign, "$pti_individuals_array", reg0),
		(party_set_name, "$pti_individuals_array", "@Individuals Data - You should not be seeing this"),
		
		(assign, "$pti_individual_name_format", "str_pti_name_format_troop_type_name"),
	]),
	
	## ARRAY SCRIPTS
	
	# script_pti_array_init
	("pti_array_init",
	[
		(set_spawn_radius, 0),
		(spawn_around_party, "p_temp_party", "pt_array"),
		#(party_set_flags, reg0, pf_disabled, 1),
		(disable_party, reg0),
	]),
	
	# script_pti_array_get
	("pti_array_get",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":array"),
			(eq, ":template", "pt_array"),
			
			(store_add, ":slot", pti_array_slots_start, ":index"),
			(try_begin),
				(ge, ":slot", pti_array_slot_max),
				
				(party_get_slot, ":array", ":array", pti_slot_array_next_array),
				(try_begin),
					(gt, ":array", 0),
					
					(val_sub, ":slot", pti_array_slot_max),
					(call_script, "script_pti_array_get", ":array", ":slot"),
				(else_try),
					(display_log_message, "@ERROR: Tried to get array value from next array, but none found", 0xFF00000),
					(assign, reg0, -1),
				(try_end),
			(else_try),
				(party_get_slot, reg0, ":array", ":slot"),
			(try_end),
		(else_try),
			(assign, reg0, ":array"),
			(display_log_message, "@ERROR: script_pti_array_get was called without a valid array being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_array_set
	("pti_array_set",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":array"),
			(eq, ":template", "pt_array"),
			
			(store_add, ":slot", pti_array_slots_start, ":index"),
			(try_begin),
				(ge, ":slot", pti_array_slot_max),
				
				(try_begin),
					(neg|party_slot_ge, ":array", pti_slot_array_next_array, 1),
					
					(call_script, "script_pti_array_init"),
					(party_set_slot, ":array", pti_slot_array_next_array, reg0),
				(try_end),
				
				(party_get_slot, ":array", ":array", pti_slot_array_next_array),
				(val_sub, ":slot", pti_array_slot_max),
				(call_script, "script_pti_array_set", ":array", ":slot", ":value"), 
			(else_try),
				(party_set_slot, ":array", ":slot", ":value"),
			(try_end),
		(else_try),
			(assign, reg0, ":array"),
			(display_log_message, "@ERROR: script_pti_array_set was called without a valid array being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_array_append
	("pti_array_append",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":value", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":array"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":index", ":array", pti_slot_array_size),
			(call_script, "script_pti_array_set", ":array", ":index", ":value"),
			(store_add, ":size", ":index", 1),
			(party_set_slot, ":array", pti_slot_array_size, ":size"),
		(else_try),
			(assign, reg0, ":array"),
			(display_log_message, "@ERROR: script_pti_array_append was called without a valid array being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_array_swap
	("pti_array_swap",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index_1", 2),
		(store_script_param, ":index_2", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":array"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_array_get", ":array", ":index_1"),
			(assign, ":element_1", reg0),
			(call_script, "script_pti_array_get", ":array", ":index_2"),
			(assign, ":element_2", reg0),
			
			(call_script, "script_pti_array_set", ":array", ":index_1", ":element_2"),
			(call_script, "script_pti_array_set", ":array", ":index_2", ":element_1"),
		(else_try),
			(assign, reg0, ":array"),
			(display_log_message, "@ERROR: script_pti_array_swap was called without a valid array being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	## LINKED LIST SCRIPTS
	
	# script_pti_linked_list_init
	("pti_linked_list_init",
	[
		(call_script, "script_pti_array_init"),
	]),
	
	# script_pti_linked_list_get_node
	("pti_linked_list_get_node",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_array_get", ":list", ":index"),
			(assign, ":node", reg0),
			(store_and, reg0, ":node", pti_list_node_value_mask),
			
			(val_rshift, ":node", pti_list_next_node_bitshift),
			(store_and, reg1, ":node", pti_list_node_mask),
			
			(val_rshift, ":node", pti_list_node_bits),
			(store_and, reg2, ":node", pti_list_node_mask),
			
			(assign, reg3, ":index"),
			#(display_message, "@Index: {reg3} | Value: {reg0} | Next index: {reg1} | Prev index: {reg2}"),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_get_node was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_get_head_node
	("pti_linked_list_get_head_node",
	[
		(store_script_param, ":list", 1),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":head_index", ":list", pti_slot_list_head),
			(call_script, "script_pti_linked_list_get_node", ":list", ":head_index"),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_get_head_node was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_get_tail_node
	("pti_linked_list_get_tail_node",
	[
		(store_script_param, ":list", 1),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":head_index", ":list", pti_slot_list_head),
			(call_script, "script_pti_linked_list_get_node", ":list", ":head_index"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg2),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_get_tail_node was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_count
	("pti_linked_list_count",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":condition_script", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(assign, ":count", 0),
			(party_get_slot, ":size", ":list", pti_slot_array_size),
			
			(call_script, "script_pti_linked_list_get_head_node", ":list"),
			(assign, ":next", reg1),
			
			(try_for_range, ":unused", 0, ":size"),
				(try_begin),
					(call_script, ":condition_script", reg0),
					
					(val_add, ":count", 1),
				(try_end),
				
				(call_script, "script_pti_linked_list_get_node", ":list", ":next"),
				(assign, ":next", reg1),
			(try_end),
			
			(assign, reg0, ":count"),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_count was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_node_set_prev
	("pti_node_set_prev",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":prev", 2),
		
		(val_and, reg0, pti_list_prev_node_clear_mask),
		(val_lshift, ":prev", pti_list_prev_node_bitshift),
		(val_or, reg0, ":prev"),
	]),
	
	# script_pti_node_set_next
	("pti_node_set_next",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":next", 2),
		
		(val_and, reg0, pti_list_next_node_clear_mask),
		(val_lshift, ":next", pti_list_next_node_bitshift),
		(val_or, reg0, ":next"),
	]),
	
	# script_pti_node_set_value
	("pti_node_set_value",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":value", 2),
		
		(val_and, reg0, pti_list_node_value_clear_mask),
		(val_or, reg0, ":value"),
	]),
	
	# script_pti_linked_list_set_prev
	("pti_linked_list_set_prev",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":prev", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_array_get", ":list", ":index"),
			(call_script, "script_pti_node_set_prev", reg0, ":prev"),
			(call_script, "script_pti_array_set", ":list", ":index", reg0),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_set_prev was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_set_next
	("pti_linked_list_set_next",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":next", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_array_get", ":list", ":index"),
			(call_script, "script_pti_node_set_next", reg0, ":next"),
			(call_script, "script_pti_array_set", ":list", ":index", reg0),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_set_next was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_set_value
	("pti_linked_list_set_value",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_array_get", ":list", ":index"),
			(call_script, "script_pti_node_set_value", reg0, ":value"),
			(call_script, "script_pti_array_set", ":list", ":index", reg0),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_set_value was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_insert_before
	("pti_linked_list_insert_before",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		(store_script_param, ":reset_head", 4),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":new_index", ":list", pti_slot_array_size),
			
			# Get the neighbour nodes that will be modified to accommodate the new node (in this case current and previous)
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":prev_index", reg2),
			
			# Modify the neighbour nodes to point to the new node
			(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index", ":new_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":index", ":new_index"),
			
			# Create the new node
			(assign, reg0, ":value"),
			(call_script, "script_pti_node_set_next", reg0, ":index"),
			(call_script, "script_pti_node_set_prev", reg0, ":prev_index"),
			(assign, ":new_node", reg0),
			(call_script, "script_pti_array_append", ":list", ":new_node"),
			
			# If inserting before the head node and reset_head is selected, make this the new head node
			(try_begin),
				(party_slot_eq, ":list", pti_slot_list_head, ":index"),
				(neq, ":reset_head", 0),
				
				(party_set_slot, ":list", pti_slot_list_head, ":new_index"),
				#(assign, reg0, ":new_index"),
				#(display_message, "@Setting head to index {reg0}"),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_insert_before was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_insert_after
	("pti_linked_list_insert_after",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":new_index", ":list", pti_slot_array_size),
			
			# Get the neighbour nodes that will be modified to accommodate the new node (in this case current and next)
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":next_index", reg1),
			
			# Modify the neighbour nodes to point to the new node
			(call_script, "script_pti_linked_list_set_next", ":list", ":index", ":new_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index", ":new_index"),
			
			# Create the new node
			(assign, reg0, ":value"),
			(call_script, "script_pti_node_set_next", reg0, ":next_index"),
			(call_script, "script_pti_node_set_prev", reg0, ":index"),
			(assign, ":new_node", reg0),
			(call_script, "script_pti_array_append", ":list", ":new_node"),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_insert_after was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_append
	("pti_linked_list_append",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":value", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(try_begin),
				# If list is empty, create head node pointing to itself as both previous and next
				(party_slot_eq, ":list", pti_slot_array_size, 0),
				
				# The next and prev indexes are both 0, which doesn't need to be explicitly added (will be 0 by default)
				(call_script, "script_pti_array_append", ":list", ":value"),
			(else_try),
				# If list is not empty, insert a new node after the tail node
				(party_get_slot, ":head_index", ":list", pti_slot_list_head),
				(call_script, "script_pti_linked_list_get_node", ":list", ":head_index"),
				(call_script, "script_pti_linked_list_insert_after", ":list", reg2, ":value"),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_append was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_copy_node
	# WARNING: This will overwrite whatever exists at the new index, it is only intended for use in script_pti_linked_list_remove
	("pti_linked_list_copy_node",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":new_index", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			# Point the neighbours at the new index
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":next", reg1),
			(assign, ":prev", reg2),
			
			(call_script, "script_pti_linked_list_set_next", ":list", ":prev", ":new_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":next", ":new_index"),
			
			# Overwrite the new index
			(call_script, "script_pti_array_get", ":list", ":index"),
			(call_script, "script_pti_array_set", ":list", ":new_index", reg0),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_copy_node was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_swap
	("pti_linked_list_swap",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index_1", 2),
		(store_script_param, ":index_2", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index_1"),
			(assign, ":next_index_1", reg1),
			(assign, ":prev_index_1", reg2),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index_2"),
			(assign, ":next_index_2", reg1),
			(assign, ":prev_index_2", reg2),
			
			(try_begin),
				(eq, ":next_index_1", ":index_2"),
				
				(call_script, "script_pti_linked_list_swap_with_next", ":list", ":index_1"),
			(else_try),
				(eq, ":next_index_2", ":index_1"),
				
				(call_script, "script_pti_linked_list_swap_with_next", ":list", ":index_2"),
			(else_try),
				(call_script, "script_pti_linked_list_set_next", ":list", ":index_2", ":next_index_1"),
				(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index_1", ":index_2"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":index_2", ":prev_index_1"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index_1", ":index_2"),
				
				(call_script, "script_pti_linked_list_set_next", ":list", ":index_1", ":next_index_2"),
				(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index_2", ":index_1"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":index_1", ":prev_index_2"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index_2", ":index_1"),
				
				# If swapping the head node, set the other node as the new head node
				(try_begin),
					(party_slot_eq, ":list", pti_slot_list_head, ":index_1"),
					
					(party_set_slot, ":list", pti_slot_list_head, ":index_2"),
					#(assign, reg0, ":index_2"),
					#(display_message, "@Setting head to index {reg0}"),
				(else_try),
					(party_slot_eq, ":list", pti_slot_list_head, ":index_2"),
					
					(party_set_slot, ":list", pti_slot_list_head, ":index_1"),
					#(assign, reg0, ":index_1"),
					#(display_message, "@Setting head to index {reg0}"),
				(try_end),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_swap was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_swap_with_next
	("pti_linked_list_swap_with_next",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":next_index", reg1),
			(assign, ":prev_index", reg2),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":next_index"),
			(assign, ":last_index", reg1),
			
			(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index", ":next_index"),
			(call_script, "script_pti_linked_list_set_next", ":list", ":next_index", ":index"),
			(call_script, "script_pti_linked_list_set_next", ":list", ":index", ":last_index"),
			
			(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index", ":prev_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":index", ":next_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":last_index", ":index"),
			
			# If swapping the head node, set the other node as the new head node
			(try_begin),
				(party_slot_eq, ":list", pti_slot_list_head, ":index"),
				
				(party_set_slot, ":list", pti_slot_list_head, ":next_index"),
				#(assign, reg0, ":next_index"),
				#(display_message, "@Setting head to index {reg0}"),
			(else_try),
				(party_slot_eq, ":list", pti_slot_list_head, ":next_index"),
				
				(party_set_slot, ":list", pti_slot_list_head, ":index"),
				#(assign, reg0, ":index"),
				#(display_message, "@Setting head to index {reg0}"),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_swap_with_next was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_swap_with_prev
	("pti_linked_list_swap_with_prev",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":next_index", reg1),
			(assign, ":prev_index", reg2),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":prev_index"),
			(assign, ":first_index", reg2),
			
			(call_script, "script_pti_linked_list_set_next", ":list", ":first_index", ":index"),
			(call_script, "script_pti_linked_list_set_next", ":list", ":index", ":prev_index"),
			(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index", ":next_index"),
			
			(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index", ":prev_index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":prev_index", ":index"),
			(call_script, "script_pti_linked_list_set_prev", ":list", ":index", ":first_index"),
			
			# If swapping the head node, set the other node as the new head node
			(try_begin),
				(party_slot_eq, ":list", pti_slot_list_head, ":index"),
				
				(party_set_slot, ":list", pti_slot_list_head, ":prev_index"),
				#(assign, reg0, ":prev_index"),
				#(display_message, "@Setting head to index {reg0}"),
			(else_try),
				(party_slot_eq, ":list", pti_slot_list_head, ":prev_index"),
				
				(party_set_slot, ":list", pti_slot_list_head, ":index"),
				#(assign, reg0, ":index"),
				#(display_message, "@Setting head to index {reg0}"),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_swap_with_prev was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_move_before
	("pti_linked_list_move_before",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":dest_index", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(assign, ":next", reg1),
			(assign, ":prev", reg2),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":dest_index"),
			(assign, ":dest_prev", reg2),
			
			(try_begin),
				(eq, ":next", ":dest_index"),	# If already in place, do nothing
			(else_try),
				(eq, ":prev", ":dest_index"),	# If nodes are neighbours, do an adjacent swap
				
				(call_script, "script_pti_linked_list_swap_with_next", ":list", ":dest_index"),
			(else_try),
				# Connect the moved node's original neighbours together
				(call_script, "script_pti_linked_list_set_next", ":list", ":prev", ":next"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":next", ":prev"),
				
				# Connect the moved node to its new neighbours
				(call_script, "script_pti_linked_list_set_next", ":list", ":dest_prev", ":index"),
				(call_script, "script_pti_linked_list_set_next", ":list", ":index", ":dest_index"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":dest_index", ":index"),
				(call_script, "script_pti_linked_list_set_prev", ":list", ":index", ":dest_prev"),
				
				(try_begin),
					(party_slot_eq, ":list", pti_slot_list_head, ":dest_index"),
					
					(party_set_slot, ":list", pti_slot_list_head, ":index"),
					#(assign, reg0, ":index"),
					#(display_message, "@Setting head to index {reg0}"),
				(try_end),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_move_before was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_remove_index
	("pti_linked_list_remove_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
		# Connect the neighbour nodes together
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(assign, ":next", reg1),
		(assign, ":prev", reg2),
		
		(call_script, "script_pti_linked_list_set_next", ":list", ":prev", ":next"),
		(call_script, "script_pti_linked_list_set_prev", ":list", ":next", ":prev"),
		
		# Copy the node held in the last index into this index so that the last index in the array can be deleted in order to save space
		(party_get_slot, ":last_index", ":list", pti_slot_array_size),
		(val_sub, ":last_index", 1),
		(try_begin),
			(neq, ":last_index", ":index"),
			
			(call_script, "script_pti_linked_list_copy_node", ":list", ":last_index", ":index"),
		(try_end),
		
		# Delete the (now unused by the linked list) last index and decrement the size of the list
		(call_script, "script_pti_array_set", ":list", ":last_index", 0),
		(party_get_slot, ":size", ":list", pti_slot_array_size),
		(val_sub, ":size", 1),
		(party_set_slot, ":list", pti_slot_array_size, ":size"),
		
		# If the first element is being removed, set the head to point to the next element
		(try_begin),
			(party_slot_eq, ":list", pti_slot_list_head, ":index"),
			
			(party_set_slot, ":list", pti_slot_list_head, ":next"),
		(try_end),
	]),
	
	# script_pti_linked_list_remove_from_start_index
	("pti_linked_list_remove_from_start_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":object", 2),
		(store_script_param, ":start_index", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":head_index", ":list", pti_slot_list_head),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":start_index"),
			(assign, ":curr_obj", reg0),
			(assign, ":next", reg1),
			(assign, ":curr_index", reg3),
			
			(assign, ":index", -1),
			(party_get_slot, ":size", ":list", pti_slot_array_size),
			(try_for_range, ":unused", 0, ":size"),
				(eq, ":curr_obj", ":object"),
				
				(assign, ":index", ":curr_index"),
				(assign, ":size", 0),
			(else_try),
				(neq, ":next", ":head_index"),
				(neq, ":next", ":start_index"),
				
				(call_script, "script_pti_linked_list_get_node", ":list", ":next"),
				(assign, ":curr_obj", reg0),
				(assign, ":next", reg1),
				(assign, ":curr_index", reg3),
			(else_try),
				(assign, ":size", 0),
			(try_end),
			
			(try_begin),
				(gt, ":index", -1),
				
				(call_script, "script_pti_linked_list_remove_index", ":list", ":index"),
			(else_try),
				(assign, reg0, ":object"),
				(assign, reg1, ":list"),
				(display_log_message, "@ERROR: Tried to remove {reg0} from list (ID: {reg1}), but {reg0} could not be found in the list", 0xFF00000),
			(try_end),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_remove was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_remove
	("pti_linked_list_remove",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":object", 2),
		
		(party_get_slot, ":head_index", ":list", pti_slot_list_head),
		(call_script, "script_pti_linked_list_remove_from_start_index", ":list", ":object", ":head_index"),
	]),
	
	# script_pti_linked_list_get_nth_index
	("pti_linked_list_get_nth_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":n", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_head_node", ":list"),
			(try_for_range, ":unused", 0, ":n"),
				(call_script, "script_pti_linked_list_get_node", ":list", reg1),
			(try_end),
			
			(assign, reg0, reg3),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_get_nth_index was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_get_nth_index_after_index
	("pti_linked_list_get_nth_index_after_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":n", 2),
		(store_script_param, ":index", 3),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
			(try_for_range, ":unused", 0, ":n"),
				(call_script, "script_pti_linked_list_get_node", ":list", reg1),
			(try_end),
			
			(assign, reg0, reg3),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_get_nth_index_after_index was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_merge_halves
	("pti_linked_list_merge_halves",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":comparison_script", 2),
		(store_script_param, ":left", 3),
		(store_script_param, ":right", 4),
		
		(store_sub, ":diff", ":right", ":left"),
		(store_div, ":half_diff", ":diff", 2),
		
		(call_script, "script_pti_linked_list_get_nth_index", ":list", ":left"),
		(call_script, "script_pti_linked_list_get_node", ":list", reg0),
		(assign, ":left_value", reg0),
		(assign, ":left_next", reg1),
		(assign, ":left_index", reg3),
		(assign, ":left_curr", ":left"),
		
		#(assign, reg2, ":left"),
		#(assign, reg3, ":right"),
		#(str_store_string, s0, "@Merging from {reg2} to {reg3}:"),
		#(try_for_range, ":unused", 0, ":half_diff"),
		#	(str_store_string, s0, "@{s0} {reg0}"),
		#	(call_script, "script_pti_linked_list_get_node", ":list", reg1),
		#(try_end),
		#(str_store_string, s0, "@{s0} |"),
		#(try_for_range, ":unused", ":half_diff", ":diff"),
		#	(str_store_string, s0, "@{s0} {reg0}"),
		#	(call_script, "script_pti_linked_list_get_node", ":list", reg1),
		#(try_end),
		#(display_message, s0),
		
		(store_add, ":left_end", ":left", ":half_diff"),
		
		(call_script, "script_pti_linked_list_get_nth_index_after_index", ":list", ":half_diff", ":left_index"),
		(call_script, "script_pti_linked_list_get_node", ":list", reg0),
		(assign, ":right_value", reg0),
		(assign, ":right_next", reg1),
		(assign, ":right_index", reg3),
		(store_add, ":right_curr", ":left", ":half_diff"),
		
		(assign, ":end_cond", ":diff"),
		(try_for_range, ":unused", 0, ":end_cond"),
			(this_or_next|eq, ":right_curr", ":right"),
			(eq, ":left_curr", ":left_end"),
			
			#(assign, reg0, ":left_curr"),
			#(assign, reg1, ":left_end"),
			#(assign, reg2, ":right_curr"),
			#(assign, reg3, ":right"),
			#(display_message, "@{reg0} = {reg1} or {reg2} = {reg3}"),
			
			(assign, ":end_cond", 0),
		(else_try),
			(lt, ":right_curr", ":right"),
			(call_script, ":comparison_script", ":left_value", ":right_value"),
			
			#(assign, reg0, ":right_value"),
			#(assign, reg1, ":left_value"),
			#(display_message, "@Selecting {reg0} from {reg1} and {reg0}"),
			
			(call_script, "script_pti_linked_list_move_before", ":list", ":right_index", ":left_index"),
			
			#(call_script, "script_pti_linked_list_get_node", ":list", ":right_index"),
			#(assign, ":left_value", reg0),
			#(assign, ":left_next", reg1),
			#(assign, ":left_index", reg3),
			#(val_add, ":left_end", 1),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":right_next"),
			(assign, ":right_value", reg0),
			(assign, ":right_next", reg1),
			(assign, ":right_index", reg3),
			(val_add, ":right_curr", 1),
		(else_try),
			#(assign, reg0, ":left_value"),
			#(assign, reg1, ":right_value"),
			#(display_message, "@Selecting {reg0} from {reg0} and {reg1}"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", ":left_next"),
			(assign, ":left_value", reg0),
			(assign, ":left_next", reg1),
			(assign, ":left_index", reg3),
			(val_add, ":left_curr", 1),
		(try_end),
		
		#(assign, reg0, ":left"),
		#(assign, reg1, ":right"),
		#(display_message, "@Done merging from {reg0} to {reg1}"),
	]),
	
	# script_pti_linked_list_merge_sort_r
	("pti_linked_list_merge_sort_r",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":comparison_script", 2),
		(store_script_param, ":left", 3),
		(store_script_param, ":right", 4),
		
		#(assign, reg0, ":left"),
		#(assign, reg1, ":right"),
		#(display_message, "@Sorting from {reg0} to {reg1}"),
		
		(store_sub, ":diff", ":right", ":left"),
		(try_begin),
			(gt, ":diff", 1),
			
			(store_div, ":mid", ":diff", 2),
			(val_add, ":mid", ":left"),
			(call_script, "script_pti_linked_list_merge_sort_r", ":list", ":comparison_script", ":left", ":mid"),
			(call_script, "script_pti_linked_list_merge_sort_r", ":list", ":comparison_script", ":mid", ":right"),
			(call_script, "script_pti_linked_list_merge_halves", ":list", ":comparison_script", ":left", ":right"),
		(else_try),
			(eq, ":diff", 1),
			
			(call_script, "script_pti_linked_list_get_nth_index", ":list", ":left"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, ":left_value", reg0),
			(assign, ":left_index", reg3),
			(call_script, "script_pti_linked_list_get_node", ":list", reg1),
			(assign, ":right_value", reg0),
			
			(call_script, ":comparison_script", ":left_value", ":right_value"),
			
			#(assign, reg0, ":left_value"),
			#(assign, reg1, ":right_value"),
			#(store_sub, reg2, ":comparison_script", "script_game_start"),
			#(display_message, "@Swapping {reg0} and {reg1} according to script no. {reg2}"),
			(call_script, "script_pti_linked_list_swap_with_next", ":list", ":left_index"),
		(try_end),
		
		#(assign, reg0, ":left"),
		#(assign, reg1, ":right"),
		#(display_message, "@Done sorting from {reg0} to {reg1}"),
	]),
	
	# script_pti_linked_list_merge_sort
	("pti_linked_list_merge_sort",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":comparison_script", 2),
		
		(try_begin),
			(party_get_template_id, ":template", ":list"),
			(eq, ":template", "pt_array"),
			
			(party_get_slot, ":size", ":list", pti_slot_array_size),
			(val_sub, ":size", 1),
			(call_script, "script_pti_linked_list_merge_sort_r", ":list", ":comparison_script", 0, ":size"),
		(else_try),
			(assign, reg0, ":list"),
			(display_log_message, "@ERROR: script_pti_linked_list_merge_sort was called without a valid list being passed (party ID: {reg0})", 0xFF0000),
		(try_end),
	]),
	
	# script_pti_linked_list_get_troop_sub_list_head
	("pti_linked_list_get_troop_sub_list_head",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":troop_id", 2),
		
		(assign, ":sub_list_head", -1),
		
		(party_get_num_companion_stacks, ":num_stacks", ":list"),
		(call_script, "script_pti_linked_list_get_head_node", ":list"),
		(assign, ":next_index", reg1),
		
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":stack_troop_id", ":list", ":stack"),
			(eq, ":stack_troop_id", ":troop_id"),
			
			(assign, ":sub_list_head", reg0),
			(assign, ":num_stacks", 0),
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", ":next_index"),
			(assign, ":next_index", reg1),
		(try_end),
		
		(assign, reg0, ":sub_list_head"),
	]),
	
	# script_pti_linked_list_add_troop_sub_list
	("pti_linked_list_add_troop_sub_list",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":value", 3),
		
		# Construct a new node that will point forwards and backwards to itself, creating essentially a new linked list within the linked list
		(party_get_slot, ":sub_list_head", ":list", pti_slot_array_size),
		(val_add, ":sub_list_head", 1),
		
		(assign, reg0, ":value"),
		(call_script, "script_pti_node_set_prev", reg0, ":sub_list_head"),
		(call_script, "script_pti_node_set_next", reg0, ":sub_list_head"),
		(assign, ":new_node", reg0),
		
		# To the actual linked list, append a node that points to the new sub-list to be created
		(call_script, "script_pti_linked_list_append", ":list", ":sub_list_head"),
		
		# Append the sub-list
		(call_script, "script_pti_array_append", ":list", ":new_node"),
		
		# Add a new troop stack to the list's party. These troop stacks will be used to know the size of the overall linked list and each sub list via stack sizes, rather than the singular pti_slot_array_size, which gives little information for a 2D list.
		(party_add_members, ":list", ":troop_id", 1),
		
		(assign, reg0, ":sub_list_head"),
	]),
	
	# script_pti_linked_list_append_to_sub_list
	("pti_linked_list_append_to_sub_list",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":sub_list_head", 2),
		(store_script_param, ":value", 3),
		
		(call_script, "script_pti_linked_list_insert_before", ":list", ":sub_list_head", ":value", 0),
	]),
	
	# script_cf_pti_gt
	("cf_pti_gt",
	[
		(store_script_param, ":value_1", 1),
		(store_script_param, ":value_2", 2),
		
		(gt, ":value_1", ":value_2"),
	]),
	
	## INDIVIDUAL CREATION AND ADDITION TO PARTY SCRIPTS
	
	# script_pti_create_individual
	# This script doesn't actually produce any data, it just returns a free array index that can be used
	# These array indexes point to a particular space in one big global array where data can be put and later retrieved (Individual.get and Individual.set)
	# The space allocated could be at the end of the array if it is full, or it could be space previously allocated to an individual that has been killed
	# "$pti_individuals_array_next_free_index" gets updated to the latter in script_pti_kill_individual_in_party
	("pti_create_individual",
	[
		# Update the size of the individuals array if a new individual must be added at the end
		(party_get_slot, ":size", "$pti_individuals_array", pti_slot_array_size),
		(try_begin),
			(ge, "$pti_individuals_array_next_free_index", ":size"),
			
			(val_add, ":size", Individual.num_attribute_slots),
			(party_set_slot, "$pti_individuals_array", pti_slot_array_size, ":size"),
		(try_end),
		
		# Get the index to be returned that points to free space to fill with the new individual's data
		(assign, ":individual", "$pti_individuals_array_next_free_index"),
		
		# Find the next free index that can be used for future individual creation
		# By default update to the end of the array, but then search for an earlier free space between the previous one and the end
		(assign, "$pti_individuals_array_next_free_index", ":size"),
		
		(store_add, ":next_slots_start", "$pti_individuals_array_next_free_index", Individual.num_attribute_slots),
		(store_sub, ":end_cond", ":size", ":next_slots_start"),
		(val_div, ":end_cond", Individual.num_attribute_slots),
		(try_for_range, ":individual_offset", 0, ":end_cond"),
			# To see if a space is free, check if all slots in it have values of 0
			(assign, ":is_empty", 1),
			(assign, ":inner_end_cond", Individual.num_attribute_slots),
			(try_for_range, ":slot_offset", 0, ":inner_end_cond"),
				(store_mul, ":total_offset", ":individual_offset", Individual.num_attribute_slots),
				(val_add, ":total_offset", ":slot_offset"),
				(store_add, ":index", ":next_slots_start", ":total_offset"),
				(call_script, "script_pti_array_get", "$pti_individuals_array", ":index"),
				(neq, reg0, 0),
				
				(assign, ":inner_end_cond", 0),
				(assign, ":is_empty", 0),
			(try_end),
			
			(eq, ":is_empty", 1),
			
			(assign, ":end_cond", 0),
			(store_mul, "$pti_individuals_array_next_free_index", ":individual_offset", Individual.num_attribute_slots),
			(val_add, "$pti_individuals_array_next_free_index", ":next_slots_start"),
		(try_end),
		
		# Return the free space that was available for this individual
		(assign, reg0, ":individual"),
	]),
	
	# script_pti_create_individual_of_type
	("pti_create_individual_of_type",
	[
		(store_script_param, ":troop_id", 1),
		
		(call_script, "script_pti_create_individual"),
		(assign, ":individual", reg0),
		
		Individual.set(":individual", "troop_type", ":troop_id"),
		
		(call_script, "script_pti_individual_generate_base_equipment", ":individual"),
		(call_script, "script_pti_individual_generate_face_keys", ":individual"),
		
		(call_script, "script_pti_troop_get_name_range", ":troop_id"),
		(assign, ":names_begin", reg0),
		(assign, ":names_end", reg1),
		
		(store_random_in_range, ":name", ":names_begin", ":names_end"),
		(val_sub, ":name", ":names_begin"),
		Individual.set(":individual", "name", ":name"),
		
		(store_current_day, ":curr_day"),
		Individual.set(":individual", "day_joined", ":curr_day"),
		
		(call_script, "script_pti_xp_needed_to_upgrade_to", ":troop_id"),
		Individual.set(":individual", "xp", reg0),
		
		(assign, reg0, ":individual"),
	]),
	
	# script_pti_party_add_individual
	("pti_party_add_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":individual", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(try_begin),
			(party_count_members_of_type, ":num_troops", ":list", ":troop_id"),
			(eq, ":num_troops", 0),
			
			(call_script, "script_pti_linked_list_add_troop_sub_list", ":list", ":troop_id", ":individual"),
		(else_try),
			(call_script, "script_pti_linked_list_get_troop_sub_list_head", ":list", ":troop_id"),
			(call_script, "script_pti_linked_list_append_to_sub_list", ":list", reg0, ":individual"),
			(party_add_members, ":list", ":troop_id", 1),
		(try_end),
		
		(party_add_members, ":party", ":troop_id", 1),
	]),
	
	# script_pti_recruit_troops_from_center
	("pti_recruit_troops_from_center",
	[
		(store_script_param, ":dest_party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":center", 3),
		(store_script_param, ":number", 4),
		
		(try_for_range, ":unused", 0, ":number"),
			(call_script, "script_pti_create_individual_of_type", ":troop_id"),
			(assign, ":individual", reg0),
			Individual.set(":individual", "home", ":center"),
			(call_script, "script_pti_party_add_individual", ":dest_party", ":individual"),
		(try_end),
	]),
	
	# script_pti_recruit_prisoners
	("pti_recruit_prisoners",
	[
		(store_script_param, ":dest_party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":number", 3),
		
		# Get the faction of the troop in order to randomly pick a home fief
		# If not a kingdom troop, just go by current location
		(store_faction_of_troop, ":faction", ":troop_id"),
		(try_begin),
			(neg|is_between, ":faction", npc_kingdoms_begin, npc_kingdoms_end),
			
			(assign, ":minimum_distance", 1000000),
			(try_for_range, ":center", centers_begin, centers_end),
				(store_distance_to_party_from_party, ":dist", ":dest_party", ":center"),
				(try_begin),
					(lt, ":dist", ":minimum_distance"),
					
					(assign, ":minimum_distance", ":dist"),
					(assign, ":nearest_center", ":center"),
				(try_end),
			(try_end),
			
			(store_faction_of_party, ":faction", ":nearest_center"),
		(try_end),
		
		(try_for_range, ":unused", 0, ":number"),
			(call_script, "script_cf_select_random_village_with_faction", ":faction"),
			(assign, ":center", reg0),
			
			(call_script, "script_pti_create_individual_of_type", ":troop_id"),
			(assign, ":individual", reg0),
			Individual.set(":individual", "home", ":center"),
			Individual.set(":individual", "is_recent_prisoner", 1),
			(call_script, "script_pti_party_add_individual", ":dest_party", ":individual"),
		(try_end),
	]),
	
	# script_pti_get_random_village_associated_with_lord
	("pti_get_random_village_associated_with_lord",
	[
		(store_script_param, ":lord", 1),
		
		# Count fiefs the lord owns
		(assign, ":num_centers", 0),
		(try_for_range, ":center", centers_begin, centers_end),
			(party_slot_eq, ":center", slot_town_lord, ":lord"),
			
			(val_add, ":num_centers", 1),
		(try_end),
		
		(try_begin),
			# If the lord owns at least one fief, choose randomly from those fiefs
			(gt, ":num_centers", 0),
			
			(store_random_in_range, ":rand", 0, ":num_centers"),
			
			(assign, ":end_cond", centers_end),
			(assign, ":center_number", 0),
			(try_for_range, ":center", centers_begin, ":end_cond"),
				(party_slot_eq, ":center", slot_town_lord, ":lord"),
				
				(try_begin),
					(eq, ":center_number", ":rand"),
					
					(assign, ":chosen_center", ":center"),
					(assign, ":end_cond", 0),	# End loop
				(else_try),
					(val_add, ":center_number", 1),
				(try_end),
			(try_end),
			
			# If the chosen fief is not a village, choose randomly from its surrounding villages
			(neg|party_slot_eq, ":chosen_center", slot_party_type, spt_village),
			
			# Count surrounding villages of the chosen center
			(assign, ":num_villages", 0),
			(try_for_range, ":village", villages_begin, villages_end),
				(party_slot_eq, ":village", slot_village_bound_center, ":chosen_center"),
				
				(val_add, ":num_villages", 1),
			(try_end),
			
			(store_random_in_range, ":rand", 0, ":num_villages"),
			
			(assign, ":end_cond", villages_end),
			(assign, ":village_number", 0),
			(try_for_range,":village", villages_begin, ":end_cond"),
				(party_slot_eq, ":village", slot_village_bound_center, ":chosen_center"),
				
				(try_begin),
					(eq, ":village_number", ":rand"),
					
					(assign, ":chosen_center", ":village"),
					(assign, ":end_cond", 0),	# End loop
				(else_try),
					(val_add, ":village_number", 1),
				(try_end),
			(try_end),
		(else_try),
			# If the lord owns no fiefs, choose randomly from villages of his faction
			(store_faction_of_troop, ":faction", ":lord"),
			(call_script, "script_cf_select_random_village_with_faction", ":faction"),
		(else_try),
			# If the faction has no villages, randomly choose one of the lord's culture
			(faction_get_slot, ":culture", ":faction", slot_faction_culture),
			
			(assign, ":num_villages", 0),
			(try_for_range, ":village", villages_begin, villages_end),
				(party_slot_eq, ":village", slot_center_culture, ":culture"),
				
				(val_add, ":num_villages", 1),
			(try_end),
			
			(store_random_in_range, ":rand", 0, ":num_villages"),
			
			(assign, ":end_cond", villages_end),
			(assign, ":village_number", 0),
			(try_for_range,":village", villages_begin, ":end_cond"),
				(party_slot_eq, ":village", slot_center_culture, ":culture"),
				
				(try_begin),
					(eq, ":village_number", ":rand"),
					
					(assign, ":chosen_center", ":village"),
					(assign, ":end_cond", 0),	# End loop
				(else_try),
					(val_add, ":village_number", 1),
				(try_end),
			(try_end),
		(else_try),
			# If there were no villages of the lord's culture then lol what the fuck is going on? Just choose any random village at this point
			(store_random_in_range, ":chosen_center", villages_begin, villages_end),
		(try_end),
		
		(assign, reg0, ":chosen_center"),
	]),
	
	# script_pti_collect_troops_from_train_troop_quest
	("pti_collect_troops_from_train_troop_quest",
	[
		(store_script_param, ":dest_party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":lord", 3),
		(store_script_param, ":number", 4),
		
		(try_for_range, ":unused", 0, ":number"),
			(call_script, "script_pti_create_individual_of_type", ":troop_id"),
			(assign, ":individual", reg0),
			
			(call_script, "script_pti_get_random_village_associated_with_lord", ":lord"),
			Individual.set(":individual", "home", reg0),
			Individual.set(":individual", "train_troops_quest", 1),
			
			(call_script, "script_pti_party_add_individual", ":dest_party", ":individual"),
		(try_end),
	]),
	
	# script_pti_party_create_individuals_from_members
	("pti_party_create_individuals_from_members",
	[
		(store_script_param, ":party", 1),
		
		(try_begin),
			(party_slot_eq, ":party", pti_slot_party_individuals, 0),
			
			(str_store_party_name, s0, ":party"),
			(call_script, "script_pti_linked_list_init"),
			(party_set_slot, ":party", pti_slot_party_individuals, reg0),
			(party_set_name, reg0, "@{s0} Party Individuals Array - You should not be seeing this"),
		(try_end),
		
		(party_get_num_companion_stacks, ":num_stacks", ":party"),
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":troop_id", ":party", ":stack"),
			(party_stack_get_size, ":size", ":party", ":stack"),
			(store_faction_of_troop, ":faction", ":troop_id"),
			
			(try_for_range, ":unused", 0, ":size"),
				(try_begin),
					(is_between, ":faction", npc_kingdoms_begin, npc_kingdoms_end),
					(call_script, "script_cf_select_random_village_with_faction", ":faction"),
					(assign, ":center", reg0),
				(else_try),
					(store_random_in_range, ":center", villages_begin, villages_end),
				(try_end),
				
				(call_script, "script_pti_create_individual_of_type", ":troop_id"),
				(assign, ":individual", reg0),
				Individual.set(":individual", "home", ":center"),
				(call_script, "script_pti_party_add_individual", ":party", ":individual"),
			(try_end),
		(try_end),
	]),
	
	## INDIVIDUAL ATTRIBUTE GETTING AND SETTING
	
	# script_pti_individual_get_attribute
	# Should only be called from the method Individual.get(individual, attribute) in pti_constants
	# Given the relevant data transformation values from that method, this script returns the value of an attribute for an individual
	("pti_individual_get_attribute",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":offset", 2),
		(store_script_param, ":bitshift", 3),
		(store_script_param, ":bitmask", 4),
		
		(val_add, ":individual", ":offset"),
		(call_script, "script_pti_array_get", "$pti_individuals_array", ":individual"),
		(val_rshift, reg0, ":bitshift"),
		(val_and, reg0, ":bitmask"),
	]),
	
	# script_pti_individual_set_attribute
	# Should only be called from the method Individual.get(individual, attribute) in pti_constants
	# Given the relevant data transformation values from that method, this script sets the value of an attribute for an individual
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
			
			(val_lshift, ":value", ":bitshift"),
			
			(val_add, ":individual", ":offset"),
			(call_script, "script_pti_array_get", "$pti_individuals_array", ":individual"),
			(val_and, reg0, ":clear_mask"),
			(val_or, reg0, ":value"),
			(call_script, "script_pti_array_set", "$pti_individuals_array", ":individual", reg0),
		(else_try),
			(assign, reg0, ":value"),
			(assign, reg1, ":bitmask"),
			(display_log_message, "@ERROR: Tried to add value of {reg0} to attribute for which the maximum value is {reg1}", 0xFF00000),
		(try_end),
	]),
	
	## INDIVIDUAL ITERATION AND COUNTING SCRIPTS
	
	# script_pti_get_next_individual_with_troop_id
	("pti_get_next_individual_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":condition", 3),
		
		(assign, "$pti_current_individual", -1),
		(assign, "$pti_curr_individual_index", "$pti_next_individual_index"),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		
		(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
		(assign, ":sub_list_head", reg0),
		
		(party_count_members_of_type, ":count", ":list", ":troop_id"),
		(try_for_range, ":unused", 0, ":count"),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_individual_index"),
			#(display_message, "@Got individual {reg0} from index {reg3}"),
			(assign, ":individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
			
			(call_script, ":condition", ":individual"),
			
			(assign, "$pti_current_individual", ":individual"),
			(assign, ":count", 0),
		(else_try),
			(neq, "$pti_next_individual_index", ":sub_list_head"),
			
			(assign, "$pti_curr_individual_index", "$pti_next_individual_index"),
		(else_try),
			(assign, ":count", 0),
		(try_end),
		
		# For output, set reg0 to indicate whether or not the end of the stack was reached (useful for script_pti_get_next_individual)
		(try_begin),
			(eq, "$pti_next_individual_index", ":sub_list_head"),
			
			(assign, reg0, 1),
		(else_try),
			(assign, reg0, 0),
		(try_end),
	]),
	
	# script_pti_get_next_individual
	("pti_get_next_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_num_companion_stacks, ":num_stacks", ":list"),
		
		(try_for_range, ":stack", "$pti_curr_troop_stack", ":num_stacks"),
			(assign, "$pti_curr_troop_stack", ":stack"),
			(party_stack_get_troop_id, ":troop_id", ":list", ":stack"),
			(call_script, "script_pti_get_next_individual_with_troop_id", ":party", ":troop_id", ":condition"),
			
			(gt, "$pti_current_individual", -1),
			
			(assign, ":num_stacks", 0),
			(eq, reg0, 0),	# Trigger the else block if the end of the stack was reached so that the next call of script_pti_get_next_individual starts from the next troop stack
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_curr_troop_index", reg1),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_next_individual_index", reg0),
			(val_add, "$pti_curr_troop_stack", 1),
		(try_end),
		
		# If no individual found, set all the global variables to -1
		(try_begin),
			(eq, "$pti_current_individual", -1),
			
			(assign, "$pti_curr_individual_index", -1),
			(assign, "$pti_next_individual_index", -1),
			(assign, "$pti_prev_individual_index", -1),
			(assign, "$pti_curr_troop_index", -1),
		(try_end),
	]),
	
	# script_pti_get_first_individual_with_troop_id
	("pti_get_first_individual_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":condition", 3),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_num_companion_stacks, ":num_stacks", ":list"),
		
		(party_get_slot, "$pti_curr_troop_index", ":list", pti_slot_list_head),
		
		# Find the sub-list for the given troop id
		(assign, ":troop_found", 0),
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":stack_troop_id", ":list", ":stack"),
			(eq, ":stack_troop_id", ":troop_id"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_next_individual_index", reg0),
			(assign, "$pti_curr_troop_stack", ":stack"),
			
			(assign, ":num_stacks", 0),
			(assign, ":troop_found", 1),
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_curr_troop_index", reg1),
		(try_end),
		
		# If sub-list found, get the first individual, otherwise set all global variables to -1
		(try_begin),
			(eq, ":troop_found", 1),
			
			(call_script, "script_pti_get_next_individual_with_troop_id", ":party", ":troop_id", ":condition"),
		(else_try),
			(assign, "$pti_current_individual", -1),
			(assign, "$pti_curr_individual_index", -1),
			(assign, "$pti_next_individual_index", -1),
			(assign, "$pti_prev_individual_index", -1),
			(assign, "$pti_curr_troop_index", -1),
		(try_end),
	]),
	
	# script_pti_get_first_individual
	("pti_get_first_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		
		(call_script, "script_pti_linked_list_get_head_node", ":list"),
		(assign, "$pti_curr_troop_index", reg3),
		(assign, "$pti_next_individual_index", reg0),
		(assign, "$pti_curr_troop_stack", 0),
		
		(call_script, "script_pti_get_next_individual", ":party", ":condition"),
	]),
	
	# script_pti_get_prev_individual_with_troop_id
	("pti_get_prev_individual_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":condition", 3),
		
		(assign, "$pti_current_individual", -1),
		(assign, "$pti_curr_individual_index", "$pti_prev_individual_index"),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		
		(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
		(assign, ":sub_list_head", reg0),
		
		(party_count_members_of_type, ":count", ":list", ":troop_id"),
		(try_for_range, ":unused", 0, ":count"),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_individual_index"),
			(assign, ":individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
			
			(call_script, ":condition", ":individual"),
			
			(assign, "$pti_current_individual", ":individual"),
			(assign, ":count", 0),
		(else_try),
			(neq, "$pti_curr_individual_index", ":sub_list_head"),
			
			(assign, "$pti_curr_individual_index", "$pti_prev_individual_index"),
		(else_try),
			(assign, ":count", 0),
		(try_end),
	]),
	
	# script_pti_get_prev_individual
	("pti_get_prev_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_num_companion_stacks, ":num_stacks", ":list"),
		
		(assign, ":stacks_begin", 0),
		(store_add, ":stacks_end", "$pti_curr_troop_stack", 1),
		(try_for_range_backwards, ":stack", ":stacks_begin", ":stacks_end"),
			(assign, "$pti_curr_troop_stack", ":stack"),
			(party_stack_get_troop_id, ":troop_id", ":list", ":stack"),
			(call_script, "script_pti_get_prev_individual_with_troop_id", ":party", ":troop_id", ":condition"),
			
			(gt, "$pti_current_individual", -1),
			
			(assign, ":stacks_begin", ":num_stacks"),
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_curr_troop_index"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_prev_individual_index", reg2),
		(try_end),
		
		# If no individual found, set all the global variables to -1
		(try_begin),
			(eq, "$pti_current_individual", -1),
			
			(assign, "$pti_curr_individual_index", -1),
			(assign, "$pti_next_individual_index", -1),
			(assign, "$pti_prev_individual_index", -1),
			(assign, "$pti_curr_troop_index", -1),
		(try_end),
	]),
	
	# script_pti_get_last_individual_with_troop_id
	("pti_get_last_individual_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":condition", 3),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_num_companion_stacks, ":num_stacks", ":list"),
		
		(call_script, "script_pti_linked_list_get_tail_node", ":list"),
		(assign, "$pti_curr_troop_index", reg0),
		
		# Find the sub-list for the given troop id
		(assign, ":troop_found", 0),
		(try_for_range_backwards, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":stack_troop_id", ":list", ":stack"),
			(eq, ":stack_troop_id", ":troop_id"),
			
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_prev_individual_index", reg2),
			(assign, "$pti_curr_troop_stack", ":stack"),
			
			(assign, ":num_stacks", 0),
			(assign, ":troop_found", 1),
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
			(assign, "$pti_curr_troop_index", reg2),
		(try_end),
		
		# If sub-list found, get the last individual, otherwise set all global variables to -1
		(try_begin),
			(eq, ":troop_found", 1),
			
			(call_script, "script_pti_get_prev_individual_with_troop_id", ":party", ":troop_id", ":condition"),
		(else_try),
			(assign, "$pti_current_individual", -1),
			(assign, "$pti_curr_individual_index", -1),
			(assign, "$pti_next_individual_index", -1),
			(assign, "$pti_prev_individual_index", -1),
			(assign, "$pti_curr_troop_index", -1),
		(try_end),
	]),
	
	# script_pti_get_last_individual
	("pti_get_last_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		
		(call_script, "script_pti_linked_list_get_tail_node", ":list"),
		(assign, "$pti_curr_troop_index", reg0),
		(call_script, "script_pti_linked_list_get_node", ":list", "$pti_curr_troop_index"),
		(call_script, "script_pti_linked_list_get_node", ":list", 0),
		(assign, "$pti_prev_individual_index", reg2),
		(assign, "$pti_curr_troop_stack", 0),
		
		(call_script, "script_pti_get_prev_individual", ":party", ":condition"),
	]),
	
	# script_pti_count_individuals_with_troop_id
	("pti_count_individuals_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":troop_id", 2),
		(store_script_param, ":condition_script", 3),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_count_members_of_type, ":num_troops", ":list", ":troop_id"),
		
		(try_begin),
			(eq, ":condition_script", "script_cf_pti_true"),
			
			(assign, reg0, ":num_troops"),
		(else_try),
			(assign, ":count", 0),
			
			pti_get_first_individual(":party", ":troop_id", ":condition_script"),
			(assign, ":first_individual", "$pti_current_individual"),
			(try_for_range, ":unused", 0, ":num_troops"),
				(gt, "$pti_current_individual", -1),
				
				(val_add, ":count", 1),
				
				pti_get_next_individual(":party", ":troop_id", ":condition_script"),
				(neq, "$pti_current_individual", ":first_individual"),
			(else_try),
				(assign, ":num_troops", 0),
			(try_end),
			
			(assign, reg0, ":count"),
		(try_end),
	]),
	
	# script_pti_count_individuals
	("pti_count_individuals",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_num_companions, ":num_troops", ":list"),
		
		(try_begin),
			(eq, ":condition_script", "script_cf_pti_true"),
			
			(assign, reg0, ":num_troops"),
		(else_try),
			(assign, ":count", 0),
			
			pti_get_first_individual(party = ":party", condition = ":condition_script"),
			(assign, ":first_individual", "$pti_current_individual"),
			(try_for_range, ":unused", 0, ":num_troops"),
				(gt, "$pti_current_individual", -1),
				
				(val_add, ":count", 1),
				pti_get_next_individual(party = ":party", condition = ":condition_script"),
				
				(neq, "$pti_current_individual", ":first_individual"),
			(else_try),
				(assign, ":num_troops", 0),
			(try_end),
			
			(assign, reg0, ":count"),
		(try_end),
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
	
	# script_cf_pti_individual_can_upgrade_to
	("cf_pti_individual_can_upgrade_to",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":troop_id", 2),
		
		(call_script, "script_pti_xp_needed_to_upgrade_to", ":troop_id"),
		(assign, ":upgrade_xp", reg0),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(store_character_level, ":next_level", ":troop_id"),
		(val_add, ":next_level", 1),
		(call_script, "script_pti_xp_needed_to_reach_level", ":next_level"),
		(val_max, ":upgrade_xp", reg0),
		
		Individual.get(":individual", "xp"),
		(ge, reg0, ":upgrade_xp"),
	]),
	
	# script_cf_pti_individual_is_upgradeable
	("cf_pti_individual_is_upgradeable",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(assign, ":upgradeable", 0),
		(try_begin),
			(troop_get_upgrade_troop, ":upgrade", ":troop_id", 0),
			(gt, ":upgrade", 0),
			
			(try_begin),
				(call_script, "script_cf_pti_individual_can_upgrade_to", ":individual", ":upgrade"),
				
				(assign, ":upgradeable", 1),
			(else_try),
				(troop_get_upgrade_troop, ":upgrade", ":troop_id", 1),
				(gt, ":upgrade", 0),
				
				(call_script, "script_cf_pti_individual_can_upgrade_to", ":individual", ":upgrade"),
				
				(assign, ":upgradeable", 1),
			(try_end),
		(try_end),
		
		(eq, ":upgradeable", 1),
	]),
	
	# script_cf_pti_individual_is_wounded
	("cf_pti_individual_is_wounded",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_wounded"),
		(eq, reg0, 1),
	]),
	
	# script_cf_pti_individual_is_nonwounded
	("cf_pti_individual_is_nonwounded",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_wounded"),
		(eq, reg0, 0),
	]),
	
	# script_cf_pti_individual_is_not_wounded
	("cf_pti_individual_is_not_wounded",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_wounded"),
		(eq, reg0, 0),
	]),
	
	# script_cf_pti_individual_is_recent_prisoner
	("cf_pti_individual_is_recent_prisoner",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_recent_prisoner"),
		(eq, reg0, 1),
	]),
	
	# script_cf_pti_individual_is_marked_for_killing
	("cf_pti_individual_is_marked_for_killing",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "marked_for_kill"),
		(eq, reg0, 1),
	]),
	
	# script_cf_pti_individual_is_from_train_troops_quest
	("cf_pti_individual_is_from_train_troops_quest",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "train_troops_quest"),
		(eq, reg0, 1),
	]),
	
	# script_cf_pti_individual_xp_lt
	("cf_pti_individual_xp_lt",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "xp"),
		(lt, reg0, "$pti_comparison_xp"),
	]),
	
	## INDIVIDUAL FACE SCRIPTS
	
	# script_pti_individual_generate_face_keys
	("pti_individual_generate_face_keys",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(str_store_troop_face_keys, s0, ":troop_id", 0),
		(str_store_troop_face_keys, s1, ":troop_id", 1),
		
		(str_store_troop_face_keys, s2, "trp_temp_troop"),
		
		(face_keys_get_hair, ":hair_begin", s0),
		(face_keys_get_hair, ":hair_end", s1),
		(store_random_in_range, ":hair", ":hair_begin", ":hair_end"),
		Individual.set(":individual", "hair", ":hair"),
		
		(face_keys_get_beard, ":beard_begin", s0),
		(face_keys_get_beard, ":beard_end", s1),
		(store_random_in_range, ":beard", ":beard_begin", ":beard_end"),
		Individual.set(":individual", "beard", ":beard"),
		
		(face_keys_get_face_texture, ":face_texture_begin", s0),
		(face_keys_get_face_texture, ":face_texture_end", s1),
		(store_random_in_range, ":face_texture", ":face_texture_begin", ":face_texture_end"),
		Individual.set(":individual", "face_texture", ":face_texture"),
		
		(face_keys_get_hair_texture, ":hair_texture_begin", s0),
		(face_keys_get_hair_texture, ":hair_texture_end", s1),
		(store_random_in_range, ":hair_texture", ":hair_texture_begin", ":hair_texture_end"),
		Individual.set(":individual", "hair_texture", ":hair_texture"),
		
		(face_keys_get_hair_color, ":hair_color_begin", s0),
		(face_keys_get_hair_color, ":hair_color_end", s1),
		(store_random_in_range, ":hair_color", ":hair_color_begin", ":hair_color_end"),
		Individual.set(":individual", "hair_colour", ":hair_color"),
		
		## Getting age range from a recruit will always result in young troops that stay young throughout the entire game, might as well get full range of ages
		## TODO: UPDATE FROM UNIFORM DISTRIBUTION (I think older version of PTI uses gamma?)
		#(face_keys_get_age, ":age_begin", s0),
		#(face_keys_get_age, ":age_end", s1),
		#(store_random_in_range, ":age", ":age_begin", ":age_end"),
		(store_random_in_range, ":age", 0, 48),
		Individual.set(":individual", "age", ":age"),
		
		## These operations apparently don't work anyway
		#(face_keys_get_skin_color, ":skin_color_begin", s0),
		#(face_keys_get_skin_color, ":skin_color_end", s1),
		#(store_random_in_range, ":skin_color", ":skin_color_begin", ":skin_color_end"),
		#(face_keys_set_skin_color, s2, ":skin_color"),
	]),
	
	# script_pti_individual_get_face_keys
	("pti_individual_get_face_keys",
	[
		(store_script_param, ":individual", 1),
		
		# Start with average face keys (all dummy troops made in pti_troops have totally average faces as opposed to the usual down syndrome you'd see on troops with each set of face keys given as 0)
		(str_store_troop_face_keys, s0, "trp_pti_load_check"),
		
		Individual.get(":individual", "hair"),
		(face_keys_set_hair, s0, reg0),
		
		Individual.get(":individual", "beard"),
		(face_keys_set_beard, s0, reg0),
		
		Individual.get(":individual", "face_texture"),
		(face_keys_set_face_texture, s0, reg0),
		
		Individual.get(":individual", "hair_texture"),
		(face_keys_set_hair_texture, s0, reg0),
		
		Individual.get(":individual", "hair_colour"),
		(face_keys_set_hair_color, s0, reg0),
		
		Individual.get(":individual", "age"),
		(assign, ":age", reg0),
		(store_current_day, ":curr_day"),
		Individual.get(":individual", "day_joined"),
		(store_sub, ":extra_years", ":curr_day", reg0),
		(val_div, ":extra_years", 90),
		(val_add, ":age", ":extra_years"),
		(val_min, ":age", 63),
		
		(face_keys_set_age, s0, ":age"),
	]),
	
	# script_pti_give_troop_individual_face
	("pti_give_troop_individual_face",
	[
		(store_script_param, ":troop_id", 1),
		(store_script_param, ":individual", 2),
		
		Individual.get(":individual", "troop_type"),
		(troop_get_type, ":gender", reg0),
		(troop_set_type, ":troop_id", ":gender"),
		
		(call_script, "script_pti_individual_get_face_keys", ":individual", s0),
		(troop_set_face_keys, ":troop_id", s0, 0),
		(try_begin),
			(neg|troop_is_hero, ":troop_id"),
			
			(troop_set_face_keys, ":troop_id", s0, 1),
		(try_end),
	]),
	
	## STATS SCRIPTS
	
	# script_pti_troop_reset_stats
	("pti_troop_reset_stats",
	[
		(store_script_param, ":troop_id", 1),
		
		(try_for_range, ":attribute", 0, 4),
			(store_attribute_level, ":points", ":troop_id", ":attribute"),
			(val_mul, ":points", -1),
			(troop_raise_attribute, ":troop_id", ":attribute", ":points"),
		(try_end),
		
		(try_for_range, ":skill", 0, 42),
			(store_skill_level, ":points", ":skill", ":troop_id"),
			(val_mul, ":points", -1),
			(troop_raise_skill, ":troop_id", ":skill", ":points"),
		(try_end),
		
		(try_for_range, ":proficiency", 0, 7),
			(troop_raise_proficiency_linear, ":troop_id", ":proficiency", -700),
		(try_end),
	]),
	
	# script_pti_troop_copy_stats
	("pti_troop_copy_stats",
	[
		(store_script_param, ":target", 1),
		(store_script_param, ":source", 2),
		
		(call_script, "script_pti_troop_reset_stats", ":target"),
		
		(try_for_range, ":attribute", 0, 4),
			(store_attribute_level, ":attribute_level", ":source", ":attribute"),
			(troop_raise_attribute, ":target", ":attribute", ":attribute_level"),
		(try_end),
		
		(try_for_range, ":skill", 0, 42),
			(store_skill_level, ":skill_level", ":skill", ":source"),
			(troop_raise_skill, ":target", ":skill", ":skill_level"),
		(try_end),
		
		(try_for_range, ":proficiency", 0, 7),
			(store_proficiency_level, ":proficiency_level", ":source", ":proficiency"),
			(troop_raise_proficiency_linear, ":target", ":proficiency", ":proficiency_level"),
		(try_end),
	]),
	
	# script_pti_xp_needed_to_upgrade_to
	("pti_xp_needed_to_upgrade_to",
	[
		(store_script_param, ":troop_id", 1),
		
		(store_character_level, ":level", ":troop_id"),
		(call_script, "script_pti_xp_needed_to_reach_level", ":level"),
	]),
	
	# script_pti_xp_needed_to_reach_level
	("pti_xp_needed_to_reach_level",
	[
		(store_script_param, ":level", 1),
		
		#formula : int needed_upgrade_xp = 2 * (30 + 0.006f * level_boundaries[troops[troop_id].level]);
		(get_level_boundary, reg0, ":level"),
		(val_mul, reg0, 6),
		(val_div, reg0, 1000),
		(val_add, reg0, 30),
	]),
	
	# script_pti_level_given_xp
	("pti_level_given_xp",
	[
		(store_script_param, ":xp", 1),
		
		(assign, ":end_cond", 64),
		(try_for_range, ":level", 1, ":end_cond"),
			(call_script, "script_pti_xp_needed_to_reach_level", ":level"),
			(lt, reg0, ":xp"),
			
			(assign, ":return_level", ":level"),
		(else_try),
			(assign, ":end_cond", 0),
		(try_end),
		
		(assign, reg0, ":return_level"),
	]),
	
	## MORALE SCRIPTS
	
	# script_pti_troop_print_morale_description_to_s0
	("pti_troop_print_morale_description_to_s0",
	[
		(store_script_param, ":troop_id", 1),
		
		(call_script, "script_game_get_morale_of_troops_from_faction", ":troop_id"),
		(try_begin),
			(lt, reg0, 10),

			(str_store_string, s0, "@Terrible"),
		(else_try),
			(lt, reg0, 20),

			(str_store_string, s0, "@Very Low"),
		(else_try),
			(lt, reg0, 30),

			(str_store_string, s0, "@Low"),
		(else_try),
			(lt, reg0, 40),

			(str_store_string, s0, "@Below Average"),
		(else_try),
			(lt, reg0, 60),

			(str_store_string, s0, "@Average"),
		(else_try),
			(lt, reg0, 70),

			(str_store_string, s0, "@Above Average"),
		(else_try),
			(lt, reg0, 80),

			(str_store_string, s0, "@High"),
		(else_try),
			(lt, reg0, 90),

			(str_store_string, s0, "@Very High"),
		(else_try),
			(str_store_string, s0, "@Excellent"),
		(try_end),
	]),
	
	## ITEM SCRIPTS
	
	# script_pti_item_get_capabilities
	("pti_item_get_capabilities",
	[
		(store_script_param, ":item", 1),
		
		(assign, ":result", 0),
		(assign, ":capability", 1),
		
		(try_for_range, ":unused", 0, 56),
			(try_begin),
				(item_has_capability, ":item", ":capability"),
				
				(val_or, ":result", ":capability"),
			(try_end),
			
			(val_lshift, ":capability", 1),
		(try_end),
		
		(assign, reg0, ":result"),
	]),
	
	# script_pti_item_get_value
	("pti_item_get_value",
	[
		(store_script_param, ":item", 1),
		
		## POTENTIALLY UPDATE LATER
		(store_item_value, reg0, ":item"),
	]),
	
	# script_dplmc_copy_inventory
	("dplmc_copy_inventory",
	[
	(store_script_param_1, ":source"),
	(store_script_param_2, ":target"),

	(troop_clear_inventory, ":target"),
	(troop_get_inventory_capacity, ":inv_cap", ":source"),
	(try_for_range, ":i_slot", 0, ":inv_cap"),
		(troop_get_inventory_slot, ":item", ":source", ":i_slot"),
		(troop_set_inventory_slot, ":target", ":i_slot", ":item"),
		(troop_get_inventory_slot_modifier, ":imod", ":source", ":i_slot"),
		(troop_set_inventory_slot_modifier, ":target", ":i_slot", ":imod"),
		(troop_inventory_slot_get_item_amount, ":amount", ":source", ":i_slot"),
		(gt, ":amount", 0),
		
		(troop_inventory_slot_set_item_amount, ":target", ":i_slot", ":amount"),
	(try_end),
	]),
	
	# script_pti_troop_get_random_item_of_type
	("pti_troop_get_random_item_of_type",
	[
		(store_script_param, ":troop_id", 1),
		(store_script_param, ":item_type", 2),
		
		(troop_sort_inventory, ":troop_id"),
		
		(assign, ":type_count", 0),
		(assign, ":end_cond", max_inventory_items),
		(try_for_range, ":slot", 0, ":end_cond"),
			(troop_get_inventory_slot, ":item", ":troop_id", ":slot"),
			(gt, ":item", 0),
			
			(try_begin),
				(item_get_type, ":curr_type", ":item"),
				(eq, ":curr_type", ":item_type"),
				
				(val_add, ":type_count", 1),
			(try_end),
			
		#(else_try),
		#	(assign, ":end_cond", 0),
		(try_end),
		
		(try_begin),
			(gt, ":type_count", 0),
			
			(store_random_in_range, ":item_num", 0, ":type_count"),
			(assign, ":type_count", 0),
			(assign, ":end_cond", max_inventory_items),
			(try_for_range, ":slot", 0, ":end_cond"),
				(troop_get_inventory_slot, ":item", ":troop_id", ":slot"),
				(gt, ":item", 0),
				
				(item_get_type, ":curr_type", ":item"),
				(eq, ":curr_type", ":item_type"),
				
				(try_begin),
					(eq, ":type_count", ":item_num"),
					
					(assign, ":end_cond", 0),
				(try_end),
				
				(val_add, ":type_count", 1),
			(try_end),
			
			(assign, reg0, ":item"),
		(else_try),
			(assign, reg0, -1),
		(try_end),
	]),
	
	# script_pti_troop_get_random_item_of_type_between
	("pti_troop_get_random_item_of_type_between",
	[
		(store_script_param, ":troop_id", 1),
		(store_script_param, ":types_begin", 2),
		(store_script_param, ":types_end", 3),
		
		(troop_sort_inventory, ":troop_id"),
		
		(assign, ":max_slot", 0),
		(assign, ":type_count", 0),
		(assign, ":end_cond", max_inventory_items),
		(try_for_range, ":slot", 0, max_inventory_items),
			(troop_get_inventory_slot, ":item", ":troop_id", ":slot"),
			(gt, ":item", 0),
			
			(assign, ":max_slot", ":slot"),
			
			(try_begin),
				(item_get_type, ":curr_type", ":item"),
				(is_between, ":curr_type", ":types_begin", ":types_end"),
				
				(val_add, ":type_count", 1),
			(try_end),
			
		(else_try),
			(assign, ":end_cond", 0),
		(try_end),
		
		(val_add, ":max_slot", 1),
		
		(try_begin),
			(gt, ":type_count", 0),
			
			(store_random_in_range, ":item_num", 0, ":type_count"),
			(assign, ":type_count", 0),
			(assign, ":end_cond", ":max_slot"),
			(try_for_range, ":slot", 0, ":end_cond"),
				(troop_get_inventory_slot, ":item", ":troop_id", ":slot"),
				(gt, ":item", 0),
				
				(item_get_type, ":curr_type", ":item"),
				(is_between, ":curr_type", ":types_begin", ":types_end"),
				
				(try_begin),
					(eq, ":type_count", ":item_num"),
					
					(assign, ":end_cond", 0),
				(try_end),
				
				(val_add, ":type_count", 1),
			(try_end),
			
			(assign, reg0, ":item"),
		(else_try),
			(assign, reg0, -1),
		(try_end),
	]),
	
	## INDIVIDUAL EQUIPMENT SCRIPTS
	
	# script_cf_pti_troop_can_use_item
	("cf_pti_troop_can_use_item",
	[
		(store_script_param, ":troop_id", 1),
		(store_script_param, ":item", 2),
		
		(item_get_type, ":item_type", ":item"),
		(item_get_difficulty, ":requirement", ":item"),
		
		# Get relevant stat
		(try_begin),
			(eq, ":item_type", itp_type_horse),
			(store_skill_level, ":stat", skl_riding, ":troop_id"),
		(else_try),
			(eq, ":item_type", itp_type_shield),
			(store_skill_level, ":stat", skl_shield, ":troop_id"),
		(else_try),
			(eq, ":item_type", itp_type_bow),
			(store_skill_level, ":stat", skl_power_draw, ":troop_id"),
		(else_try),
			(eq, ":item_type", itp_type_thrown),
			(store_skill_level, ":stat", skl_power_throw, ":troop_id"),
		(else_try),
			(store_attribute_level, ":stat", ":troop_id", ca_strength),
		(try_end),
		
		# Compare
		(ge, ":stat", ":requirement"),
	]),
	
	# script_pti_individual_get_base_item
	individual_get_item("base"),
	
	# script_pti_individual_get_looted_item
	individual_get_item("looted"),
	
	# script_pti_individual_set_base_item
	individual_set_item("base"),
	
	# script_pti_individual_set_looted_item
	individual_set_item("looted"),
	
	# script_pti_individual_generate_base_equipment
	("pti_individual_generate_base_equipment",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(call_script, "script_dplmc_copy_inventory", ":troop_id", "trp_temp_troop"),
		
		# Clear current base armour first (important when upgrading)
		Individual.set(":individual", "base_armour", 0),
		Individual.set(":individual", "base_weapons", 0),
		Individual.set(":individual", "base_horse", 0),
		
		# Generate armour
		(assign, ":equipment", 0),
		(try_for_range_backwards, ":armour_type", itp_type_head_armor, itp_type_pistol),
			(val_lshift, ":equipment", ITEM_BITS),
			
			(call_script, "script_pti_troop_get_random_item_of_type", "trp_temp_troop", ":armour_type"),
			(assign, ":item", reg0),
			(gt, ":item", 0),
			
			(val_or, ":equipment", ":item"),
		(try_end),
		Individual.set(":individual", "base_armour", ":equipment"),
		
		(assign, ":next_weapon_slot", ek_item_0),
		
		# Generate ranged weapon if applicable
		(try_begin),
			(store_random_in_range, ":rand", 0, 2),
			(this_or_next|troop_is_guarantee_ranged, ":troop_id"),
			(eq, ":rand", 1),	# If not guaranteed ranged, 50% chance
			
			## CONSIDER WORKING IN WAY TO INCLUDE GUNS
			# Get the ranged weapon (if there is one)
			(call_script, "script_pti_troop_get_random_item_of_type_between", "trp_temp_troop", itp_type_bow, itp_type_goods),
			(assign, ":weapon", reg0),
			(gt, ":weapon", 0),
			
			(call_script, "script_pti_individual_set_base_item", ":individual", ":next_weapon_slot", ":weapon"),
			(val_add, ":next_weapon_slot", 1),
			
			# Get the appropriate missiles if applicable
			(item_get_type, ":weapon_type", ":weapon"),
			(try_begin),
				(eq, ":weapon_type", itp_type_bow),
				
				(call_script, "script_pti_troop_get_random_item_of_type", "trp_temp_troop", itp_type_arrows),
				(gt, reg0, 0),
				
				(call_script, "script_pti_individual_set_base_item", ":individual", ":next_weapon_slot", reg0),
				(val_add, ":next_weapon_slot", 1),
			(else_try),
				(eq, ":weapon_type", itp_type_crossbow),
				
				(call_script, "script_pti_troop_get_random_item_of_type", "trp_temp_troop", itp_type_bolts),
				(gt, reg0, 0),
				
				(call_script, "script_pti_individual_set_base_item", ":individual", ":next_weapon_slot", reg0),
				(val_add, ":next_weapon_slot", 1),
			(try_end),
		(try_end),
		
		# Generate shield if applicable
		(try_begin),
			(store_random_in_range, ":rand", 0, 2),
			## TODO: FIND WAY TO CHECK IF GUARANTEED SHIELD
			#(this_or_next|troop_is_guarantee_shield, ":troop_id"),
			#(eq, ":rand", 1),	# If not guaranteed shield, 50% chance
			
			(call_script, "script_pti_troop_get_random_item_of_type", "trp_temp_troop", itp_type_shield),
				(gt, reg0, 0),
				
				(call_script, "script_pti_individual_set_base_item", ":individual", ":next_weapon_slot", reg0),
				(val_add, ":next_weapon_slot", 1),
		(try_end),
		
		# Generate melee weapons
		(store_sub, ":upper_bound", ek_head - ek_item_0 + 1, ":next_weapon_slot"),
		(store_random_in_range, ":num_weapons", 1, ":upper_bound"),
		(try_for_range, ":unused", 0, ":num_weapons"),
			(call_script, "script_pti_troop_get_random_item_of_type_between", "trp_temp_troop", itp_type_one_handed_wpn, itp_type_arrows),
			(assign, ":weapon", reg0),
			(gt, ":weapon", 0),
			
			(call_script, "script_pti_individual_set_base_item", ":individual", ":next_weapon_slot", ":weapon"),
			(val_add, ":next_weapon_slot", 1),
			(store_item_kind_count, ":item_count", ":weapon", "trp_temp_troop"),
			(troop_remove_items, "trp_temp_troop", ":weapon", ":item_count"),
		(try_end),
		
		# Generate horse
		(try_begin),
			(store_random_in_range, ":rand", 0, 2),
			(this_or_next|troop_is_guarantee_horse, ":troop_id"),
			(eq, ":rand", 1),	# If not guaranteed horse, 50% chance
			
			(call_script, "script_pti_troop_get_random_item_of_type", "trp_temp_troop", itp_type_horse),
			(gt, reg0, 0),
			
			Individual.set(":individual", "base_horse", reg0),
		(try_end),
	]),
	
	# script_pti_equip_agent_as_individual
	("pti_equip_agent_as_individual",
	[
		(store_script_param, ":agent", 1),
		(store_script_param, ":individual", 2),
		
		# Setting armour should not be necessary thanks to the tf_guarantee_all flag
		#Individual.get(":individual", "base_armour"),
		#(assign, ":equipment", reg0),
		#(try_for_range, ":slot", ek_head, ek_horse),
		#	(store_and, ":item", ":equipment", mask(ITEM_BITS)),
		#	(agent_equip_item, ":agent", ":item"),
		#	(val_rshift, ":equipment", ITEM_BITS),
		#(try_end),
		
		Individual.get(":individual", "base_weapons"),
		(assign, ":equipment", reg0),
		(try_for_range, ":slot", ek_item_0, ek_head),
			(store_and, ":item", ":equipment", mask(ITEM_BITS)),
			(agent_equip_item, ":agent", ":item"),
			(val_rshift, ":equipment", ITEM_BITS),
		(try_end),
	]),
	
	# script_pti_equip_troop_as_individual
	("pti_equip_troop_as_individual",
	[
		(store_script_param, ":troop_id", 1),
		(store_script_param, ":individual", 2),
		
		(troop_clear_inventory, ":troop_id"),
		(try_for_range, ":slot", 0, num_equipment_kinds),
			(troop_set_inventory_slot, ":troop_id", ":slot", -1),
		(try_end),
		
		Individual.get(":individual", "base_armour"),
		(assign, ":equipment", reg0),
		(assign, ":armour_slots_start", ek_head),
		(try_begin),
			(eq, "$pti_nps_open", 1),
			(eq, "$pti_show_helmets", 0),
			
			(assign, ":armour_slots_start", ek_body),
			(val_rshift, ":equipment", ITEM_BITS),
		(try_end),
		
		(try_for_range, ":slot", ":armour_slots_start", ek_horse),
			(store_and, ":item", ":equipment", mask(ITEM_BITS)),
			(try_begin),
				(gt, ":item", 0),
				
				(troop_add_item, ":troop_id", ":item"),
			(try_end),
			
			(val_rshift, ":equipment", ITEM_BITS),
		(try_end),
		
		Individual.get(":individual", "base_weapons"),
		(assign, ":equipment", reg0),
		(try_for_range, ":slot", ek_item_0, ek_head),
			(store_and, ":item", ":equipment", mask(ITEM_BITS)),
			(gt, ":item", 0),
			
			(troop_add_item, ":troop_id", ":item"),
			(val_rshift, ":equipment", ITEM_BITS),
		(try_end),
		
		(try_begin),
			Individual.get(":individual", "base_horse"),
			(gt, reg0, 0),
			(troop_add_item, ":troop_id", reg0),
		(try_end),
		
		(troop_sort_inventory, ":troop_id"),
		(troop_equip_items, ":troop_id"),
	]),
	
	## INDIVIDUAL LOOTING SCRIPTS
	
	# script_cf_pti_individual_can_loot_horse
	("cf_pti_individual_can_loot_horse",
	[
		(store_script_param, ":individual", 1),
		
		## POTENTIALLY UPDATE LATER
		# Individual can loot horses if they currently have a horse
		(call_script, "script_pti_individual_get_base_item", ":individual", ek_horse),
		(gt, reg0, 0),
	]),
	
	# script_pti_individual_loot_from_agent
	("pti_individual_loot_from_agent",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":agent", 2),
		
		(try_for_range, ":slot", ek_item_0, ek_head),
			(call_script, "script_pti_individual_loot_weapon_from_agent", ":individual", ":agent", ":slot"),
		(try_end),
		
		(try_for_range, ":slot", ek_head, ek_horse),
			(call_script, "script_pti_individual_loot_armour_from_agent", ":individual", ":agent", ":slot"),
		(try_end),
		
		(try_begin),
			(call_script, "script_cf_pti_individual_can_loot_horse", ":individual"),
			(call_script, "script_pti_individual_loot_horse_from_agent", ":individual", ":agent"),
		(try_end),
	]),
	
	# script_pti_individual_loot_armour_from_agent
	("pti_individual_loot_armour_from_agent",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":agent", 2),
		(store_script_param, ":slot", 3),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(agent_get_item_slot, ":looted_item", ":agent", ":slot"),
		(try_begin),
			(gt, ":looted_item", 0),
			
			## UPDATE THIS LATER - LET INDIVIDUALS HOLD FOR LATER OR SHARE LOOTED ITEMS
			# Only proceed if the individual can use this item
			(call_script, "script_cf_pti_troop_can_use_item", ":troop_id", ":looted_item"),
			
			# Get current piece of looted armour
			(call_script, "script_pti_individual_get_looted_item", ":individual", ":slot"),
			(assign, ":curr_item", reg0),
			
			# Get values of current and newly looted armour
			(call_script, "script_pti_item_get_value", ":looted_item"),
			(assign, ":looted_value"),
			
			(assign, ":curr_value", 0),
			(try_begin),
				(gt, ":curr_item", 0),
				
				(call_script, "script_pti_item_get_value", ":curr_item"),
				(assign, ":curr_value"),
			(try_end),
			
			# Loot armour if it is of higher value than current armour
			(gt, ":looted_value", ":curr_value"),
			
			(call_script, "script_pti_individual_set_looted_item", ":individual", ":slot", ":looted_item"),
		(try_end),
	]),
	
	# script_pti_individual_loot_weapon_from_agent
	("pti_individual_loot_weapon_from_agent",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":agent", 2),
		(store_script_param, ":slot", 3),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(agent_get_item_slot, ":looted_item", ":agent", ":slot"),
		(try_begin),
			(gt, ":looted_item", 0),
			
			## UPDATE THIS LATER - LET INDIVIDUALS HOLD FOR LATER OR SHARE LOOTED ITEMS
			# Only proceed if the individual can use this item
			(call_script, "script_cf_pti_troop_can_use_item", ":troop_id", ":looted_item"),
			
			# Get the item's type and capabilities
			(item_get_type, ":looted_type", ":looted_item"),
			(call_script, "script_pti_item_get_capabilities", ":looted_item"),
			(assign, ":looted_capability", reg0),
			
			# Iterate through the individual's base items to find one potentially worth replacing
			(assign, ":end_cond", ek_head),
			(try_for_range, ":curr_slot", ek_item_0, ":end_cond"),
				(call_script, "script_pti_individual_get_base_item", ":individual", ":curr_slot"),
				(assign, ":curr_base_item", reg0),
				
				(gt, ":curr_base_item", 0),
				
				# Make sure item is of same type (e.g. one handed, two handed, bow, etc)
				(item_get_type, ":curr_type", ":curr_base_item"),
				(eq, ":curr_type", ":looted_type"),
				
				# Proceed if newly looted item is of higher value than any already looted item in the same slot
				(call_script, "script_pti_individual_get_looted_item", ":individual", ":curr_slot"),
				(assign, ":curr_looted_item", reg0),
				
				(call_script, "script_pti_item_get_value", ":looted_item"),
				(assign, ":looted_value"),
				
				(call_script, "script_pti_item_get_value", ":curr_looted_item"),
				(assign, ":curr_value"),
				
				(gt, ":looted_value", ":curr_value"),
				
				# Proceed if either the item isn't a melee weapon or it is a melee weapon of the same capabilities (e.g. lance vs spear, sword vs axe, etc)
				(assign, ":continue", 0),
				(try_begin),
					(gt, ":curr_type", itp_type_polearm),
					
					(assign, ":continue", 1),
				(else_try),
					(call_script, "script_pti_item_get_capabilities", ":curr_base_item"),
					(eq, reg0, ":looted_capability"),
					
					(assign, ":continue", 1),
				(try_end),
				
				(eq, ":continue", 1),
				
				# Loot the item and end the loop if all above conditions are met
				(call_script, "script_pti_individual_set_looted_item", ":individual", ":curr_slot", ":looted_item"),
				(assign, ":end_cond", 0),
			(try_end),
		(try_end),
	]),
	
	# script_pti_individual_loot_horse_from_agent
	("pti_individual_loot_horse_from_agent",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":agent", 2),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(try_begin),
			(agent_get_horse, ":horse", ":agent"),
			(gt, ":horse", 0),
			
			(agent_get_item_id, ":horse_id", ":horse"),
			(call_script, "script_cf_pti_troop_can_use_item", ":troop_id", ":horse"),
			
			(assign, ":curr_value", 0),
			(try_begin),
				(call_script, "script_pti_individual_get_looted_item", ":individual", ek_horse),
				(gt, reg0, 0),
				
				(call_script, "script_pti_item_get_value", reg0),
				(assign, ":curr_value", reg0),
			(try_end),
			
			(call_script, "script_pti_item_get_value", ":horse_id"),
			(assign, ":looted_value", reg0),
			
			(gt, ":looted_value", ":curr_value"),
			
			(call_script, "script_pti_individual_set_looted_item", ":individual", ek_horse, ":horse_id"),
		(try_end),
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
			
			(faction_get_slot, ":names_begin", ":faction", pti_slot_faction_female_names_begin),
			(faction_get_slot, ":names_end", ":faction", pti_slot_faction_female_names_end),
			
			(try_begin),
				(eq, ":names_begin", 0),
				
				(assign, ":names_begin", "str_default_female_name_1"),
				(assign, ":names_end", "str_default_female_names_end"),
			(try_end),
		(else_try),
			(faction_get_slot, ":names_begin", ":faction", pti_slot_faction_male_names_begin),
			(faction_get_slot, ":names_end", ":faction", pti_slot_faction_male_names_end),
			
			(try_begin),
				(eq, ":names_begin", 0),
				
				(assign, ":names_begin", "str_default_male_name_1"),
				(assign, ":names_end", "str_default_male_names_end"),
			(try_end),
		(try_end),
		
		(assign, reg0, ":names_begin"),
		(assign, reg1, ":names_end"),
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
	
	# script_pti_individual_get_days_of_service
	("pti_individual_get_days_of_service",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "day_joined"),
		(assign, ":day_joined", reg0),
		(store_current_day, reg0),
		(val_sub, reg0, ":day_joined"),
	]),
	
	# script_pti_upgrade_individual_in_party_to
	("pti_upgrade_individual_in_party_to",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":party", 2),
		(store_script_param, ":upgrade_troop_id", 3),
		
		Individual.get(":individual", "troop_type"),
		(party_remove_members, ":party", reg0, 1),
		Individual.set(":individual", "troop_type", ":upgrade_troop_id"),
		(party_add_members, ":party", ":upgrade_troop_id", 1),
	]),
	
	# script_pti_remove_individual_from_party
	("pti_remove_individual_from_party",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":party", 2),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(call_script, "script_pti_linked_list_get_troop_sub_list_head", ":list", ":troop_id"),
		(call_script, "script_pti_linked_list_remove_from_start_index", ":list", ":individual", reg0),
		
		(party_remove_members, ":party", ":troop_id", 1),
		(party_remove_members, ":list", ":troop_id", 1),
	]),
	
	# script_pti_kill_individual_in_party
	("pti_kill_individual_in_party",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":party", 2),
		
		(call_script, "script_pti_remove_individual_from_party", ":individual", ":party"),
		
		# Clear the individual's data
		(try_for_range, ":offset", 0, Individual.num_attribute_slots),
			(store_add, ":index", ":individual", ":offset"),
			(call_script, "script_pti_array_set", "$pti_individuals_array", ":index", 0),
		(try_end),
		
		# Mark this index as the next free one if it is earlier than the current next free one
		(try_begin),
			(lt, ":individual", "$pti_individuals_array_next_free_index"),
			
			(assign, "$pti_individuals_array_next_free_index", ":individual"),
		(try_end),
	]),
	
	# script_pti_mark_individual_for_killing
	# Killing individuals while iterating over them causes problems, so use this and then script_pti_kill_marked_individuals after your loop instead
	("pti_mark_individual_for_killing",
	[
		(store_script_param, ":individual", 1),
		
		Individual.set(":individual", "marked_for_kill", 1),
	]),
	
	# script_pti_kill_individuals_in_party
	("pti_kill_individuals_in_party",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		pti_count_individuals(party = ":party", condition = ":condition_script"),
		(assign, ":count", reg0),
		
		(try_for_range, ":unused", 0, ":count"),
			pti_get_first_individual(party = ":party", condition = ":condition_script"),
			(call_script, "script_pti_kill_individual_in_party", "$pti_current_individual", ":party"),
		(try_end),
	]),
	
	# script_cf_party_remove_random_regular_troop
	# Overwriting this allows for the removal of troops when choosing to leave some behind to escape a battle
	# Input: arg1 = party_no
	# Output: troop_id that has been removed (can fail)
	("cf_party_remove_random_regular_troop",
	[
		(store_script_param_1, ":party"),
		
		pti_count_individuals(party = ":party", condition = "script_cf_pti_individual_is_nonwounded"),
		(assign, ":count", reg0),
		
		(assign, reg0, -1),
		(gt, ":count", 0),
		
		(store_random_in_range, ":rand", 0, ":count"),
		pti_get_first_individual(party = ":party", condition = "script_cf_pti_individual_is_nonwounded"),
		(try_for_range, ":unused", 0, ":rand"),
			pti_get_next_individual(party = ":party", condition = "script_cf_pti_individual_is_nonwounded"),
		(try_end),
		
		Individual.get("$pti_current_individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(call_script, "script_pti_kill_individual_in_party", "$pti_current_individual", ":party"),
		(call_script, "script_pti_restore_party", ":party"),
		
		(assign, reg0, ":troop_id"),
	]),
	
	# script_pti_heal_individual
	("pti_heal_individual",
	[
		(store_script_param, ":individual", 1),
		
		Individual.set(":individual", "is_wounded", 0),
		
		(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		(display_message, "@{s1} healed"),
	]),
	
	# script_pti_wound_individual
	("pti_wound_individual",
	[
		(store_script_param, ":individual", 1),
		
		Individual.set(":individual", "is_wounded", 1),
	]),
	
	# script_pti_apply_script_to_party_members_meeting_condition
	("pti_apply_script_to_party_members_meeting_condition",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":script", 2),
		(store_script_param, ":condition_script", 3),
		
		pti_count_individuals(party = ":party", condition = ":condition_script"),
		(assign, ":count", reg0),
		
		pti_get_first_individual(party = ":party", condition = ":condition_script"),
		(try_for_range, ":i", 0, ":count"),
			(call_script, ":script", "$pti_current_individual"),
			pti_get_next_individual(party = ":party", condition = ":condition_script"),
		(try_end),
	]),
	
	# script_pti_apply_script_randomly_to_party_members_meeting_condition_with_troop_id
	("pti_apply_script_randomly_to_party_members_meeting_condition_with_troop_id",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":script", 2),
		(store_script_param, ":condition_script", 3),
		(store_script_param, ":n", 4),
		(store_script_param, ":troop_id", 5),
		
		pti_count_individuals(":party", ":troop_id", ":condition_script"),
		(assign, ":count", reg0),
		
		pti_get_first_individual(":party", ":troop_id", ":condition_script"),
		(try_for_range, ":i", 0, ":count"),
			(try_begin),
				(store_sub, ":remaining_individuals", ":count", ":i"),
				(store_random_in_range, ":rand", 0, ":remaining_individuals"),
				(le, ":rand", ":n"),
				
				(call_script, ":script", "$pti_current_individual"),
				(val_sub, ":n", 1),
				
				(eq, ":n", 0),
				
				(assign, ":count", 0),	# End the loop when enough have been healed
			(try_end),
			
			pti_get_next_individual(":party", ":troop_id", ":condition_script"),
		(try_end),
	]),
	
	# script_pti_apply_script_randomly_to_party_members_meeting_condition
	("pti_apply_script_randomly_to_party_members_meeting_condition",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":script", 2),
		(store_script_param, ":condition_script", 3),
		(store_script_param, ":n", 4),
		
		pti_count_individuals(party = ":party", condition = ":condition_script"),
		(assign, ":count", reg0),
		
		pti_get_first_individual(party = ":party", condition = ":condition_script"),
		(try_for_range, ":i", 0, ":count"),
			(try_begin),
				(store_sub, ":remaining_individuals", ":count", ":i"),
				(store_random_in_range, ":rand", 0, ":remaining_individuals"),
				(le, ":rand", ":n"),
				
				(call_script, ":script", "$pti_current_individual"),
				(val_sub, ":n", 1),
				
				(eq, ":n", 0),
				
				(assign, ":count", 0),	# End the loop when enough have been healed
			(try_end),
			
			pti_get_next_individual(party = ":party", condition = ":condition_script"),
		(try_end),
	]),
	
	# script_pti_apply_wound_treatment_to_individuals
	("pti_apply_wound_treatment_to_individuals",
	[
		(store_script_param, ":party", 1),
		
		(party_get_num_companion_stacks, ":num_stacks", ":party"),
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":troop_id", ":party", ":stack"),
			(neg|troop_is_hero, ":troop_id"),
			
			(party_stack_get_num_wounded, ":party_wounded_count", ":party", ":stack"),
			
			pti_count_individuals(party = ":party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_wounded"),
			(assign, ":individuals_wounded_count", reg0),
			
			(gt, ":individuals_wounded_count", ":party_wounded_count"),
			
			(store_sub, ":difference", ":individuals_wounded_count", ":party_wounded_count"),
			pti_apply_script_randomly_to_party_members("script_pti_heal_individual", ":difference", party = ":party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_wounded"),
		(try_end),
	]),
	
	# script_pti_apply_casualties_to_individuals
	("pti_apply_casualties_to_individuals",
	[
		(store_script_param, ":party", 1),
		
		(party_get_num_companion_stacks, ":num_stacks", ":party"),
		(try_for_range, ":stack", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":troop_id", ":party", ":stack"),
			
			# Apply kills
			(party_stack_get_size, ":party_count", ":party", ":stack"),
			
			pti_count_individuals(party = ":party", troop_id = ":troop_id"),
			(assign, ":individuals_count", reg0),
			
			(gt, ":individuals_count", ":party_count"),
			
			(store_sub, ":difference", ":individuals_count", ":party_count"),
			(assign, "$pti_selected_party_id", ":party"),
			pti_apply_script_randomly_to_party_members("script_pti_mark_individual_for_killing", ":difference", party = ":party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_nonwounded"),
			(call_script, "script_pti_kill_individuals_in_party", ":party", "script_cf_pti_individual_is_marked_for_killing"),
			
			(str_store_troop_name_by_count, s0, ":troop_id", ":difference"),
			(assign, reg0, ":difference"),
			(display_message, "@{reg0} {s0} killed"),
			
			# Apply wounds
			(party_stack_get_num_wounded, ":party_wounded_count", ":party", ":stack"),
			
			pti_count_individuals(party = ":party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_wounded"),
			(assign, ":individuals_wounded_count", reg0),
			
			(gt, ":party_wounded_count", ":individuals_wounded_count"),
			
			(store_sub, ":difference", ":party_wounded_count", ":individuals_wounded_count"),
			pti_apply_script_randomly_to_party_members("script_pti_wound_individual", ":difference", party = ":party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_nonwounded"),
			
			(str_store_troop_name_by_count, s0, ":troop_id", ":difference"),
			(assign, reg0, ":difference"),
			(display_message, "@{reg0} {s0} wounded"),
		(try_end),
	]),
	
	# script_pti_get_trainer_amount_for_level
	("pti_get_trainer_amount_for_level",
	[
		(store_script_param, ":trainer_level", 1),
		
		(try_begin),
			(eq, ":trainer_level", 0),
			
			(assign, reg0, 0),
		(else_try),
			(eq, ":trainer_level", 1),
			
			(assign, reg0, 4),
		(else_try),
			(eq, ":trainer_level", 2),
			
			(assign, reg0, 10),
		(else_try),
			(eq, ":trainer_level", 3),
			
			(assign, reg0, 16),
		(else_try),
			(eq, ":trainer_level", 4),
			
			(assign, reg0, 23),
		(else_try),
			(eq, ":trainer_level", 5),
			
			(assign, reg0, 30),
		(else_try),
			(eq, ":trainer_level", 6),
			
			(assign, reg0, 38),
		(else_try),
			(eq, ":trainer_level", 7),
			
			(assign, reg0, 46),
		(else_try),
			(eq, ":trainer_level", 8),
			
			(assign, reg0, 55),
		(else_try),
			(eq, ":trainer_level", 9),
			
			(assign, reg0, 65),
		(else_try),
			(assign, reg0, 80),
		(try_end),
	]),
	
	# script_pti_individual_add_xp
	("pti_individual_add_xp",
	[
		(store_script_param, ":individual", 1),
		
		#(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		#(assign, reg0, "$pti_xp_to_add"),
		#(display_message, "@Adding {reg0} xp to {s0} {s1}"),
		
		Individual.get(":individual", "xp"),
		(val_add, reg0, "$pti_xp_to_add"),
		Individual.set(":individual", "xp", reg0),
	]),
	
	## PARTY SCRIPTS
	
	# script_pti_party_copy_prisoners
	("pti_party_copy_prisoners",
	[
		(store_script_param, ":target_party", 1),
		(store_script_param, ":source_party", 2),
		
		#(str_store_party_name, s0, ":source_party"),
		#(str_store_party_name, s1, ":target_party"),
		#(display_message, "@Transferring prisoners from {s0} to {s1}"),
		
		(party_get_num_prisoner_stacks, ":num_stacks", ":source_party"),
		(try_for_range, ":stack_no", 0, ":num_stacks"),
			(party_prisoner_stack_get_troop_id, ":stack_troop", ":source_party", ":stack_no"),
			(party_prisoner_stack_get_size, ":stack_size", ":source_party", ":stack_no"),
			(party_add_prisoners, ":target_party", ":stack_troop", ":stack_size"),
			
			#(str_store_troop_name_by_count, s0, ":stack_troop", ":stack_size"),
			#(str_store_party_name, s1, ":target_party"),
			#(assign, reg0, ":stack_size"),
			#(display_message, "@Transferring {reg0} {s0} to {s1}"),
		(try_end),
	]),
	
	# script_pti_party_copy_heroes
	("pti_party_copy_heroes",
	[
		(store_script_param, ":target_party", 1),
		(store_script_param, ":source_party", 2),
		
		#(str_store_party_name, s0, ":source_party"),
		#(str_store_party_name, s1, ":target_party"),
		#(display_message, "@Transferring heroes from {s0} to {s1}"),
		
		(party_get_num_companion_stacks, ":num_stacks", ":source_party"),
		(try_for_range, ":stack_no", 0, ":num_stacks"),
			(party_stack_get_troop_id, ":stack_troop", ":source_party", ":stack_no"),
			(troop_is_hero, ":stack_troop"),
			(neq, ":stack_troop", "trp_player"),
			
			(party_add_members, ":target_party", ":stack_troop", 1),
			
			#(str_store_troop_name, s0, ":stack_troop"),
			#(str_store_party_name, s1, ":target_party"),
			#(display_message, "@Transferring {s0} to {s1}"),
		(try_end),
	]),
	
	## BATTLE SCRIPTS ##
	
	# script_pti_troop_get_xp_for_killing
	("pti_troop_get_xp_for_killing",
	[
		(store_script_param, ":troop_id", 1),
		
		(call_script, "script_game_get_prisoner_price", ":troop_id"),
		(val_mul, reg0, 6),
		(val_div, reg0, 5),
	]),
	
	# script_pti_set_up_individual_troop
	("pti_set_up_individual_troop",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":troop_id", 2),
		
		(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		(assign, ":troop_type", reg0),
		Individual.get(":individual", "home"),
		(str_store_party_name, s2, reg0),
		(troop_set_name, ":troop_id", "$pti_individual_name_format"),
		
		(troop_set_slot, ":troop_id", pti_slot_troop_regular_troop_type, ":troop_type"),
		
		(call_script, "script_pti_troop_copy_stats", ":troop_id", ":troop_type"),
		(call_script, "script_pti_equip_troop_as_individual", ":troop_id", ":individual"),
		(call_script, "script_pti_give_troop_individual_face", ":troop_id", ":individual"),
		
		Individual.get(":individual", "class_overridden"),
		(try_begin),
			(eq, reg0, 1),
			
			Individual.get(":individual", "class"),
			(troop_set_class, ":troop_id", reg0),
		(else_try),
			(troop_get_class, ":class", ":troop_type"),
			(troop_set_class, ":troop_id", ":class"),
		(try_end),
		
		(troop_set_slot, ":troop_id", pti_slot_troop_individual, ":individual"),
	]),
	
	# script_pti_individual_agent_process_battle
	("pti_individual_agent_process_battle",
	[
		(store_script_param, ":agent", 1),
		
		(agent_get_slot, ":individual", ":agent", pti_slot_agent_individual),
		
		#(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		#(display_message, "@Processing battle for {s0} {s1}"),
		
		# Increase the kill and knock out counts
		(agent_get_kill_count, ":battle_kill_count", ":agent"),
		Individual.get(":individual", "kill_count"),
		(val_add, reg0, ":battle_kill_count"),
		Individual.set(":individual", "kill_count", reg0),
		
		(agent_get_kill_count, ":battle_knock_out_count", ":agent", 1),
		Individual.get(":individual", "knock_out_count"),
		(val_add, reg0, ":battle_knock_out_count"),
		Individual.set(":individual", "knock_out_count", reg0),
		
		# Update the highest kills in a given battle if applicable
		(val_add, ":battle_kill_count", ":battle_knock_out_count"),
		Individual.get(":individual", "most_kills"),
		(val_max, reg0, ":battle_kill_count"),
		Individual.set(":individual", "most_kills", reg0),
		
		# Add xp gained in battle
		(agent_get_slot, ":xp_gained", ":agent", pti_slot_agent_xp_gained),
		Individual.get(":individual", "xp"),
		(val_add, reg0, ":xp_gained"),
		Individual.set(":individual", "xp", reg0),
		
		# Update the best kill if applicable
		(try_begin),
			(neg|agent_slot_eq, ":agent", pti_slot_agent_best_kill_level, 0),
			
			Individual.get(":individual", "best_kill"),
			(assign, ":best_kill", reg0),
			(assign, ":best_kill_level", 0),
			(try_begin),
				(gt, ":best_kill", 0),
				
				(store_character_level, ":best_kill_level", ":best_kill"),
			(try_end),
			
			(agent_get_slot, ":battle_best_kill_level", ":agent", pti_slot_agent_best_kill_level),
			(gt, ":battle_best_kill_level", ":best_kill_level"),
			
			(agent_get_slot, ":battle_best_kill", ":agent", pti_slot_agent_best_kill),
			Individual.set(":individual", "best_kill", ":battle_best_kill"),
		(try_end),
	]),
	
	# script_pti_individual_agent_process_casualty
	("pti_individual_agent_process_casualty",
	[
		(store_script_param, ":agent", 1),
		(store_script_param, ":wounded", 2),
		
		(agent_get_slot, ":individual", ":agent", pti_slot_agent_individual),
		
		#(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		#(assign, reg0, ":agent"),
		#(assign, reg1, ":individual"),
		#(display_message, "@Processing casualty of {s0} {s1}. Agent ID: {reg0} | Individual ID: {reg1}"),
		
		(try_begin),
			(eq, ":wounded", 1),
			
			(call_script, "script_pti_individual_agent_process_battle", ":agent"),
			
			Individual.set(":individual", "is_wounded", 1),
			Individual.get(":individual", "times_wounded"),
			(val_add, reg0, 1),
			Individual.set(":individual", "times_wounded", reg0),
		(else_try),
			(call_script, "script_pti_kill_individual_in_party", ":individual", "p_main_party"),
		(try_end),
	]),
	
	# script_pti_process_battle
	("pti_process_battle",
	[
		(get_player_agent_no, ":player_agent"),
		
		(try_for_agents, ":agent"),
			(agent_is_human, ":agent"),
			(agent_is_alive, ":agent"),
			(neq, ":agent", ":player_agent"),
			
			(agent_get_party_id, ":agent_party", ":agent"),
			(eq, ":agent_party", "p_main_party"),
			
			(call_script, "script_pti_individual_agent_process_battle", ":agent"),
		(try_end),
	]),
	
	# script_pti_restore_party
	("pti_restore_party",
	[
		(store_script_param, ":party", 1),
		
		# Clear party, but retain prisoners
		(call_script, "script_pti_party_copy_prisoners", "p_pti_prisoners", ":party"),
		(call_script, "script_pti_party_copy_heroes", "p_pti_prisoners", ":party"),
		(party_clear, ":party"),
		(call_script, "script_pti_party_copy_prisoners", ":party", "p_pti_prisoners"),
		(call_script, "script_pti_party_copy_heroes", ":party", "p_pti_prisoners"),
		(party_clear, "p_pti_prisoners"),
		
		pti_count_individuals(party = ":party"),
		(assign, ":count", reg0),
		
		pti_get_first_individual(party = ":party"),
		(try_for_range, ":unused", 0, ":count"),
			Individual.get("$pti_current_individual", "troop_type"),
			(assign, ":troop_id", reg0),
			(party_add_members, ":party", ":troop_id", 1),
			
			Individual.get("$pti_current_individual", "is_wounded"),
			(try_begin),
				(eq, reg0, 1),
				
				(party_wound_members, ":party", ":troop_id", 1),
			(try_end),
			
			pti_get_next_individual(":party"),
		(try_end),
	]),
	
	## NEW PARTY SCREEN SCRIPTS ##
	
	# script_pti_open_exchange_screen
	("pti_open_exchange_screen",
	[
		(store_script_param, ":exchange_leader", 1),
		(store_script_param, ":party", 2),
		
		(assign, "$pti_exchange_party", ":party"),
		(assign, "$pti_show_individual_members", 0),
		(assign, "$pti_show_individual_exchange_members", 0),
		(assign, "$pti_nps_selected_troop_id", "trp_player"),
		(assign, "$pti_nps_selected_exchange_troop_id", -1),
		(assign, "$pti_nps_selected_individual", -1),
		(assign, "$pti_nps_selected_prisoner_troop_id", -1),
		(start_presentation, "prsnt_new_party_screen"),
	]),
	
	# script_pti_open_party_screen
	("pti_open_party_screen",
	[
		(assign, "$pti_exchange_party", -1),
		(assign, "$pti_show_individual_members", 0),
		(assign, "$pti_show_individual_exchange_members", 0),
		(assign, "$pti_nps_selected_troop_id", "trp_player"),
		(assign, "$pti_nps_selected_exchange_troop_id", -1),
		(assign, "$pti_nps_selected_individual", -1),
		(assign, "$pti_nps_selected_prisoner_troop_id", -1),
		(start_presentation, "prsnt_new_party_screen"),
	]),
	
	# script_pti_nps_create_upper_left_stack_container
	("pti_nps_create_upper_left_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 29, 298, 262, 388),
		(assign, "$pti_nps_upper_left_container", reg1),
	]),
	
	# script_pti_nps_create_upper_right_stack_container
	("pti_nps_create_upper_right_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 685, 298, 262, 388),
		(assign, "$pti_nps_upper_right_container", reg1),
	]),
	
	# script_pti_nps_create_lower_left_stack_container
	("pti_nps_create_lower_left_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 29, 108, 262, 134),
		(assign, "$pti_nps_lower_left_container", reg1),
	]),
	
	# script_pti_nps_create_lower_right_stack_container
	("pti_nps_create_lower_right_stack_container",
	[
		(set_container_overlay, -1),
		
		(call_script, "script_gpu_create_scrollable_container", 685, 108, 262, 134),
		(assign, "$pti_nps_lower_right_container", reg1),
	]),
	
	# script_pti_container_get_overlay_mappings
	("pti_container_get_overlay_mappings",
	[
		(store_script_param, ":container", 1),
		
		(try_begin),
			(gt, ":container", -1),
			(eq, ":container", "$pti_nps_upper_left_container"),
			
			(assign, reg0, "trp_pti_nps_upper_left_button_overlays"),
			(assign, reg1, "trp_pti_nps_upper_left_highlight_overlays"),
			(assign, reg2, "trp_pti_nps_upper_left_text_overlays"),
			(assign, reg3, "trp_pti_nps_upper_left_image_overlays"),
			(assign, reg4, "trp_pti_nps_upper_left_troop_overlays"),
		(else_try),
			(gt, ":container", -1),
			(eq, ":container", "$pti_nps_upper_right_container"),
			
			(assign, reg0, "trp_pti_nps_upper_right_button_overlays"),
			(assign, reg1, "trp_pti_nps_upper_right_highlight_overlays"),
			(assign, reg2, "trp_pti_nps_upper_right_text_overlays"),
			(assign, reg3, "trp_pti_nps_upper_right_image_overlays"),
			(assign, reg4, "trp_pti_nps_upper_right_troop_overlays"),
		(else_try),
			(gt, ":container", -1),
			(eq, ":container", "$pti_nps_lower_left_container"),
			
			(assign, reg0, "trp_pti_nps_lower_left_button_overlays"),
			(assign, reg1, "trp_pti_nps_lower_left_highlight_overlays"),
			(assign, reg2, "trp_pti_nps_lower_left_text_overlays"),
			(assign, reg3, "trp_pti_nps_lower_left_image_overlays"),
			(assign, reg4, "trp_pti_nps_lower_left_troop_overlays"),
		(else_try),
			(gt, ":container", -1),
			(eq, ":container", "$pti_nps_lower_right_container"),
			
			(assign, reg0, "trp_pti_nps_lower_right_button_overlays"),
			(assign, reg1, "trp_pti_nps_lower_right_highlight_overlays"),
			(assign, reg2, "trp_pti_nps_lower_right_text_overlays"),
			(assign, reg3, "trp_pti_nps_lower_right_image_overlays"),
			(assign, reg4, "trp_pti_nps_lower_right_troop_overlays"),
		(else_try),
			(assign, reg0, ":container"),
			(display_log_message, "@ERROR: Called script_pti_container_get_overlay_mappings without a valid container (parameter passed: {reg0})", 0xFF000000),
			
			(assign, reg0, -1),
			(assign, reg1, -1),
			(assign, reg2, -1),
			(assign, reg3, -1),
			(assign, reg4, -1),
		(try_end),
	]),
	
	# script_pti_nps_add_stacks_to_container
	("pti_nps_add_stacks_to_container",
	[
		(store_script_param, ":container", 1),
		(store_script_param, ":num_stacks", 2),
		(store_script_param, ":stack_init_script", 3),
		(store_script_param, ":x_offset", 4),
		
		(call_script, "script_pti_container_get_overlay_mappings", ":container"),
		(assign, ":button_mapping", reg0),
		(assign, ":highlight_mapping", reg1),
		(assign, ":text_mapping", reg2),
		(assign, ":image_mapping", reg3),
		(assign, ":troop_mapping", reg4),
		
		(store_mul, ":cur_y", 26, ":num_stacks"),
		(try_for_range, ":i", 0, ":num_stacks"),
			(set_container_overlay, ":container"),
			
			#(display_message, s0),
			(val_sub, ":cur_y", 26),
			
			# Call script to set the associated stack object (e.g. a troop id) and string (e.g. troop name)
			(call_script, ":stack_init_script", ":i"),
			(assign, ":stack_object", reg0),
			(assign, ":image_troop", reg1),
			
			# Stack overlay
			(call_script, "script_gpu_create_image_button", mesh_party_member_button, mesh_party_member_button_pressed, ":x_offset", ":cur_y", 435),
			(assign, ":stack_button", reg1),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":stack_button", ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_containers", ":stack_button", ":container"),
			(troop_set_slot, ":button_mapping", ":stack_object", ":stack_button"),
			
			# Highlight overlay (initially invisible, made visible if stack highlighted)
			(call_script, "script_gpu_create_image_button", mesh_party_member_button_pressed, mesh_party_member_button_pressed, ":x_offset", ":cur_y", 435),
			(assign, ":highlight_button", reg1),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":highlight_button", ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_containers", ":highlight_button", ":container"),
			(troop_set_slot, ":highlight_mapping", ":stack_object", ":highlight_button"),
			#(overlay_set_color, ":highlight_button", 0x000088),
			(overlay_set_alpha, ":highlight_button", 0),
			#(overlay_set_display, ":highlight_button", 0),
			
			# Stack text
			(store_add, ":text_y", ":cur_y", 2),
			(store_add, ":text_x", ":x_offset", 100),
			(call_script, "script_gpu_create_text_overlay", "str_s0", ":text_x", ":text_y", 900, 262, 26, tf_center_justify),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", reg1, ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", reg1, 1),
			(troop_set_slot, "trp_pti_nps_overlay_containers", reg1, ":container"),
			(troop_set_slot, ":text_mapping", ":stack_object", reg1),
			
			# Troop image
			(set_container_overlay, -1),
			(call_script, "script_gpu_create_troop_image", ":image_troop", 330, 335, 1000),
			(overlay_set_display, reg1, 0),
			(troop_set_slot, ":image_mapping", ":stack_object", reg1),
			
			# Presentation troop
			(troop_set_slot, ":troop_mapping", ":stack_object", ":image_troop"),
		(try_end),
		
		(set_container_overlay, -1),
	]),
	
	# script_cf_pti_individual_is_selected
	("cf_pti_individual_is_selected",
	[
		(store_script_param, ":individual", 1),
		
		(eq, ":individual", "$pti_nps_selected_individual"),
	]),
	
	# script_cf_pti_prisoner_is_selected
	("cf_pti_prisoner_is_selected",
	[
		(store_script_param, ":troop_id", 1),
		
		(eq, ":troop_id", "$pti_nps_selected_prisoner_troop_id"),
	]),
	
	# script_cf_pti_exhange_troop_is_selected
	("cf_pti_exhange_troop_is_selected",
	[
		(store_script_param, ":troop_id", 1),
		
		(eq, ":troop_id", "$pti_nps_selected_exhange_troop_id"),
	]),
	
	# script_cf_pti_exhange_prisoner_is_selected
	("cf_pti_exhange_prisoner_is_selected",
	[
		(store_script_param, ":troop_id", 1),
		
		(eq, ":troop_id", "$pti_nps_selected_exhange_prisoner_troop_id"),
	]),
	
	# script_pti_nps_troop_stack_init
	("pti_nps_troop_stack_init",
	[
		(store_script_param, ":stack_no", 1),
		
		(party_stack_get_troop_id, ":troop_id", "$pti_nps_selected_party", ":stack_no"),
		(str_store_troop_name, s0, ":troop_id"),
		
		(try_begin),
			(neg|troop_is_hero, ":troop_id"),
			
			# Get the number of upgrades available (to later determine if + should be added to name)
			pti_count_individuals(party = "$pti_nps_selected_party", troop_id = ":troop_id", condition = "script_cf_pti_individual_is_upgradeable"),
			(assign, ":num_upgradeable", reg0),
			
			# Set up display troop as first individual of this troop type if not hero troop
			pti_get_first_individual(party = "$pti_nps_selected_party", troop_id = ":troop_id"),
			(assign, ":individual", "$pti_current_individual"),
			
			(call_script, "script_pti_equip_troop_as_individual", "$pti_current_individual_troop", ":individual"),
			(call_script, "script_pti_give_troop_individual_face", "$pti_current_individual_troop", ":individual"),
			
			(str_store_troop_name, s0, ":troop_id"),
			(try_begin),
				(party_stack_get_size, reg0, "$pti_nps_selected_party", ":stack_no"),
				(party_stack_get_num_wounded, reg1, "$pti_nps_selected_party", ":stack_no"),
				(gt, reg1, 0),
				
				(store_sub, reg2, reg0, reg1),
				(str_store_string, s0, "@{s0} ({reg2}/{reg0})"),
			(else_try),
				(str_store_string, s0, "@{s0} ({reg0})"),
			(try_end),
			
			(try_begin),
				(gt, ":num_upgradeable", 0),
				
				(str_store_string, s0, "@{s0} +"),
			(try_end),
			
			(assign, reg0, ":troop_id"),
			(assign, reg1, "$pti_current_individual_troop"),
		(else_try),
			(store_troop_health, reg0, ":troop_id"),
			(str_store_string, s0, "@{s0} ({reg0}%)"),
			
			(assign, reg0, ":troop_id"),
			(assign, reg1, ":troop_id"),
		(try_end),
		
		(val_add, "$pti_current_individual_troop", 1),
	]),
	
	# script_pti_nps_prisoner_stack_init
	("pti_nps_prisoner_stack_init",
	[
		(store_script_param, ":stack_no", 1),
		
		(party_prisoner_stack_get_troop_id, ":troop_id", "$pti_nps_selected_party", ":stack_no"),
		
		(str_store_troop_name, s0, ":troop_id"),
		(try_begin),
			(neg|troop_is_hero, ":troop_id"),
			
			(party_prisoner_stack_get_size, reg0, "$pti_nps_selected_party", ":stack_no"),
			(str_store_string, s0, "@{s0} ({reg0})"),
		(else_try),
			(store_troop_health, reg0, ":troop_id"),
			(str_store_string, s0, "@{s0} ({reg0}%)"),
		(try_end),
		
		(assign, reg0, ":troop_id"),
		(assign, reg1, ":troop_id"),
	]),
	
	# script_pti_nps_individual_stack_init
	("pti_nps_individual_stack_init",
	[
		(assign, ":curr_individual", "$pti_current_individual"),
		
		pti_get_next_individual(party = "$pti_nps_selected_party", troop_id = "$pti_nps_selected_stack_troop_id"),
		
		(call_script, "script_pti_set_up_individual_troop", ":curr_individual", "$pti_current_individual_troop"),
		
		(assign, ":upgradeable", 0),
		(try_begin),
			(call_script, "script_cf_pti_individual_is_upgradeable", ":curr_individual"),
			
			(assign, ":upgradeable", 1),
		(try_end),
		
		(call_script, "script_pti_individual_get_type_and_name", ":curr_individual"),
		(str_store_string_reg, s0, s1),
		(troop_set_name, "$pti_current_individual_troop", s0),
		
		(try_begin),
			Individual.get(":curr_individual", "is_wounded"),
			(eq, reg0, 1),
			
			(str_store_string, s0, "@{s0} (wounded)"),
		(try_end),
		
		(try_begin),
			(eq, ":upgradeable", 1),
			
			(str_store_string, s0, "@{s0} +"),
		(try_end),
		(assign, reg0, ":curr_individual"),
		(assign, reg1, "$pti_current_individual_troop"),
		
		(val_add, "$pti_current_individual_troop", 1),
	]),
	
	# script_pti_nps_select_stack
	("pti_nps_select_stack",
	[
		(store_script_param, ":stack_object", 1),
		(store_script_param, ":container", 2),
		
		(call_script, "script_pti_container_get_overlay_mappings", ":container"),
		(assign, ":highlight_mapping", reg1),
		(assign, ":image_mapping", reg3),
		
		# Show pressed stack overlay
		(troop_get_slot, ":highlight_button", ":highlight_mapping", ":stack_object"),
		#(overlay_set_display, ":highlight_button", 1),
		(overlay_set_alpha, ":highlight_button", 0xFF),
		
		# Hide previously shown troop image if applicable
		(try_begin),
			(gt, "$pti_nps_curr_troop_image", -1),
			
			(overlay_set_display, "$pti_nps_curr_troop_image", 0),
		(try_end),
		
		# Show selected object's image
		(troop_get_slot, ":troop_image", ":image_mapping", ":stack_object"),
		(overlay_set_display, ":troop_image", 1),
		(assign, "$pti_nps_curr_troop_image", ":troop_image"),
		
		# Set the title
		(try_begin),
			(assign, ":continue", 0),
			(try_begin),
				(eq, "$pti_show_individual_members", 1),
				(eq, ":container", "$pti_nps_individual_stack_container"),
				
				(assign, ":continue", 1),
			(else_try),
				(eq, "$pti_show_individual_exchange_members", 1),
				(eq, ":container", "$pti_nps_exchange_individual_stack_container"),
				
				(assign, ":continue", 1),
			(try_end),
			(eq, ":continue", 1),
			
			(call_script, "script_pti_individual_get_type_and_name", ":stack_object"),
			Individual.get(":stack_object", "home"),
			(str_store_party_name, s2, reg0),
			(overlay_set_text, "$pti_nps_title", "str_pti_name_format_name_of_home"),
		(else_try),
			(str_store_troop_name, s0, ":stack_object"),
			(overlay_set_text, "$pti_nps_title", "str_s0"),
		(try_end),
		
		# Set the weekly wages and morale text (will eventually be done separately for troops and individuals)
		(try_begin),
			(this_or_next|eq, ":container", "$pti_nps_individual_stack_container"),
			(eq, ":container", "$pti_nps_troop_stack_container"),
			
			(assign, ":troop_id", "$pti_nps_selected_troop_id"),
			(try_begin),
				(eq, ":container", "$pti_nps_troop_stack_container"),
				
				(assign, ":troop_id", ":stack_object"),
			(try_end),
			
			(gt, ":troop_id", 0),
			
			(call_script, "script_game_get_troop_wage", ":troop_id"),
			(store_sub, reg1, reg0, 1),	
			(str_store_string, s0, "@Weekly wage: {reg0} {reg1?denars:denar}"),
			(overlay_set_text, "$pti_nps_weekly_wages", "str_s0"),
			
			(call_script, "script_pti_troop_print_morale_description_to_s0", ":troop_id"),
			(str_store_string, s0, "@Morale: {s0}"),
			(overlay_set_text, "$pti_nps_morale", "str_s0"),
		(try_end),
		
		(assign, "$pti_nps_selected_stack_object", ":stack_object"),
		(assign, "$pti_nps_selected_stack_container", ":container"),
	]),
	
	# script_pti_nps_unselect_stack
	("pti_nps_unselect_stack",
	[
		(store_script_param, ":stack_object", 1),
		(store_script_param, ":container", 2),
		
		(call_script, "script_pti_container_get_overlay_mappings", ":container"),
		(assign, ":highlight_mapping", reg1),
		(assign, ":image_mapping", reg3),
		
		# Hide pressed stack overlay
		(troop_get_slot, ":highlight_button", ":highlight_mapping", ":stack_object"),
		#(overlay_set_display, ":highlight_button", 0),
		(overlay_set_alpha, ":highlight_button", 0),
		
		# Hide selected object's image
		(troop_get_slot, ":troop_image", ":image_mapping", ":stack_object"),
		(overlay_set_display, ":troop_image", 0),
		
		# Clear title
		(str_clear, s0),
		(overlay_set_text, "$pti_nps_title", "str_s0"),
		
		# Clear any individual text
		(try_begin),
			(gt, "$pti_nps_individual_summary", -1),
			
			(str_clear, s0),
			(overlay_set_text, "$pti_nps_individual_summary", "str_s0"),
		(try_end),
		
		# Clear the weekly wages and morale text
		(str_clear, s0),
		(overlay_set_text, "$pti_nps_weekly_wages", "str_s0"),
		
		(str_clear, s0),
		(overlay_set_text, "$pti_nps_morale", "str_s0"),
		
		# Hide the troop class overlays
		(overlay_set_display, "$pti_nps_troop_class_selector", 0),
		(overlay_set_display, "$pti_nps_troop_class_rename_button", 0),
		
		# Hide the upgrade buttons
		(try_begin),
			(gt, "$pti_nps_upgrade_button_1", -1),
			
			(overlay_set_display, "$pti_nps_upgrade_button_1", 0),
			
			(gt, "$pti_nps_upgrade_button_2", -1),
			(overlay_set_display, "$pti_nps_upgrade_button_2", 0),
		(try_end),
	]),
	
	# script_pti_nps_get_selected_class
	("pti_nps_get_selected_class",
	[
		(try_begin),
			(eq, "$pti_show_individual_members", 1),
			(gt, "$pti_nps_selected_individual_id", -1),
			
			Individual.get("$pti_nps_selected_individual", "class_overridden"),
			(try_begin),
				(eq, reg0, 1),
				
				Individual.get("$pti_nps_selected_individual", "class"),
				(assign, ":class", reg0),
			(else_try),
				(assign, ":class", grc_everyone),
			(try_end),
		(else_try),
			(gt, "$pti_nps_selected_troop_id", 0),
			
			(troop_get_class, ":class", "$pti_nps_selected_troop_id"),
		(else_try),
			(assign, ":class", -1),
		(try_end),
		
		(assign, reg0, ":class"),
	]),
	
	# script_pti_nps_refresh_troop_class
	("pti_nps_refresh_troop_class",
	[
		(call_script, "script_pti_nps_get_selected_class"),
		(try_begin),
			(gt, reg0, -1),
			
			(overlay_set_display, "$pti_nps_troop_class_selector", 1),
			(overlay_set_val, "$pti_nps_troop_class_selector", reg0),
			
			# Only show the rename button for actual troop classes (i.e. not for "Default")
			(this_or_next|eq, "$pti_show_individual_members", 0),
			(neq, reg0, grc_everyone),
			
			(overlay_set_display, "$pti_nps_troop_class_rename_button", 1),
		(try_end),
	]),
	
	# script_pti_nps_refresh_text
	("pti_nps_refresh_text",
	[
		# Troop type
		Individual.get("$pti_nps_selected_individual", "troop_type"),
		(str_store_troop_name, s10, reg0),
		
		# Home
		Individual.get("$pti_nps_selected_individual", "home"),
		(str_store_party_name, s0, reg0),
		(str_store_string, s10, "@{s10} from {s0}"),
		
		# Age
		Individual.get("$pti_nps_selected_individual", "age"),
		(val_mul, reg0, 2),
		(val_div, reg0, 3),
		(val_add, reg0, 16),
		(str_store_string, s10, "@{s10}^{reg0} years old"),
		
		# Days of service
		(store_current_day, ":days_in_party"),
		Individual.get("$pti_nps_selected_individual", "day_joined"),
		(val_sub, ":days_in_party", reg0),
		(assign, reg0, ":days_in_party"),
		(str_store_string, s10, "@{s10}^Has been in service for {reg0} days"),
		
		# Battle stats
		Individual.get("$pti_nps_selected_individual", "kill_count"),
		(str_store_string, s10, "@{s10}^Number of enemies killed: {reg0}"),
		
		Individual.get("$pti_nps_selected_individual", "knock_out_count"),
		(str_store_string, s10, "@{s10}^Number of enemies knocked out: {reg0}"),
		
		Individual.get("$pti_nps_selected_individual", "most_kills"),
		(str_store_string, s10, "@{s10}^Most enemies killed in one battle: {reg0}"),
		
		Individual.get("$pti_nps_selected_individual", "best_kill"),
		(try_begin),
			(gt, reg0, 0),
			
			(str_store_troop_name, s0, reg0),
			(str_store_string, s10, "@{s10}^Best kill: {s0}"),
		(try_end),
		
		Individual.get("$pti_nps_selected_individual", "times_wounded"),
		(str_store_string, s10, "@{s10}^Number of times wounded: {reg0}"),
		
		Individual.get("$pti_nps_selected_individual", "train_troops_quest"),
		(try_begin),
			(eq, reg0, 1),
			
			(quest_get_slot, ":giver_troop", "qst_raise_troops", slot_quest_giver_troop),
			(quest_get_slot, ":target_troop", "qst_raise_troops", slot_quest_target_troop),
			(str_store_troop_name, s0, ":giver_troop"),
			(str_store_troop_name, s1, ":target_troop"),
			(str_store_string, s10, "@{s10}^^Is to be returned to {s0} upon being trained to the level of {s1}"),
		(try_end),
		
		# XP
		Individual.get("$pti_nps_selected_individual", "xp"),
		(str_store_string, s10, "@{s10}^XP: {reg0}"),
		(call_script, "script_pti_level_given_xp", reg0),
		(str_store_string, s10, "@{s10}^Level: {reg0}"),
		
		# Finish
		(str_store_string_reg, s0, s10),
		(overlay_set_text, "$pti_nps_individual_summary", "str_s0"),
	]),
	
	# script_pti_nps_create_individual_upgrade_buttons
	("pti_nps_create_individual_upgrade_buttons",
	[
		(str_clear, s0),
		
		(call_script, "script_gpu_create_in_game_button_overlay", "str_s0", 500, 300),
		(assign, "$pti_nps_upgrade_button_1", reg1),
		(overlay_set_display, "$pti_nps_upgrade_button_1", 0),
		
		(call_script, "script_gpu_create_in_game_button_overlay", "str_s0", 500, 250),
		(assign, "$pti_nps_upgrade_button_2", reg1),
		(overlay_set_display, "$pti_nps_upgrade_button_2", 0),
	]),
	
	# script_pti_nps_refresh_individual_upgrade_buttons
	("pti_nps_refresh_individual_upgrade_buttons",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "troop_type"),
		(assign, ":troop_id", reg0),
		
		(try_begin),
			(troop_get_upgrade_troop, ":upgrade", ":troop_id", 0),
			(gt, ":upgrade", 0),
			
			(overlay_set_display, "$pti_nps_upgrade_button_1", 1),
			
			(str_store_troop_name, s0, ":upgrade"),
			(str_store_string, s0, "@Upgrade to {s0}"),
			(overlay_set_text, "$pti_nps_upgrade_button_1", "str_s0"),
			(try_begin),
				(call_script, "script_cf_pti_individual_can_upgrade_to", ":individual", ":upgrade"),
				
				(overlay_set_alpha, "$pti_nps_upgrade_button_1", 0xFF),
			(else_try),
				(overlay_set_alpha, "$pti_nps_upgrade_button_1", 0x44),
			(try_end),
			#(call_script, "script_gpu_overlay_set_size", "$pti_nps_upgrade_button_1", 250, 25),
		(else_try),
			(overlay_set_display, "$pti_nps_upgrade_button_1", 0),
		(try_end),
		
		(try_begin),
			(troop_get_upgrade_troop, ":upgrade", ":troop_id", 1),
			(gt, ":upgrade", 0),
			
			(overlay_set_display, "$pti_nps_upgrade_button_2", 1),
			
			(str_store_troop_name, s0, ":upgrade"),
			(str_store_string, s0, "@Upgrade to {s0}"),
			(overlay_set_text, "$pti_nps_upgrade_button_2", "str_s0"),
			(try_begin),
				(call_script, "script_cf_pti_individual_can_upgrade_to", ":individual", ":upgrade"),
				
				(overlay_set_alpha, "$pti_nps_upgrade_button_2", 0xFF),
			(else_try),
				(overlay_set_alpha, "$pti_nps_upgrade_button_2", 0x44),
			(try_end),
		(else_try),
			(overlay_set_display, "$pti_nps_upgrade_button_2", 0),
		(try_end),
	]),
	
]

def operation_matches(operation, *args):
	matches = type(operation) == tuple
	if matches:
		for i, arg in enumerate(args):
			matches = len(operation) > i and (arg == "?" or operation[i] == arg)
			if not matches:
				break
	
	return matches

def merge(scripts):
	scripts.extend(new_scripts)
	
	# Update village recruitment to add individuals
	try:
		add_troops_op = [operation for operation in scripts["village_recruit_volunteers_recruit"].operations if operation[0] == party_add_members][0]
		index = scripts["village_recruit_volunteers_recruit"].operations.index(add_troops_op)
		volunteer_troop = add_troops_op[2]
		volunteer_amount = add_troops_op[3]
		scripts["village_recruit_volunteers_recruit"].operations[index] = (call_script, "script_pti_recruit_troops_from_center", "p_main_party", volunteer_troop, "$current_town", volunteer_amount)
	except IndexError:
		raise ValueError("Could not find party_add_members operation in script_village_recruit_volunteers_recruit")
	
	# Ensure wound treatment is applied to individuals on party encounter, to prevent starting a battle with individual healing lagging behind party troops
	scripts["game_event_party_encounter"].operations.append((call_script, "script_pti_apply_wound_treatment_to_individuals", "p_main_party"))
	
	count_casualties_operations = scripts["count_mission_casualties_from_agents"].operations
	indexes = [i for i, operation in enumerate(count_casualties_operations) if operation_matches(operation, agent_get_troop_id)]
	for index in reversed(indexes):
		troop_id = count_casualties_operations[index][1]
		count_casualties_operations[index+1:index+1] = [
			(try_begin),
				(troop_get_slot, reg0, troop_id, pti_slot_troop_regular_troop_type),
				(gt, reg0, 0),
				
				#(str_store_troop_name, s0, troop_id),
				#(str_store_troop_name, s1, reg0),
				#(display_message, "@Replacing {s0} with {s1}"),
				
				(assign, troop_id, reg0),
			(try_end),
		]