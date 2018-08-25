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

PTI_INDV_IMAGE_X = -70
PTI_INDV_IMAGE_Y = 350
PTI_INDV_IMAGE_SIZE = 1250

PTI_INV_SLOT_SIZE = 60
PTI_INV_CONT_WIDTH = 1
PTI_INV_CONT_HEIGHT = 4

PTI_INV_POS_X = PTI_INDV_IMAGE_X + 295
PTI_INV_POS_Y = PTI_INDV_IMAGE_Y + 45

PTI_BUTTONS_POS_X = 800
PTI_BUTTONS_POS_Y = 50
PTI_BUTTONS_SIZE_X = 110
PTI_BUTTONS_SIZE_Y = 40
PTI_BUTTONS_GAP = 20

presentations = [
	
	("test_individual_screen", 0, mesh_load_window,
	[
		(ti_on_presentation_load,
		[
			## TROOP IMAGE
			(call_script, "script_pti_equip_troop_as_individual", "trp_pti_nps_presentation_troop", "$pti_test_individual"),
			(call_script, "script_pti_give_troop_individual_face", "trp_pti_nps_presentation_troop", "$pti_test_individual"),
			
			(call_script, "script_gpu_create_troop_image", "trp_pti_nps_presentation_troop", PTI_INDV_IMAGE_X, PTI_INDV_IMAGE_Y, PTI_INDV_IMAGE_SIZE),
			
			## HELMET CHECKBOX
			
			(str_store_string, s0, "@Show Helmet"),
			(call_script, "script_gpu_create_text_overlay", "str_s0", PTI_INV_POS_X, PTI_INV_POS_Y + PTI_INV_SLOT_SIZE * (PTI_INV_CONT_HEIGHT + 0.5), 1000, 125, 20, 0),
			(call_script, "script_gpu_create_checkbox", PTI_INV_POS_X + 125, PTI_INV_POS_Y + PTI_INV_SLOT_SIZE * (PTI_INV_CONT_HEIGHT + 0.5)),
			(assign, "$pti_test_show_helmet_checkbox", reg1),
			(overlay_set_val, "$pti_test_show_helmet_checkbox", "$pti_show_helmets"),
			
			#(create_check_box_overlay, reg1, "mesh_checkbox_off", "mesh_checkbox_on"),
			#(position_set_x, pos1, PTI_INV_POS_X),
			#(position_set_y, pos1, PTI_INV_POS_Y + PTI_INV_SLOT_SIZE * 4.5),
			#(overlay_set_position, reg1, pos1),
			
			## TROOP INVENTORY
			(call_script, "script_gpu_create_scrollable_container", PTI_INV_POS_X, PTI_INV_POS_Y, PTI_INV_SLOT_SIZE * PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE * PTI_INV_CONT_HEIGHT),
			(assign, "$pti_individual_armour_container", reg1),
			
			(set_container_overlay, "$pti_individual_armour_container"),
			
			Individual.get("$pti_test_individual", "base_armour"),
			(assign, ":equipment", reg0),
			(try_for_range, ":slot", ek_head, ek_horse),
				(store_and, ":item", ":equipment", mask(ITEM_BITS)),
				
				(store_sub, ":item_index", ":slot", ek_head),
				(call_script, "script_gpu_get_grid_position", ":item_index", 4, PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE, PTI_INV_SLOT_SIZE),
				(assign, ":pos_x", reg0),
				(assign, ":pos_y", reg1),
				
				(call_script, "script_gpu_create_mesh_overlay", "mesh_inv_slot", ":pos_x", ":pos_y", PTI_INV_SLOT_SIZE * 10, PTI_INV_SLOT_SIZE * 10),
				(gt, ":item", 0),
				
				(store_add, ":item_x", ":pos_x", PTI_INV_SLOT_SIZE / 2),
				(store_add, ":item_y", ":pos_y", PTI_INV_SLOT_SIZE / 2),
				(call_script, "script_gpu_create_item_overlay", ":item", ":item_x", ":item_y", PTI_INV_SLOT_SIZE * 10),
				
				(val_rshift, ":equipment", ITEM_BITS),
			(try_end),
			
			(set_container_overlay, -1),
			
			(call_script, "script_gpu_create_scrollable_container", PTI_INV_POS_X + PTI_INV_SLOT_SIZE * 1.5, PTI_INV_POS_Y, PTI_INV_SLOT_SIZE * PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE * PTI_INV_CONT_HEIGHT),
			(assign, "$pti_individual_weapon_container", reg1),
			
			(set_container_overlay, "$pti_individual_weapon_container"),
			
			Individual.get("$pti_test_individual", "base_weapons"),
			(assign, ":equipment", reg0),
			(try_for_range, ":slot", ek_item_0, ek_head),
				(store_and, ":item", ":equipment", mask(ITEM_BITS)),
				
				(store_sub, ":item_index", ":slot", ek_item_0),
				(call_script, "script_gpu_get_grid_position", ":item_index", 4, PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE, PTI_INV_SLOT_SIZE),
				(assign, ":pos_x", reg0),
				(assign, ":pos_y", reg1),
				
				(call_script, "script_gpu_create_mesh_overlay", "mesh_inv_slot", ":pos_x", ":pos_y", PTI_INV_SLOT_SIZE * 10, PTI_INV_SLOT_SIZE * 10),
				(gt, ":item", 0),
				
				(store_add, ":item_x", ":pos_x", PTI_INV_SLOT_SIZE / 2),
				(store_add, ":item_y", ":pos_y", PTI_INV_SLOT_SIZE / 2),
				(call_script, "script_gpu_create_item_overlay", ":item", ":item_x", ":item_y", PTI_INV_SLOT_SIZE * 10),
				
				(val_rshift, ":equipment", ITEM_BITS),
			(try_end),
			
			(set_container_overlay, -1),
			
			Individual.get("$pti_test_individual", "base_horse"),
			(assign, ":horse", reg0),
			(try_begin),
				(assign, ":pos_x", PTI_INV_POS_X + PTI_INV_SLOT_SIZE * 3),
				(assign, ":pos_y", PTI_INV_POS_Y),
				
				(call_script, "script_gpu_create_mesh_overlay", "mesh_inv_slot", ":pos_x", ":pos_y", PTI_INV_SLOT_SIZE * 10, PTI_INV_SLOT_SIZE * 10),
				(gt, ":horse", 0),
				
				(store_add, ":item_x", ":pos_x", PTI_INV_SLOT_SIZE / 2),
				(store_add, ":item_y", ":pos_y", PTI_INV_SLOT_SIZE / 2),
				(call_script, "script_gpu_create_item_overlay", ":horse", ":item_x", ":item_y", PTI_INV_SLOT_SIZE * 10),
			(try_end),
			
			#(try_begin),
			#	Individual.get("$pti_test_individual", "base_horse"),
			#	(gt, reg0, 0),
			#(try_end),
			
			#(call_script, "script_gpu_create_scrollable_container", PTI_INV_POS_X, PTI_INV_POS_Y, PTI_INV_SLOT_SIZE * PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE * PTI_INV_CONT_HEIGHT),
			#(assign, "$pti_troop_inventory_container", reg1),
			#
			#(set_container_overlay, "$pti_troop_inventory_container"),
			#
			#(try_for_range, ":item_slot", 0, num_equipment_kinds),
			#	(troop_get_inventory_slot, ":item", "trp_pti_nps_presentation_troop", ":item_slot"),
			#	(troop_get_inventory_slot_modifier, ":imod", "trp_pti_nps_presentation_troop", ":item_slot"),
			#	(gt, ":item", 0),
			#	
			#	(troop_add_item, "trp_pti_nps_presentation_troop", ":item", ":imod"),
			#	(troop_set_inventory_slot, "trp_pti_nps_presentation_troop", ":item_slot", -1),
			#(try_end),
			#
			#(troop_get_inventory_capacity, ":capacity", "trp_pti_nps_presentation_troop"),
			#(val_sub, ":capacity", num_equipment_kinds),
			#(try_for_range, ":item_index", 0, ":capacity"),
			#	(store_add, ":item_slot", ":item_index", num_equipment_kinds),
			#	(troop_get_inventory_slot, ":item", "trp_pti_nps_presentation_troop", ":item_slot"),
			#	
			#	(call_script, "script_gpu_get_grid_position", ":item_index", ":capacity", PTI_INV_CONT_WIDTH, PTI_INV_SLOT_SIZE, PTI_INV_SLOT_SIZE),
			#	(assign, ":pos_x", reg0),
			#	(assign, ":pos_y", reg1),
			#	
			#	(call_script, "script_gpu_create_mesh_overlay", "mesh_inv_slot", ":pos_x", ":pos_y", PTI_INV_SLOT_SIZE * 10, PTI_INV_SLOT_SIZE * 10),
			#	(gt, ":item", 0),
			#	
			#	(store_add, ":item_x", ":pos_x", PTI_INV_SLOT_SIZE / 2),
			#	(store_add, ":item_y", ":pos_y", PTI_INV_SLOT_SIZE / 2),
			#	(call_script, "script_gpu_create_item_overlay", ":item", ":item_x", ":item_y", PTI_INV_SLOT_SIZE * 10),
			#(try_end),
			#
			#(set_container_overlay, -1),
			
			## EXIT BUTTON
			(str_store_string, s0, "@Exit"),
			(call_script, "script_gpu_create_game_button_overlay", "str_s0", PTI_BUTTONS_POS_X + PTI_BUTTONS_SIZE_X + PTI_BUTTONS_GAP, PTI_BUTTONS_POS_Y),
			(assign, "$pti_test_individual_screen_exit", reg1),
			(position_set_x, pos1, PTI_BUTTONS_SIZE_X),
			(position_set_y, pos1, PTI_BUTTONS_SIZE_Y),
			(overlay_set_size, "$pti_test_individual_screen_exit", pos1),
			
			(presentation_set_duration, 999999),
		]),
		
		(ti_on_presentation_event_state_change,
		[
			(store_trigger_param_1, ":object"),
			(store_trigger_param_2, ":value"),
			
			(try_begin),
				(eq, ":object", "$pti_test_show_helmet_checkbox"),
				
				(assign, "$pti_show_helmets", ":value"),
				(start_presentation, "prsnt_test_individual_screen"),
			(else_try),
				## EXIT BUTTON PRESSED
				(eq, ":object", "$pti_test_individual_screen_exit"),
				
				(presentation_set_duration, 0),
			(try_end),
		]),
	]),
	
	("new_party_screen", 0, mesh_party_window_b,
	[
		(ti_on_presentation_load,
		[
			# Clear variables
			(assign, "$pti_nps_troop_stack_container", -1),
			(assign, "$pti_nps_individual_stack_container", -1),
			(assign, "$pti_nps_upgrade_button_1", -1),
			(assign, "$pti_nps_upgrade_button_2", -1),
			(try_for_range, ":slot", 0, 99999),
				(troop_set_slot, "trp_pti_nps_overlay_highlights_on_mouseover", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_containers", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_stack_object_text_overlays", ":slot", 0),
				(troop_set_slot, "trp_pti_nps_overlay_stack_objects", ":slot", 0),
				(troop_slot_eq, "trp_pti_nps_stack_button_overlays", ":slot", 0),
			(try_end),
			
			(assign, "$pti_nps_last_click_milliseconds", 0),
			(assign, "$pti_current_individual_troop", "trp_pti_individual_1"),
			(assign, "$pti_nps_open", 1),
			
			# Checkbox for showing helmets
			(str_store_string, s0, "@Show Helmets"),
			gpu_create_text_overlay(550, 715, flags=tf_right_align),
			
			(call_script, "script_gpu_create_checkbox", 560, 715),
			(assign, "$pti_nps_show_helmets_checkbox", reg1),
			(overlay_set_val, "$pti_nps_show_helmets_checkbox", "$pti_show_helmets"),
			
			(try_begin),
				# Set up troop stacks if not drilled down to see agents
				(neq, "$pti_nps_open_agent_screen", 1),
				
				# Add label for party companion stacks
				(party_get_num_companion_stacks, ":num_stacks", "p_main_party"),
				(call_script, "script_game_get_party_companion_limit", "p_main_party"),
				(assign, reg1, reg0),
				(party_get_num_companions, reg0, "p_main_party"),
				(str_store_string, s0, "@Company: {reg0} / {reg1}"),
				(call_script, "script_gpu_create_text_overlay", "str_s0", 825, 712, 1000, 262, 26, tf_center_justify),
				
				(call_script, "script_pti_nps_create_upper_right_stack_container"),
				(assign, "$pti_nps_troop_stack_container", reg1),
				(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_troop_stack_container", ":num_stacks", "script_pti_nps_troop_stack_init", STACK_X_OFFSET),
				
				# Add troop image if a troop is selected
				(try_begin),
					(gt, "$pti_nps_selected_troop_id", -1),
					
					# Show pressed button instead of unpressed one
					(troop_get_slot, ":stack_button", "trp_pti_nps_stack_button_overlays", "$pti_nps_selected_troop_id"),
					#(overlay_set_display, ":stack_button", 0),
					(troop_get_slot, ":highlight_button", "trp_pti_nps_stack_button_highlight_overlays", "$pti_nps_selected_troop_id"),
					(overlay_set_display, ":highlight_button", 1),
					
					# Show selected troop image
					(troop_get_slot, ":troop_image", "trp_pti_nps_stack_object_troop_images", "$pti_nps_selected_troop_id"),
					(overlay_set_display, ":troop_image", 1),
				(try_end),
			(else_try),
				# Individual summary text
				(call_script, "script_pti_nps_create_upper_left_stack_container"),
				(assign, "$pti_nps_individual_summary", reg1),
				(call_script, "script_pti_nps_refresh_text"),
				
				# Set up agent stacks
				(call_script, "script_pti_count_individuals", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
				(assign, ":num_individuals", reg0),
				
				# Add individual labels
				(str_store_troop_name_plural, s0, "$pti_nps_selected_troop_id"),
				(assign, reg0, ":num_individuals"),
				(str_store_string, s0, "@{s0}: {reg0}"),
				(call_script, "script_gpu_create_text_overlay", "str_s0", 825, 712, 1000, 262, 26, tf_center_justify),
				
				#(display_message, "@{reg0} individuals"),
				(call_script, "script_pti_nps_create_upper_right_stack_container"),
				(assign, "$pti_nps_individual_stack_container", reg1),
				(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
				(call_script, "script_pti_nps_add_stacks_to_container", "$pti_nps_individual_stack_container", ":num_individuals", "script_pti_nps_individual_stack_init", STACK_X_OFFSET),
				
				# Add upgrade buttons
				(call_script, "script_pti_nps_create_individual_upgrade_buttons"),
				
				# Add individual image if an individual is selected
				(try_begin),
					(gt, "$pti_nps_selected_individual", -1),
					
					# Show pressed button instead of unpressed one
					(troop_get_slot, ":stack_button", "trp_pti_nps_stack_button_overlays", "$pti_nps_selected_individual"),
					#(overlay_set_display, ":stack_button", 0),
					(troop_get_slot, ":highlight_button", "trp_pti_nps_stack_button_highlight_overlays", "$pti_nps_selected_individual"),
					(overlay_set_display, ":highlight_button", 1),
					
					# Show selected individual image
					(troop_get_slot, ":image_troop", "trp_pti_nps_stack_object_troop_images", "$pti_nps_selected_individual"),
					(overlay_set_display, ":image_troop", 1),
					
					#(call_script, "script_pti_equip_troop_as_individual", "trp_pti_nps_presentation_troop", "$pti_nps_selected_individual"),
					#(call_script, "script_pti_give_troop_individual_face", "trp_pti_nps_presentation_troop", "$pti_nps_selected_individual"),
					
					(call_script, "script_pti_nps_refresh_individual_upgrade_buttons", "$pti_nps_selected_individual"),
				(try_end),
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
				(eq, "$pti_nps_open_agent_screen", 1),
				
				(assign, "$pti_nps_open_agent_screen", 0),
				(assign, "$pti_nps_selected_individual", -1),
				(start_presentation, "prsnt_new_party_screen"),
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
			
			# Set selected troop id if clicked
			(try_begin),
				(troop_slot_eq, "trp_pti_nps_overlay_containers", ":overlay", "$pti_nps_troop_stack_container"),
				
				(troop_get_slot, ":troop_id", "trp_pti_nps_overlay_stack_objects", ":overlay"),
				
				# If the clicked troop has already been selected and was clicked under 500ms ago (i.e. double-clicked), go to agents screen
				(try_begin),
					(neg|troop_is_hero, ":troop_id"),
					(eq, ":troop_id", "$pti_nps_selected_troop_id"),
					(store_sub, ":milliseconds_since_click", "$pti_nps_milliseconds_running", "$pti_nps_last_click_milliseconds"),
					(is_between, ":milliseconds_since_click", 10, 500),
					
					(assign, "$pti_nps_open_agent_screen", 1),
					(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
					(assign, "$pti_nps_selected_individual", "$pti_current_individual"),
					
					(start_presentation, "prsnt_new_party_screen"),
				(else_try),
					# Unselect previously selected troop if applicable
					(try_begin),
						(gt, "$pti_nps_selected_troop_id", -1),
						
						(call_script, "script_pti_nps_unselect_stack", "$pti_nps_selected_troop_id"),
						(assign, "$pti_nps_last_click_milliseconds", "$pti_nps_milliseconds_running"),
					(try_end),
					
					(call_script, "script_pti_nps_select_stack", ":troop_id"),
				(try_end),
				
				(assign, "$pti_nps_selected_troop_id", ":troop_id"),
			(try_end),
			
			# Set selected individual if clicked
			(try_begin),
				(troop_slot_eq, "trp_pti_nps_overlay_containers", ":overlay", "$pti_nps_individual_stack_container"),
				
				# Unselect previously selected individual if applicable
				(try_begin),
					(gt, "$pti_nps_selected_individual", -1),
					
					(call_script, "script_pti_nps_unselect_stack", "$pti_nps_selected_individual"),
				(try_end),
				
				# Select new individual
				(troop_get_slot, "$pti_nps_selected_individual", "trp_pti_nps_overlay_stack_objects", ":overlay"),
				(call_script, "script_pti_nps_select_stack", "$pti_nps_selected_individual"),
				
				# Refresh the summary text
				(call_script, "script_pti_nps_refresh_text"),
				
				# Update the upgrade buttons
				(call_script, "script_pti_nps_refresh_individual_upgrade_buttons", "$pti_nps_selected_individual"),
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
				
				Individual.get("$pti_nps_selected_individual", "xp"),
				(assign, ":xp", reg0),
				
				Individual.get("$pti_nps_selected_individual", "troop_type"),
				(assign, ":troop_id", reg0),
				(try_begin),
					(eq, ":overlay", "$pti_nps_upgrade_button_1"),					
					
					(troop_get_upgrade_troop, ":upgrade", ":troop_id", 0),
					(call_script, "script_pti_xp_needed_to_upgrade_to", ":upgrade"),
					(assign, ":upgrade_xp", reg0),
				(else_try),
					(troop_get_upgrade_troop, ":upgrade", ":troop_id", 1),
					(call_script, "script_pti_xp_needed_to_upgrade_to", ":upgrade"),
					(assign, ":upgrade_xp", reg0),
				(try_end),
				
				(ge, ":xp", ":upgrade_xp"),
				
				Individual.set("$pti_nps_selected_individual", "troop_type", ":upgrade"),
				(call_script, "script_pti_individual_generate_base_equipment", "$pti_nps_selected_individual"),
				
				(party_remove_members, "p_main_party", ":troop_id", 1),
				(party_add_members, "p_main_party", ":upgrade", 1),
				
				(try_begin),
					(party_count_members_of_type, ":stack_size", "p_main_party", "$pti_nps_selected_troop_id"),
					(eq, ":stack_size", 0),
					
					(assign, "$pti_nps_selected_troop_id", ":upgrade"),
				(else_try),
					(call_script, "script_pti_get_first_individual", "p_main_party", "script_cf_pti_individual_is_of_selected_troop"),
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
