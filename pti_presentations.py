from header_common import *
from header_presentations import *
from header_mission_templates import *
from ID_meshes import *
from header_operations import *
from header_triggers import *
from header_items import *
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
	
	("rename_troop_class", 0, mesh_party_window_b,
	[
		(ti_on_presentation_load,
		[
			# Troop class rename text box
			(str_store_class_name, s0, "$pti_class_to_be_renamed"),
			(call_script, "script_gpu_create_text_box_overlay", "str_s0", 400, 400),
			(assign, "$pti_nps_troop_class_rename_overlay"),
			
			# Button for when finished renaming troop class
			(str_store_string, s0, "@Done"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 585, 350),
			(assign, "$pti_nps_troop_class_rename_done_button", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_troop_class_rename_done_button", 85, 30),	# Reduce size
			
			# Cancel button
			(str_store_string, s0, "@Cancel"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 475, 350),
			(assign, "$pti_nps_troop_class_rename_cancel_button", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_troop_class_rename_cancel_button", 85, 30),	# Reduce size
			
			(presentation_set_duration, 999999),
		]),
		
		# Trigger for renaming troop class
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_troop_class_rename_overlay"),
				
				(str_store_string, s7, s0),
			(else_try),
				(eq, ":overlay", "$pti_nps_troop_class_rename_done_button"),
				
				(class_set_name, "$pti_class_to_be_renamed", s7),
				
				(start_presentation, "prsnt_new_party_screen"),
				#(presentation_set_duration, 0),
			(else_try),
				(eq, ":overlay", "$pti_nps_troop_class_rename_cancel_button"),
				
				(start_presentation, "prsnt_new_party_screen"),
				#(presentation_set_duration, 0),
			(try_end),
		]),
	]),
	
	("new_party_screen", 0, mesh_party_window_b,
	[
		(ti_on_presentation_load,
		[
			# Clear variables
			(assign, "$pti_nps_troop_stack_container", -1),
			(assign, "$pti_nps_exchange_troop_stack_container", -1),
			(assign, "$pti_nps_individual_stack_container", -1),
			(assign, "$pti_nps_exchange_individual_stack_container", -1),
			(assign, "$pti_nps_upgrade_button_1", -1),
			(assign, "$pti_nps_upgrade_button_2", -1),
			(assign, "$pti_nps_individual_summary", -1),
			(try_for_range, ":slot", 0, 99999),
				(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_containers", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":slot", 0),
				
				] + [(troop_set_slot, "trp_pti_nps_{}_{}_overlays".format(container, obj), ":slot", 0) for container in pti_nps_containers for obj in pti_nps_objects] + [
			(try_end),
			
			(assign, "$pti_nps_upper_left_container", -1),
			(assign, "$pti_nps_upper_right_container", -1),
			(assign, "$pti_nps_lower_left_container", -1),
			(assign, "$pti_nps_lower_right_container", -1),
			
			(assign, "$pti_nps_last_click_milliseconds", 0),
			(assign, "$pti_current_individual_troop", "trp_pti_individual_1"),
			(assign, "$pti_nps_open", 1),
			
			(assign, "$pti_nps_curr_troop_image", -1),
			
			(call_script, "script_pti_restore_party", "p_main_party"),
			
			# Checkbox for showing helmets
			(str_store_string, s0, "@Show Helmets"),
			gpu_create_text_overlay(550, 715, flags=tf_right_align),
			(call_script, "script_gpu_overlay_set_size", reg1, 750, 750),	# Reduce font size
			
			(call_script, "script_gpu_create_checkbox", 560, 717),
			(assign, "$pti_nps_show_helmets_checkbox", reg1),
			(overlay_set_val, "$pti_nps_show_helmets_checkbox", "$pti_show_helmets"),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_show_helmets_checkbox", 750, 750),	# Reduce checkbox size
			
			# Title (initially empty, set in script_pti_nps_select_stack)
			(str_clear, s0),
			gpu_create_text_overlay(500, 665, flags=tf_center_justify),
			(assign, "$pti_nps_title", reg1),
			
			# Stack movement buttons
			(str_store_string, s0, "@Move Up"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 615, 615),
			(assign, "$pti_nps_move_up_button", reg1),
			(call_script, "script_gpu_overlay_set_size", reg1, 100, 30),
			
			(str_store_string, s0, "@Move Down"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 615, 575),
			(assign, "$pti_nps_move_down_button", reg1),
			(call_script, "script_gpu_overlay_set_size", reg1, 100, 30),
			
			# Weekly wages and morale
			(str_clear, s0),
			gpu_create_text_overlay(500, 220, flags=tf_center_justify),
			(assign, "$pti_nps_weekly_wages", reg1),
			gpu_create_text_overlay(500, 195, flags=tf_center_justify),
			(assign, "$pti_nps_morale", reg1),
			
			# Upgrade buttons
			(call_script, "script_pti_nps_create_individual_upgrade_buttons"),
			
			# Disband/Give/Take button
			(str_store_string, s0, "@Disband"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 515, 112),
			(assign, "$pti_nps_disband_button", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_disband_button", 112, 35),	# Reduce size
			(overlay_set_display, "$pti_nps_disband_button", 0),
			
			# Talk button
			(str_store_string, s0, "@Talk"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 515, 155),
			(assign, "$pti_nps_talk_button", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_talk_button", 112, 35),	# Reduce size
			(overlay_set_display, "$pti_nps_talk_button", 0),
			
			## SET UP TROOP STACKS
			
			# Party member stacks
			(assign, "$pti_nps_selected_party", "p_main_party"),
			(try_begin),
				# Set up troop stacks if not drilled down to see individuals
				(neq, "$pti_show_individual_members", 1),
				
				# Add label for party companion stacks
				(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
				(call_script, "script_game_get_party_companion_limit", "p_main_party"),
				(assign, reg1, reg0),
				(party_get_num_companions, reg0, "p_main_party"),
				(str_store_string, s0, "@Company: {reg0} / {reg1}"),
				(call_script, "script_gpu_create_text_overlay", "str_s0", 825, 710, 1000, 262, 26, tf_center_justify),
				
				(call_script, "script_pti_nps_create_upper_right_stack_container"),
				(assign, "$pti_nps_troop_stack_container", reg1),
				(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_troop_stack_container", ":num_stacks", "script_pti_nps_troop_stack_init", STACK_X_OFFSET),
				
				# Set selected troop
				(try_begin),
					(eq, "$pti_exchange_troop_selected", 0),
					(gt, "$pti_nps_selected_troop_id", -1),
					
					(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_troop_id", "$pti_nps_troop_stack_container"),
				(try_end),
			(else_try),
				# Individual summary text (only displayed if not exchanging with a party, as it takes up the space where the exchange party's troop stacks are seen)
				(try_begin),
					(le, "$pti_exchange_party", 0),
					
					(call_script, "script_pti_nps_create_upper_left_stack_container"),
					(assign, "$pti_nps_individual_summary", reg1),
					(call_script, "script_gpu_overlay_set_size", "$pti_nps_individual_summary", 800, 800),	# Reduce font size
					(call_script, "script_pti_nps_refresh_text"),
				(try_end),
				
				pti_count_individuals(troop_id = "$pti_nps_selected_troop_id"),
				(assign, ":num_individuals", reg0),
				
				# Add individual labels
				(str_store_troop_name_plural, s0, "$pti_nps_selected_troop_id"),
				(assign, reg0, ":num_individuals"),
				(str_store_string, s0, "@{s0}: {reg0}"),
				(call_script, "script_gpu_create_text_overlay", "str_s0", 825, 715, 800, 262, 26, tf_center_justify),
				
				# Set up agent stacks
				#(display_message, "@{reg0} individuals"),
				(call_script, "script_pti_nps_create_upper_right_stack_container"),
				(assign, "$pti_nps_individual_stack_container", reg1),
				pti_get_first_individual(troop_id = "$pti_nps_selected_troop_id"),
				(assign, "$pti_nps_selected_stack_troop_id", "$pti_nps_selected_troop_id"),
				(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_individual_stack_container", ":num_individuals", "script_pti_nps_individual_stack_init", STACK_X_OFFSET),
				
				# Set selected individual
				(try_begin),
					(eq, "$pti_exchange_troop_selected", 0),
					(gt, "$pti_nps_selected_individual", -1),
					
					(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_individual", "$pti_nps_individual_stack_container"),
					(call_script, "script_pti_nps_refresh_individual_upgrade_buttons", "$pti_nps_selected_individual"),
				(try_end),
			(try_end),
			
			# Prisoner stacks
			(party_get_num_prisoner_stacks, ":num_stacks", "p_main_party"),
			(call_script, "script_pti_nps_create_lower_right_stack_container"),
			(assign, "$pti_nps_prisoner_stack_container", reg1),
			(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_prisoner_stack_container", ":num_stacks", "script_pti_nps_prisoner_stack_init", STACK_X_OFFSET),
			
			# Set selected prisoner stack
			(try_begin),
				(eq, "$pti_exchange_troop_selected", 0),
				(gt, "$pti_nps_selected_prisoner_troop_id", -1),
				
				(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_prisoner_troop_id", "$pti_nps_prisoner_stack_container"),
			(try_end),
			
			# Exchange party member stacks
			(try_begin),
				(gt, "$pti_exchange_party", 0),
				
				(assign, "$pti_nps_selected_party", "$pti_exchange_party"),
				(try_begin),
					# Set up exchange troop stacks if not drilled down to see individuals
					(neq, "$pti_show_individual_exchange_members", 1),
					
					(party_get_num_companion_stacks, ":num_stacks", "$pti_exchange_party"),
					
					(call_script, "script_pti_nps_create_upper_left_stack_container"),
					(assign, "$pti_nps_exchange_troop_stack_container", reg1),
					(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_exchange_troop_stack_container", ":num_stacks", "script_pti_nps_troop_stack_init", STACK_X_OFFSET),
					
					# Set selected troop
					(try_begin),
						(eq, "$pti_exchange_troop_selected", 1),
						(gt, "$pti_nps_selected_exchange_troop_id", -1),
						
						(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_exchange_troop_id", "$pti_nps_exchange_troop_stack_container"),
					(try_end),
				(else_try),
					pti_count_individuals(party = "$pti_exchange_party", troop_id = "$pti_nps_selected_exchange_troop_id"),
					(assign, ":num_individuals", reg0),
					
					# Set up agent stacks
					#(display_message, "@{reg0} individuals"),
					(call_script, "script_pti_nps_create_upper_left_stack_container"),
					(assign, "$pti_nps_exchange_individual_stack_container", reg1),
					pti_get_first_individual(party = "$pti_exchange_party", troop_id = "$pti_nps_selected_exchange_troop_id"),
					(assign, "$pti_nps_selected_stack_troop_id", "$pti_nps_selected_exchange_troop_id"),
					(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_exchange_individual_stack_container", ":num_individuals", "script_pti_nps_individual_stack_init", STACK_X_OFFSET),
					
					# Set selected individual
					(try_begin),
						(eq, "$pti_exchange_troop_selected", 1),
						(gt, "$pti_nps_selected_individual", -1),
						
						(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_individual", "$pti_nps_exchange_individual_stack_container"),
					(try_end),
				(try_end),
				
				# Exchange prisoner stacks
				(party_get_num_prisoner_stacks, ":num_stacks", "$pti_exchange_party"),
				(call_script, "script_pti_nps_create_lower_left_stack_container"),
				(assign, "$pti_nps_exchange_prisoner_stack_container", reg1),
				(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_exchange_prisoner_stack_container", ":num_stacks", "script_pti_nps_prisoner_stack_init", STACK_X_OFFSET),
				
				# Set selected prisoner stack
				(try_begin),
					(eq, "$pti_exchange_troop_selected", 1),
					(gt, "$pti_nps_selected_exchange_prisoner_troop_id", -1),
					
					(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_exchange_prisoner_troop_id", "$pti_nps_exchange_prisoner_stack_container"),
				(try_end),
			(try_end),
			
			## OTHER BUTTONS
			
			# Troop class (set at end of presentation to make it exist on top of other overlays, so clicking it isn't blocked)
			(call_script, "script_gpu_create_combo_label_overlay", 685, 385),
			(assign, "$pti_nps_troop_class_selector", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_troop_class_selector", 380, 650),	# Reduce size
			(try_for_range, ":class", grc_infantry, grc_everyone),
				(str_store_class_name, s0, ":class"),
				(overlay_add_item, "$pti_nps_troop_class_selector", s0),
			(try_end),
			
			(try_begin),
				(eq, "$pti_show_individual_members", 1),
				
				(str_store_string, s0, "@Default"),
				(overlay_add_item, "$pti_nps_troop_class_selector", s0),
			(try_end),
			
			(overlay_set_display, "$pti_nps_troop_class_selector", 0),
			
			# Troop class rename button
			(str_store_string, s0, "@Rename"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", 625, 360),
			(assign, "$pti_nps_troop_class_rename_button", reg1),
			(call_script, "script_gpu_overlay_set_size", "$pti_nps_troop_class_rename_button", 80, 20),	# Reduce size
			(overlay_set_display, "$pti_nps_troop_class_rename_button", 0),
			
			# Set the troop class
			(try_begin),
				(gt, "$pti_nps_selected_troop_id", -1),
				
				(call_script, "script_pti_nps_refresh_troop_class"),
			(try_end),
			
			(presentation_set_duration, 999999),
		]),
		
		# Keep track of how long the presentation has been running (which tells how long since a troop was selected)
		# Exit if esc is pressed
		(ti_on_presentation_run,
		[
			(store_trigger_param_1, "$pti_nps_milliseconds_running"),
			
			(try_begin),
				(key_clicked, key_escape),
				
				(assign, "$pti_nps_open", 0),
				(presentation_set_duration, 0),
			(else_try),
				(key_clicked, key_back_space),
				
				(try_begin),
					(eq, "$pti_nps_selected_stack_container", "$pti_nps_individual_stack_container"),
					(eq, "$pti_show_individual_members", 1),
					
					(assign, "$pti_show_individual_members", 0),
					(assign, "$pti_nps_selected_individual", -1),
					(start_presentation, "prsnt_new_party_screen"),
				(else_try),
					(eq, "$pti_nps_selected_stack_container", "$pti_nps_exchange_individual_stack_container"),
					(eq, "$pti_show_individual_exchange_members", 1),
					
					(assign, "$pti_show_individual_exchange_members", 0),
					(assign, "$pti_nps_selected_individual", -1),
					(start_presentation, "prsnt_new_party_screen"),
				(try_end),
			(else_try),
				(this_or_next|key_is_down, key_left_control),
				(key_is_down, key_right_control),
				(key_clicked, key_x),
				
				(try_begin),
					(gt, "$pti_nps_selected_individual", -1),
					
					Individual.get("$pti_nps_selected_individual", "xp"),
					(val_add, reg0, 1000),
					Individual.set("$pti_nps_selected_individual", "xp", reg0),
					(start_presentation, "prsnt_new_party_screen"),
				(try_end),
			(else_try),
				(this_or_next|key_is_down, key_left_control),
				(key_is_down, key_right_control),
				(key_clicked, key_w),
				
				(try_begin),
					(gt, "$pti_nps_selected_individual", -1),
					
					Individual.set("$pti_nps_selected_individual", "is_wounded", 1),
					(call_script, "script_pti_restore_party", "p_main_party"),
					(start_presentation, "prsnt_new_party_screen"),
				(try_end),
			(else_try),
				(key_clicked, key_e),
				
				(display_message, "@Exchange individuals:"),
				pti_count_individuals(party = "$pti_exchange_party"),
				(assign, ":count", reg0),
				
				pti_get_first_individual(party = "$pti_exchange_party"),
				(try_for_range, ":stack", 0, ":count"),
					(call_script, "script_pti_individual_get_type_and_name", "$pti_current_individual"),
					(assign, reg0, "$pti_current_individual"),
					(assign, reg1, "$pti_curr_individual_index"),
					(display_message, "@{s0} {s1} ({reg0}) from index {reg1}"),
					
					pti_get_next_individual(party = "$pti_exchange_party"),
				(try_end),
			(try_end),
		]),
		
		(ti_escape_pressed, [(presentation_set_duration, 0)]),
		
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
		
		# Handle clicking of troop/individual stacks, including double clicks
		(ti_on_presentation_mouse_press,
		[
			(store_trigger_param_1, ":overlay"),
			#(store_trigger_param_2, ":mouse_left"),
			
			(try_begin),
				(troop_get_slot, ":container", "trp_pti_nps_overlay_containers", ":overlay"),
				(this_or_next|eq, ":container", "$pti_nps_upper_left_container"),
				(this_or_next|eq, ":container", "$pti_nps_upper_right_container"),
				(this_or_next|eq, ":container", "$pti_nps_lower_left_container"),
				(eq, ":container", "$pti_nps_lower_right_container"),
				
				(troop_get_slot, ":stack_object", "trp_pti_nps_overlay_stack_objects", ":overlay"),
				
				#(assign, reg0, ":stack_object"),
				#(assign, reg1, ":container"),
				#(display_message, "@Clicked object (ID: {reg0}) in container {reg1}"),
				
				# If the clicked stack is not the already selected one, unselect the previously selected stack and select the new one
				(try_begin),
					(this_or_next|neq, ":container", "$pti_nps_selected_stack_container"),
					(neq, ":stack_object", "$pti_nps_selected_stack_object"),
					
					# Unselect previously selected stack if applicable
					(try_begin),
						(gt, "$pti_nps_selected_stack_container", 0),
						(gt, "$pti_nps_selected_stack_object", -1),
						
						(call_script, "script_pti_nps_unselect_stack", "$pti_nps_selected_stack_object", "$pti_nps_selected_stack_container"),
						
						#(assign, reg0, "$pti_nps_selected_stack_object"),
						#(assign, reg1, "$pti_nps_selected_stack_container"),
						#(display_message, "@Unselecting object (ID: {reg0}) in container {reg1}"),
					(try_end),
					
					# Select the clicked stack
					(call_script, "script_pti_nps_select_stack", ":stack_object", ":container"),
					(try_begin),
						(gt, "$pti_nps_selected_stack_container", 0),
						(this_or_next|eq, "$pti_nps_selected_stack_container", "$pti_nps_exchange_troop_stack_container"),
						(this_or_next|eq, "$pti_nps_selected_stack_container", "$pti_nps_exchange_individual_stack_container"),
						(eq, "$pti_nps_selected_stack_container", "$pti_nps_exchange_prisoner_stack_container"),
						
						(assign, "$pti_exchange_troop_selected", 1),
					(else_try),
						(assign, "$pti_exchange_troop_selected", 0),
					(try_end),
					
					#(assign, reg0, ":stack_object"),
					#(assign, reg1, ":container"),
					#(display_message, "@Selecting object (ID: {reg0}) in container {reg1}"),
				(else_try),
					# If stack double-clicked, drill down to individuals
					(eq, ":container", "$pti_nps_selected_stack_container"),
					(eq, ":stack_object", "$pti_nps_selected_stack_object"),
					
					(store_sub, ":milliseconds_since_click", "$pti_nps_milliseconds_running", "$pti_nps_last_click_milliseconds"),
					(is_between, ":milliseconds_since_click", 10, 500),
					
					(this_or_next|eq, ":container", "$pti_nps_troop_stack_container"),
					(eq, ":container", "$pti_nps_exchange_troop_stack_container"),
					
					(try_begin),
						(eq, ":container", "$pti_nps_troop_stack_container"),
						
						(assign, "$pti_show_individual_members", 1),
						(assign, "$pti_exchange_troop_selected", 0),
						pti_get_first_individual(troop_id = "$pti_nps_selected_troop_id"),
						(assign, "$pti_nps_selected_individual", "$pti_current_individual"),
					(else_try),
						(eq, ":container", "$pti_nps_exchange_troop_stack_container"),
						
						(assign, "$pti_show_individual_exchange_members", 1),
						(assign, "$pti_exchange_troop_selected", 1),
						pti_get_first_individual(party = "$pti_exchange_party", troop_id = "$pti_nps_selected_exchange_troop_id"),
						(assign, "$pti_nps_selected_individual", "$pti_current_individual"),
					(try_end),
					
					(start_presentation, "prsnt_new_party_screen"),
				(try_end),
				
				(assign, "$pti_nps_last_click_milliseconds", "$pti_nps_milliseconds_running"),
				
				(try_begin),
					(this_or_next|eq, ":container", "$pti_nps_troop_stack_container"),
					(this_or_next|eq, ":container", "$pti_nps_exchange_troop_stack_container"),
					(this_or_next|eq, ":container", "$pti_nps_prisoner_stack_container"),
					(eq, ":container", "$pti_nps_exchange_prisoner_stack_container"),
					
					(assign, ":troop_id", ":stack_object"),
					(assign, ":continue", 0),
					(try_begin),
						(eq, ":container", "$pti_nps_troop_stack_container"),
						(neq, ":troop_id", "$pti_nps_selected_troop_id"),
						
						(assign, "$pti_nps_selected_troop_id", ":troop_id"),
						(assign, ":continue", 1),
					(else_try),
						(eq, ":container", "$pti_nps_exchange_troop_stack_container"),
						(neq, ":troop_id", "$pti_nps_selected_exchange_troop_id"),
						
						(assign, "$pti_nps_selected_exchange_troop_id", ":troop_id"),
						(assign, ":continue", 1),
					(else_try),
						(eq, ":container", "$pti_nps_prisoner_stack_container"),
						(neq, ":troop_id", "$pti_nps_selected_prisoner_troop_id"),
						
						(assign, "$pti_nps_selected_prisoner_troop_id", ":troop_id"),
					(else_try),
						(eq, ":container", "$pti_nps_exchange_prisoner_stack_container"),
						(neq, ":troop_id", "$pti_nps_selected_exchange_prisoner_troop_id"),
						
						(assign, "$pti_nps_selected_exchange_prisoner_troop_id", ":troop_id"),
					(try_end),
					(eq, ":continue", 1),
					
					# Refresh overlays
					(call_script, "script_pti_nps_refresh_troop_class"),
				(else_try),
					(this_or_next|eq, ":container", "$pti_nps_individual_stack_container"),
					(eq, ":container", "$pti_nps_exchange_individual_stack_container"),
					
					(assign, ":individual", ":stack_object"),
					(neq, ":individual", "$pti_nps_selected_individual"),
					
					(assign, "$pti_nps_selected_individual", ":individual"),
					
					# Refresh overlays
					(call_script, "script_pti_nps_refresh_troop_class"),
					(call_script, "script_pti_nps_refresh_individual_upgrade_buttons", "$pti_nps_selected_individual"),
					
					(le, "$pti_exchange_party", 0),
					
					(call_script, "script_pti_nps_refresh_text"),
				(try_end),
			(try_end),
		]),
		
		# Trigger for when upgrade buttons are clicked
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			#(store_trigger_param_2, ":value"),
			
			(try_begin),
				(gt, "$pti_nps_selected_individual", -1),
				
				(this_or_next|eq, ":overlay", "$pti_nps_upgrade_button_1"),
				(eq, ":overlay", "$pti_nps_upgrade_button_2"),
				
				Individual.get("$pti_nps_selected_individual", "troop_type"),
				(assign, ":troop_id", reg0),
				(try_begin),
					(eq, ":overlay", "$pti_nps_upgrade_button_1"),					
					
					(troop_get_upgrade_troop, ":upgrade", ":troop_id", 0),
				(else_try),
					(troop_get_upgrade_troop, ":upgrade", ":troop_id", 1),
				(try_end),
				
				(call_script, "script_cf_pti_individual_can_upgrade_to", "$pti_nps_selected_individual", ":upgrade"),
				
				Individual.set("$pti_nps_selected_individual", "troop_type", ":upgrade"),
				(call_script, "script_pti_individual_generate_base_equipment", "$pti_nps_selected_individual"),
				
				(party_remove_members, "p_main_party", ":troop_id", 1),
				(party_add_members, "p_main_party", ":upgrade", 1),
				
				(try_begin),
					(party_count_members_of_type, ":stack_size", "p_main_party", "$pti_nps_selected_troop_id"),
					(eq, ":stack_size", 0),
					
					(assign, "$pti_nps_selected_troop_id", ":upgrade"),
				(else_try),
					pti_get_first_individual(troop_id = "$pti_nps_selected_troop_id"),
					(assign, "$pti_nps_selected_individual", "$pti_current_individual"),
				(try_end),
				(start_presentation, "prsnt_new_party_screen"),
			(try_end),
		]),
		
		# Trigger for "Show Helmets" checkbox being ticked/unticked
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			(store_trigger_param_2, ":value"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_show_helmets_checkbox"),
				
				(assign, "$pti_show_helmets", ":value"),
				(start_presentation, "prsnt_new_party_screen"),
			(try_end),
		]),
		
		# Trigger for changing troop class
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			(store_trigger_param_2, ":value"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_troop_class_selector"),
				
				(try_begin),
					(eq, "$pti_show_individual_members", 1),
					
					(try_begin),
						(lt, ":value", grc_everyone),
						
						Individual.set("$pti_nps_selected_individual", "class_overridden", 1),
						Individual.set("$pti_nps_selected_individual", "class", ":value"),
						(overlay_set_display, "$pti_nps_troop_class_rename_button", 1),
					(else_try),
						Individual.set("$pti_nps_selected_individual", "class_overridden", 0),
						(overlay_set_display, "$pti_nps_troop_class_rename_button", 0),
					(try_end),
				(else_try),
					(troop_set_class, "$pti_nps_selected_troop_id", ":value"),
				(try_end),
			(try_end),
		]),
		
		# Trigger for renaming troop class
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_troop_class_rename_button"),
				
				(call_script, "script_pti_nps_get_selected_class"),
				(assign, "$pti_class_to_be_renamed", reg0),
				(start_presentation, "prsnt_rename_troop_class"),
			(try_end),
		]),
		
		# Trigger for talking to individuals
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_talk_button"),
				
				(call_script, "script_pti_container_get_overlay_mappings", "$pti_nps_selected_stack_container"),
				(assign, ":troop_mapping", reg4),
				(troop_get_slot, ":individual_troop", ":troop_mapping", "$pti_nps_selected_individual"),
				(call_script, "script_setup_troop_meeting", ":individual_troop", -1),
			(try_end),
		]),
		
		# Trigger for disbanding individuals
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":overlay"),
			
			(try_begin),
				(eq, ":overlay", "$pti_nps_disband_button"),
				
				(assign, ":key_held", -1),
				(try_begin),
					(this_or_next|key_is_down, key_left_control),
					(key_is_down, key_right_control),
					
					(assign, ":key_held", key_left_control),
				(else_try),
					(this_or_next|key_is_down, key_left_shift),
					(key_is_down, key_right_shift),
					
					(assign, ":key_held", key_left_shift),
				(try_end),
				
				(try_begin),
					(this_or_next|eq, "$pti_nps_selected_stack_container", "$pti_nps_upper_left_container"),
					(eq, "$pti_nps_selected_stack_container", "$pti_nps_upper_right_container"),
					
					(call_script, "script_pti_nps_disband_or_exchange_selected_stack", ":key_held"),
				(else_try),
					(call_script, "script_pti_nps_release_or_exchange_prisoner_stack", ":key_held"),
				(try_end),
				
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
