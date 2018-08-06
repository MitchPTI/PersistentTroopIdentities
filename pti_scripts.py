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
				(faction_set_slot, faction, pti_slot_faction_boy_names_begin, "str_{}_{}_name_1".format(faction, "boy"))
				, (faction_set_slot, faction, pti_slot_faction_boy_names_end, "str_{}_{}_names_end".format(faction, "boy"))
				, (faction_set_slot, faction, pti_slot_faction_girl_names_begin, "str_{}_{}_name_1".format(faction, "girl"))
				, (faction_set_slot, faction, pti_slot_faction_girl_names_end, "str_{}_{}_names_end".format(faction, "girl"))
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
		(assign, "$pti_individual_name_format", "str_pti_name_format_troop_type_name"),
	]),
	
	## ARRAY SCRIPTS
	
	("pti_array_init",
	[
		(spawn_around_party, "p_main_party", "pt_none"),
		(disable_party, reg0),
	]),
	
	("pti_array_get",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index", 2),
		
		(store_add, ":slot", pti_array_slots_start, ":index"),
		(try_begin),
			(ge, ":slot", pti_array_slot_max),
			
			(party_get_slot, ":array", ":array", pti_slot_array_next_array),
			(try_begin),
				(gt, ":array", 0),
				
				(val_sub, ":slot", pti_array_slot_max),
				(call_script, "script_pti_array_get", ":array", ":slot"),
			(else_try),
				(display_log_message, "@ERROR: Tried to get array value from next array, but none found", 0xFF0000),
				(assign, reg0, -1),
			(try_end),
		(else_try),
			(party_get_slot, reg0, ":array", ":slot"),
		(try_end),
	]),
	
	("pti_array_set",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
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
	]),
	
	("pti_array_append",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":value", 2),
		
		(party_get_slot, ":index", ":array", pti_slot_array_size),
		(call_script, "script_pti_array_set", ":array", ":index", ":value"),
		(store_add, ":size", ":index", 1),
		(party_set_slot, ":array", pti_slot_array_size, ":size"),
	]),
	
	("pti_array_swap",
	[
		(store_script_param, ":array", 1),
		(store_script_param, ":index_1", 2),
		(store_script_param, ":index_2", 3),
		
		(call_script, "script_pti_array_get", ":array", ":index_1"),
		(assign, ":element_1", reg0),
		(call_script, "script_pti_array_get", ":array", ":index_2"),
		(assign, ":element_2", reg0),
		
		(call_script, "script_pti_array_set", ":array", ":index_1", ":element_2"),
		(call_script, "script_pti_array_set", ":array", ":index_2", ":element_1"),
	]),
	
	## LINKED LIST SCRIPTS
	
	("pti_linked_list_init",
	[
		(call_script, "script_pti_array_init"),
	]),
	
	("pti_linked_list_get_node",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
		(call_script, "script_pti_array_get", ":list", ":index"),
		(assign, ":node", reg0),
		(call_script, "script_pti_array_get", ":list", ":index"),
		(store_and, reg0, ":node", pti_list_node_value_mask),
		
		(val_rshift, ":node", pti_list_next_node_bitshift),
		(store_and, reg1, ":node", pti_list_node_mask),
		
		(val_rshift, ":node", pti_list_node_bits),
		(store_and, reg2, ":node", pti_list_node_mask),
		
		(assign, reg3, ":index"),
		#(display_message, "@Index: {reg3} | Value: {reg0} | Next index: {reg1} | Prev index: {reg2}"),
	]),
	
	("pti_linked_list_get_head_node",
	[
		(store_script_param, ":list", 1),
		
		(party_get_slot, ":head_index", ":list", pti_slot_list_head),
		(call_script, "script_pti_linked_list_get_node", ":list", ":head_index"),
	]),
	
	("pti_linked_list_get_tail_node",
	[
		(store_script_param, ":list", 1),
		
		(party_get_slot, ":head_index", ":list", pti_slot_list_head),
		(call_script, "script_pti_linked_list_get_node", ":list", ":head_index"),
		(call_script, "script_pti_linked_list_get_node", ":list", reg2),
	]),
	
	("pti_linked_list_get_first_index_meeting_condition_r",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":condition_script", 2),
		(store_script_param, ":index", 3),
		
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(try_begin),
			(call_script, ":condition_script", reg0),
			
			(assign, reg0, reg3),
		(else_try),
			(neg|party_slot_eq, ":list", pti_slot_list_head, reg1),
			
			(call_script, "script_pti_linked_list_get_first_index_meeting_condition_r", ":list", ":condition_script", reg1),
		(else_try),
			(assign, reg0, -1),
		(try_end),
	]),
	
	("pti_linked_list_get_last_index_meeting_condition_r",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":condition_script", 2),
		(store_script_param, ":index", 3),
		
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(try_begin),
			(call_script, ":condition_script", reg0),
			
			(assign, reg0, reg3),
		(else_try),
			(neg|party_slot_eq, ":list", pti_slot_list_head, ":index"),
			
			(call_script, "script_pti_linked_list_get_last_index_meeting_condition_r", ":list", ":condition_script", reg2),
		(else_try),
			(assign, reg0, -1),
		(try_end),
	]),
	
	("pti_linked_list_count",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":condition_script", 2),
		
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
	]),
	
	("pti_node_set_prev",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":prev", 2),
		
		(val_and, reg0, pti_list_prev_node_clear_mask),
		(val_lshift, ":prev", pti_list_prev_node_bitshift),
		(val_or, reg0, ":prev"),
	]),
	
	("pti_node_set_next",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":next", 2),
		
		(val_and, reg0, pti_list_next_node_clear_mask),
		(val_lshift, ":next", pti_list_next_node_bitshift),
		(val_or, reg0, ":next"),
	]),
	
	("pti_node_set_value",
	[
		(store_script_param, reg0, 1),
		(store_script_param, ":value", 2),
		
		(val_and, reg0, pti_list_node_value_clear_mask),
		(val_or, reg0, ":value"),
	]),
	
	("pti_linked_list_set_prev",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":prev", 3),
		
		(call_script, "script_pti_array_get", ":list", ":index"),
		(call_script, "script_pti_node_set_prev", reg0, ":prev"),
		(call_script, "script_pti_array_set", ":list", ":index", reg0),
	]),
	
	("pti_linked_list_set_next",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":next", 3),
		
		(call_script, "script_pti_array_get", ":list", ":index"),
		(call_script, "script_pti_node_set_next", reg0, ":next"),
		(call_script, "script_pti_array_set", ":list", ":index", reg0),
	]),
	
	("pti_linked_list_set_value",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(call_script, "script_pti_array_get", ":list", ":index"),
		(call_script, "script_pti_node_set_value", reg0, ":value"),
		(call_script, "script_pti_array_set", ":list", ":index", reg0),
	]),
	
	("pti_linked_list_insert_before",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(party_get_slot, ":new_index", ":list", pti_slot_array_size),
		
		# Get the neighbour nodes that will be modified to accommodate the new node (in this case current and previous)
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(assign, ":next_index", reg1),
		(assign, ":prev_index", reg2),
		
		# Modify the neighbour nodes to point to the new node
		(call_script, "script_pti_linked_list_set_next", ":list", ":prev_index", ":new_index"),
		(call_script, "script_pti_linked_list_set_prev", ":list", ":index", ":new_index"),
		
		# Create the new node
		(val_lshift, ":next_index", pti_list_next_node_bitshift),
		(val_or, ":value", ":next_index"),
		(val_lshift, ":prev_index", pti_list_prev_node_bitshift),
		(val_or, ":value", ":prev_index"),
		(call_script, "script_pti_array_append", ":list", ":value"),
		
		# If inserting before the head node, make this the new head node
		(try_begin),
			(party_slot_eq, ":list", pti_slot_list_head, ":index"),
			
			(party_set_slot, ":list", pti_slot_list_head, ":new_index"),
			#(assign, reg0, ":new_index"),
			#(display_message, "@Setting head to index {reg0}"),
		(try_end),
	]),
	
	("pti_linked_list_insert_after",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":value", 3),
		
		(party_get_slot, ":new_index", ":list", pti_slot_array_size),
		
		# Get the neighbour nodes that will be modified to accommodate the new node (in this case current and next)
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(assign, ":next_index", reg1),
		
		# Modify the neighbour nodes to point to the new node
		(call_script, "script_pti_linked_list_set_next", ":list", ":index", ":new_index"),
		(call_script, "script_pti_linked_list_set_prev", ":list", ":next_index", ":new_index"),
		
		# Create the new node
		(val_lshift, ":next_index", pti_list_next_node_bitshift),
		(val_or, ":value", ":next_index"),
		(val_lshift, ":index", pti_list_prev_node_bitshift),
		(val_or, ":value", ":index"),
		(call_script, "script_pti_array_append", ":list", ":value"),
	]),
	
	("pti_linked_list_append",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":value", 2),
		
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
	]),
	
	# WARNING: This will overwrite whatever exists at the new index, it is only intended for use in script_pti_linked_list_remove
	("pti_linked_list_copy_node",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":new_index", 3),
		
		# Point the neighbours at the new index
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(assign, ":next", reg1),
		(assign, ":prev", reg2),
		
		(call_script, "script_pti_linked_list_set_next", ":list", ":prev", ":new_index"),
		(call_script, "script_pti_linked_list_set_prev", ":list", ":next", ":new_index"),
		
		# Overwrite the new index
		(call_script, "script_pti_array_get", ":list", ":index"),
		(call_script, "script_pti_array_set", ":list", ":new_index", reg0),
	]),
	
	("pti_linked_list_swap",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index_1", 2),
		(store_script_param, ":index_2", 3),
		
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
	]),
	
	("pti_linked_list_swap_with_next",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
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
	]),
	
	("pti_linked_list_swap_with_prev",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		
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
	]),
	
	("pti_linked_list_move_before",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":index", 2),
		(store_script_param, ":dest_index", 3),
		
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
	]),
	
	("pti_linked_list_remove",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":object", 2),
		
		(call_script, "script_pti_linked_list_get_head_node", ":list"),
		(assign, ":curr_obj", reg0),
		(assign, ":next", reg1),
		(assign, ":prev", reg2),
		(assign, ":curr_index", reg3),
		
		(assign, ":index", -1),
		(party_get_slot, ":size", ":list", pti_slot_array_size),
		(try_for_range, ":unused", 0, ":size"),
			(eq, ":curr_obj", ":object"),
			
			(assign, ":index", ":curr_index"),
			(assign, ":size", 0),
		(else_try),
			(call_script, "script_pti_linked_list_get_node", ":list", ":next"),
			(assign, ":curr_obj", reg0),
			(assign, ":next", reg1),
			(assign, ":prev", reg2),
			(assign, ":curr_index", reg3),
		(try_end),
		
		(try_begin),
			(gt, ":index", -1),
			
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
		(else_try),
			(display_message, "@ERROR: Tried to remove {reg0} from list (ID: {reg1}), but {reg0} could not be found in the list", 0xFF0000),
		(try_end),
	]),
	
	("pti_linked_list_get_nth_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":n", 2),
		
		(call_script, "script_pti_linked_list_get_head_node", ":list"),
		(try_for_range, ":unused", 0, ":n"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg1),
		(try_end),
		
		(assign, reg0, reg3),
	]),
	
	("pti_linked_list_get_nth_index_after_index",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":n", 2),
		(store_script_param, ":index", 3),
		
		(call_script, "script_pti_linked_list_get_node", ":list", ":index"),
		(try_for_range, ":unused", 0, ":n"),
			(call_script, "script_pti_linked_list_get_node", ":list", reg1),
		(try_end),
		
		(assign, reg0, reg3),
	]),
	
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
	
	("pti_linked_list_merge_sort",
	[
		(store_script_param, ":list", 1),
		(store_script_param, ":comparison_script", 2),
		
		(party_get_slot, ":size", ":list", pti_slot_array_size),
		(val_sub, ":size", 1),
		(call_script, "script_pti_linked_list_merge_sort_r", ":list", ":comparison_script", 0, ":size"),
	]),
	
	("cf_pti_gt",
	[
		(store_script_param, ":value_1", 1),
		(store_script_param, ":value_2", 2),
		
		(gt, ":value_1", ":value_2"),
	]),
	
	## INDIVIDUAL CREATION AND ADDITION TO PARTY SCRIPTS
	
	# script_pti_create_individual
	("pti_create_individual",
	[
		(party_get_slot, reg0, "$pti_individuals_array", pti_slot_array_size),
		(store_add, ":size", reg0, Individual.num_attribute_slots),
		(party_set_slot, "$pti_individuals_array", pti_slot_array_size, ":size"),
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
		
		(assign, reg0, ":individual"),
	]),
	
	# script_pti_add_individual_to_party
	("pti_add_individual_to_party",
	[
		(store_script_param, ":individual", 1),
		(store_script_param, ":party", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(call_script, "script_pti_linked_list_append", ":list", ":individual"),
		Individual.get(":individual", "troop_type"),
		(party_add_members, ":party", reg0, 1),
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
			(call_script, "script_pti_add_individual_to_party", ":individual", ":dest_party"),
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
			
			(val_lshift, ":value", ":bitshift"),
			
			(val_add, ":individual", ":offset"),
			(call_script, "script_pti_array_get", "$pti_individuals_array", ":individual"),
			(val_and, reg0, ":clear_mask"),
			(val_or, reg0, ":value"),
			(call_script, "script_pti_array_set", "$pti_individuals_array", ":individual", reg0),
		(else_try),
			(assign, reg0, ":value"),
			(assign, reg1, ":bitmask"),
			(display_log_message, "@ERROR: Tried to add value of {reg0} to attribute for which the maximum value is {reg1}", 0xFF0000),
		(try_end),
	]),
	
	## INDIVIDUAL ITERATION AND COUNTING SCRIPTS
	
	# script_pti_party_get_num_individuals
	("pti_party_get_num_individuals",
	[
		(store_script_param, ":party", 1),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_slot, reg0, ":list", pti_slot_array_size),
	]),
	
	# script_pti_get_first_individual
	("pti_get_first_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_slot, ":head", ":list", pti_slot_list_head),
		(call_script, "script_pti_linked_list_get_first_index_meeting_condition_r", ":list", ":condition_script", ":head"),
		(try_begin),
			(neq, reg0, -1),
			
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_current_individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
		(try_end),
	]),
	
	# script_pti_get_next_individual
	("pti_get_next_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(call_script, "script_pti_linked_list_get_first_index_meeting_condition_r", ":list", ":condition_script", "$pti_next_individual_index"),
		(try_begin),
			(neq, reg0, -1),
			
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_current_individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
		(try_end),
	]),
	
	# script_pti_get_last_individual
	("pti_get_last_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(party_get_slot, ":head", ":list", pti_slot_list_head),
		(call_script, "script_pti_linked_list_get_last_index_meeting_condition_r", ":list", ":condition_script", ":head"),
		(try_begin),
			(neq, reg0, -1),
			
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_current_individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
		(try_end),
	]),
	
	# script_pti_get_prev_individual
	("pti_get_prev_individual",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(call_script, "script_pti_linked_list_get_last_index_meeting_condition_r", ":list", ":condition_script", "$pti_prev_individual_index"),
		(try_begin),
			(neq, reg0, -1),
			
			(call_script, "script_pti_linked_list_get_node", ":list", reg0),
			(assign, "$pti_current_individual", reg0),
			(assign, "$pti_next_individual_index", reg1),
			(assign, "$pti_prev_individual_index", reg2),
		(try_end),
	]),
	
	# script_pti_count_individuals
	("pti_count_individuals",
	[
		(store_script_param, ":party", 1),
		(store_script_param, ":condition_script", 2),
		
		(party_get_slot, ":list", ":party", pti_slot_party_individuals),
		(call_script, "script_pti_linked_list_count", ":list", ":condition_script"),
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
		(eq, reg0, "$pti_nps_selected_troop_id"),
	]),
	
	# script_cf_pti_individual_is_wounded
	("cf_pti_individual_is_wounded",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_wounded"),
		(eq, reg0, 1),
	]),
	
	# script_cf_pti_individual_is_not_wounded
	("cf_pti_individual_is_not_wounded",
	[
		(store_script_param, ":individual", 1),
		
		Individual.get(":individual", "is_wounded"),
		(eq, reg0, 0),
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
		(store_random_in_range, ":age", 0, 64),
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
		
		# Start with empty face keys (such as found on temp troop)
		(str_store_troop_face_keys, s0, "trp_pti_nps_presentation_troop"),
		
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
		
		(assign, ":max_slot", 0),
		(assign, ":type_count", 0),
		(assign, ":end_cond", max_inventory_items),
		(try_for_range, ":slot", 0, max_inventory_items),
			(troop_get_inventory_slot, ":item", ":troop_id", ":slot"),
			(gt, ":item", 0),
			
			(assign, ":max_slot", ":slot"),
			
			(try_begin),
				(item_get_type, ":curr_type", ":item"),
				(eq, ":curr_type", ":item_type"),
				
				(val_add, ":type_count", 1),
			(try_end),
			
		(else_try),
			(assign, ":end_cond", 0),
		(try_end),
		
		(try_begin),
			(gt, ":type_count", 0),
			
			(store_random_in_range, ":item_num", 0, ":type_count"),
			(assign, ":type_count", 0),
			(assign, ":end_cond", ":max_slot"),
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
			(eq, ":troop_id", "trp_pti_nps_presentation_troop"),
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
	
	## BATTLE SCRIPTS ##
	
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
		
		(call_script, "script_pti_troop_copy_stats", ":troop_type", ":troop_id"),
		(call_script, "script_pti_equip_troop_as_individual", ":troop_id", ":individual"),
		(call_script, "script_pti_give_troop_individual_face", ":troop_id", ":individual"),
		
		(troop_set_slot, ":troop_id", pti_slot_troop_individual, ":individual"),
	]),
	
	# script_pti_individual_agent_process_battle
	("pti_individual_agent_process_battle",
	[
		(store_script_param, ":agent", 1),
		
		(agent_get_slot, ":individual", ":agent", pti_slot_agent_individual),
		
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
		(store_script_param, ":killer_agent", 2),
		(store_script_param, ":wounded", 3),
		
		(agent_get_slot, ":individual", ":agent", pti_slot_agent_individual),
		
		(call_script, "script_pti_individual_get_type_and_name", ":individual"),
		(assign, reg0, ":agent"),
		(assign, reg1, ":individual"),
		(display_message, "@Processing casualty of {s0} {s1}. Agent ID: {reg0} | Individual ID: {reg1}"),
		
		(try_begin),
			(eq, ":wounded", 1),
			
			(call_script, "script_pti_individual_agent_process_battle", ":agent"),
			
			Individual.set(":individual", "is_wounded", 1),
			Individual.get(":individual", "times_wounded"),
			(val_add, reg0, 1),
			Individual.set(":individual", "times_wounded", reg0),
		(else_try),
			(party_get_slot, ":list", "p_main_party", pti_slot_party_individuals),
			(call_script, "script_pti_linked_list_remove", ":list", ":individual"),
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
	
	# script_pti_restore_main_party
	("pti_restore_main_party",
	[
		(party_clear, "p_main_party"),
		
		(call_script, "script_pti_count_individuals", "p_main_party", "script_cf_pti_true"),
		(assign, ":count", reg0),
		
		(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_true"),
		(try_for_range, ":unused", 0, ":count"),
			Individual.get("$pti_current_individual", "troop_type"),
			(assign, ":troop_id", reg0),
			(party_add_members, "p_main_party", ":troop_id", 1),
			
			Individual.get("$pti_current_individual", "is_wounded"),
			(try_begin),
				(eq, reg0, 1),
				
				(party_wound_members, "p_main_party", ":troop_id", 1),
			(try_end),
			
			(call_script, "script_pti_get_next_individual", "p_main_party", "script_cf_pti_true"),
		(try_end),
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
		(store_script_param, ":x_offset", 4),
		
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
			(troop_set_slot, "trp_pti_nps_stack_button_overlays", ":stack_object", ":stack_button"),
			
			# Highlight overlay (initially invisible, made visible if stack highlighted)
			(call_script, "script_gpu_create_image_button", mesh_party_member_button_pressed, mesh_party_member_button_pressed, ":x_offset", ":cur_y", 435),
			(assign, ":highlight_button", reg1),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":highlight_button", ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_containers", ":highlight_button", ":container"),
			(troop_set_slot, "trp_pti_nps_stack_button_highlight_overlays", ":stack_object", ":highlight_button"),
			#(overlay_set_color, ":highlight_button", 0x000088),
			#(overlay_set_alpha, ":highlight_button", 0x44),
			(overlay_set_display, ":highlight_button", 0),
			
			# Stack text
			(store_add, ":text_y", ":cur_y", 2),
			(store_add, ":text_x", ":x_offset", 100),
			(call_script, "script_gpu_create_text_overlay", "str_s0", ":text_x", ":text_y", 900, 262, 26, tf_center_justify),
			(troop_set_slot, "trp_pti_nps_overlay_stack_objects", reg1, ":stack_object"),
			(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", reg1, 1),
			(troop_set_slot, "trp_pti_nps_overlay_containers", reg1, ":container"),
			(troop_set_slot, "trp_pti_nps_stack_object_text_overlays", ":stack_object", reg1),
			
			# Troop image
			(set_container_overlay, -1),
			(call_script, "script_gpu_create_troop_image", ":image_troop", 350, 325, 1000),
			(overlay_set_display, reg1, 0),
			(troop_set_slot, "trp_pti_nps_stack_object_troop_images", ":stack_object", reg1),
		(try_end),
		
		(set_container_overlay, -1),
	]),
	
	# script_cf_pti_troop_is_selected
	("cf_pti_troop_is_selected",
	[
		(store_script_param, ":troop_id", 1),
		
		(eq, ":troop_id", "$pti_nps_selected_troop_id"),
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
		(assign, reg1, ":troop_id"),
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
		(assign, reg1, ":troop_id"),
	]),
	
	# script_pti_nps_individual_stack_init
	("pti_nps_individual_stack_init",
	[
		(assign, ":curr_individual", "$pti_current_individual"),
		
		(call_script, "script_pti_get_next_individual", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
		
		(call_script, "script_pti_equip_troop_as_individual", "trp_pti_nps_presentation_troop", ":curr_individual"),
		(call_script, "script_pti_give_troop_individual_face", "trp_pti_nps_presentation_troop", ":curr_individual"),
		
		(call_script, "script_pti_individual_get_type_and_name", ":curr_individual"),
		(str_store_string_reg, s0, s1),
		(assign, reg0, ":curr_individual"),
		(assign, reg1, "trp_pti_nps_presentation_troop"),
	]),
	
]

def merge(scripts):
	scripts.extend(new_scripts)
	
	try:
		add_troops_op = [operation for operation in scripts["village_recruit_volunteers_recruit"].operations if operation[0] == party_add_members][0]
	except IndexError:
		raise ValueError("Could not find party_add_members operation in script_village_recruit_volunteers_recruit")
	
	index = scripts["village_recruit_volunteers_recruit"].operations.index(add_troops_op)
	volunteer_troop = add_troops_op[2]
	volunteer_amount = add_troops_op[3]
	scripts["village_recruit_volunteers_recruit"].operations[index] = (call_script, "script_pti_recruit_troops_from_center", "p_main_party", volunteer_troop, "$current_town", volunteer_amount)
