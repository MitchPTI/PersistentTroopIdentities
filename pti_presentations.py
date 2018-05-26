from header_common import *
from header_presentations import *
from header_mission_templates import *
from ID_meshes import *
from header_operations import *
from header_triggers import *
from module_constants import *
import string

####################################################################################################################
#	Each presentation record contains the following fields:
#	1) Presentation id: used for referencing presentations in other files. The prefix prsnt_ is automatically added before each presentation id.
#	2) Presentation flags. See header_presentations.py for a list of available flags
#	3) Presentation background mesh: See module_meshes.py for a list of available background meshes
#	4) Triggers: Simple triggers that are associated with the presentation
####################################################################################################################

STACK_X_OFFSET = 30

presentations = [
	
	("new_party_screen", 0, mesh_party_window_b,
	[
		(ti_on_presentation_load,
		[
			(try_for_range, ":slot", 0, 99999),
				(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_containers", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_stack_object_text_overlays", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":slot", 0),
				(troop_slot_eq, "trp_pti_nps_overlay_is_stack_button", ":slot", 0),
			(try_end),
			
			(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
			(call_script, "script_pti_nps_create_upper_right_stack_container"),
			(assign, "$pti_nps_troop_stack_container", reg1),
			(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_troop_stack_container", ":num_stacks", "script_pti_nps_troop_stack_init", "script_cf_pti_troop_is_selected", STACK_X_OFFSET),
			
			(call_script, "script_pti_count_individuals", "script_cf_pti_individual_is_of_selected_troop"),
			(assign, ":num_individuals", reg0),
			#(display_message, "@{reg0} individuals"),
			(call_script, "script_pti_get_first_individual", "script_cf_pti_individual_is_of_selected_troop"),
			(call_script, "script_pti_nps_create_upper_left_stack_container"),
			(assign, "$pti_nps_individual_stack_container", reg1),
			(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_individual_stack_container", ":num_individuals", "script_pti_nps_individual_stack_init", "script_cf_pti_false", STACK_X_OFFSET),
			
			(try_begin),
				(ge, "$pti_nps_selected_troop_id", 0),
				
				(call_script, "script_gpu_create_troop_image", "$pti_nps_selected_troop_id", 350, 250, 1000),
			(try_end),
			
			(presentation_set_duration, 999999),
		]),
		
		(ti_on_presentation_run,
		[
			(try_begin),
				(key_clicked, key_e),
				
				(presentation_set_duration, 0),
			(try_end),
		]),
		
		# Trigger for making text green on mouseover
		(ti_on_presentation_mouse_enter_leave,
		[
			(store_trigger_param_1, ":overlay"),
			(store_trigger_param_2, ":mouse_left"),
			
			(try_begin),
				(troop_slot_eq, "trp_pti_nps_overlay_highlights_on_mouseover", ":overlay", 1),
				
				(try_begin),
					(eq, ":mouse_left", 0),
					
					(overlay_set_color, ":overlay", 0x008800),
				(else_try),
					(overlay_set_color, ":overlay", 0x000000),
				(try_end),
			(try_end),
		]),
		
		(ti_on_presentation_mouse_press,
		[
			(store_trigger_param_1, ":overlay"),
			(store_trigger_param_2, ":mouse_button"),
			
			(troop_get_slot, ":container", "trp_pti_nps_overlay_containers", ":overlay"),
			(try_begin),
				(eq, ":mouse_button", 0), # Left mouse-click
				(eq, ":container", "$pti_nps_troop_stack_container"),
				(troop_slot_eq, "trp_pti_nps_overlay_is_stack_button", ":overlay", 1),
				
				(troop_get_slot, "$pti_nps_selected_troop_id", "trp_pti_nps_overlay_stack_objects", ":overlay"),
				#(str_store_troop_name, s0, "$pti_nps_selected_troop_id"),
				#(display_message, "@Selected {s0}"),
				(start_presentation, "prsnt_new_party_screen"),
			(try_end),
		]),
		
		# Trigger for selecting troop stacks
		#(ti_on_presentation_mouse_press,
		#[
		#	(store_trigger_param_1, ":overlay"),
		#	(store_trigger_param_2, ":mouse_button"),
		#	
		#	(try_begin),
		#		(eq, ":mouse_button", 0), # Left mouse-click
		#		
		#		(try_begin),
		#			(troop_get_slot, ":clicked_troop", "trp_nps_overlay_troop_id", ":overlay"),
		#			(gt, ":clicked_troop", 0),
		#			
		#			#(str_store_troop_name, s0, ":clicked_troop"),
		#			#(display_message, "@Clicked {s0}"),
		#			
		#			(try_begin),
		#				# If shift is being held, select all troops between the last selected and the clicked troop
		#				(this_or_next|key_is_down, key_left_shift),
		#				(key_is_down, key_right_shift),
		#				
		#				(assign, ":clicked_stack_no", -1),
		#				(assign, ":last_selected_stack_no", -1),
		#				
		#				(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
		#				(try_for_range, ":stack", 1, ":num_stacks"),
		#					(party_stack_get_troop_id, ":troop", "p_main_party", ":stack"),
		#					
		#					(try_begin),
		#						(eq, ":troop", ":clicked_troop"),
		#						
		#						(assign, ":clicked_stack_no", ":stack"),
		#					(end_try),
		#					
		#					(try_begin),
		#						(eq, ":troop", "$last_selected_troop"),
		#						
		#						(assign, ":last_selected_stack_no", ":stack"),
		#					(try_end),
		#				(try_end),
		#				
		#				(assign, ":start_stack", ":last_selected_stack_no"),
		#				(val_min, ":start_stack", ":clicked_stack_no"),
		#				
		#				(assign, ":end_stack", ":clicked_stack_no"),
		#				(val_max, ":end_stack", ":last_selected_stack_no"),
		#				(val_add, ":end_stack", 1),
		#				
		#				(try_for_range, ":stack", ":start_stack", ":end_stack"),
		#					(party_stack_get_troop_id, ":troop", "p_main_party", ":stack"),
		#					
		#					(call_script, "script_select_troop_in_new_party_screen", ":troop"),
		#				(try_end),
		#			(else_try),
		#				# If ctrl is not being held, unselect all others
		#				(neg|key_is_down, key_left_control),
		#				(neg|key_is_down, key_right_control),
		#				
		#				(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
		#				(try_for_range, ":stack", 1, ":num_stacks"),
		#					(party_stack_get_troop_id, ":troop", "p_main_party", ":stack"),
		#					(neq, ":troop", ":clicked_troop"),
		#					
		#					(call_script, "script_deselect_troop_in_new_party_screen", ":troop"),
		#				(try_end),
		#			(try_end),
		#			
		#			# Select the clicked troop
		#			(call_script, "script_select_troop_in_new_party_screen", ":clicked_troop"),
		#			
		#			(assign, "$last_selected_troop", ":clicked_troop"),
		#			
		#			(call_script, "script_populate_agents_container_in_new_party_screen"),
		#		(try_end),
		#	(try_end),
		#]),
	])
	
]