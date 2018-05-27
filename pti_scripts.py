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
		(call_script, "script_pti_linked_list_init"),
		(party_set_slot, "p_main_party", pti_slot_party_individuals, reg0),
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
			(call_script, "script_pti_array_get", "$pti_individuals_array", ":individual", ":value"),
		(else_try),
			(assign, reg0, ":value"),
			(assign, reg1, ":bitmask"),
			(display_log_message, "@ERROR: Tried to add value of {reg0} to attribute for which the maximum value is {reg1}", 0xFF0000),
		(try_end),
	]),
	
	## INDIVIDUAL ITERATION AND COUNTING SCRIPTS
	
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
	
	# script_pti_create_individual
	("pti_create_individual",
	[
		(party_get_slot, ":size", "$pti_individuals_array", pti_slot_array_size),
		(val_add, ":size", Individual.num_attribute_slots),
		(party_set_slot, "$pti_individuals_array", pti_slot_array_size, ":size"),
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
	
]

def merge(scripts):
	for i, operation in enumerate(scripts["village_recruit_volunteers_recruit"].operations):
		if operation[0] == party_add_members:
			scripts["village_recruit_volunteers_recruit"].operations[i] = (call_script, "script_pti_hire_troops_from_fief", operation[1], operation[2], operation[3], "$current_town")
	
	scripts.extend(new_scripts)
