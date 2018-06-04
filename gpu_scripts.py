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

scripts = [
	
	("gpu_create_scrollable_container",
	[
		(store_script_param, ":pos_x", 1),
		(store_script_param, ":pos_y", 2),
		(store_script_param, ":size_x", 3),
		(store_script_param, ":size_y", 4),
		
		(str_clear, s0),
		(call_script, "script_gpu_create_text_overlay", "str_s0", ":pos_x", ":pos_y", 1000, ":size_x", ":size_y", tf_scrollable),
	]),
	
	("gpu_create_text_overlay",
	[
		(store_script_param, ":string", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		(store_script_param, ":text_size", 4),
		(store_script_param, ":size_x", 5),
		(store_script_param, ":size_y", 6),
		(store_script_param, ":flags", 7),
		
		(set_fixed_point_multiplier, 1000),
		(create_text_overlay, reg1, ":string", ":flags"),
		(position_set_x, pos1, ":pos_x"),
		(position_set_y, pos1, ":pos_y"),
		(overlay_set_position, reg1, pos1),
		(position_set_x, pos1, ":text_size"),
		(position_set_y, pos1, ":text_size"),
		(overlay_set_size, reg1, pos1),
		(position_set_x, pos1, ":size_x"),
		(position_set_y, pos1, ":size_y"),
		(overlay_set_area_size, reg1, pos1),
		(overlay_set_text, reg1, ":string"),
	]),
	
	("gpu_create_game_button_overlay",
	[
		(store_script_param, ":string", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		
		(set_fixed_point_multiplier, 1000),
		(create_game_button_overlay, reg1, ":string"),
		(position_set_x, pos1, ":pos_x"),
		(position_set_y, pos1, ":pos_y"),
		(overlay_set_position, reg1, pos1),
		(overlay_set_text, reg1, ":string"),
	]),
	
	("gpu_create_button_overlay",
	[
		(store_script_param, ":string", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		(store_script_param, ":size", 4),
		(store_script_param, ":flags", 5),
		
		(set_fixed_point_multiplier, 1000),
		(create_button_overlay, reg1, ":string", ":flags"),
		(position_set_x, pos1, ":pos_x"),
		(position_set_y, pos1, ":pos_y"),
		(overlay_set_position, reg1, pos1),
		(position_set_x, pos1, ":size"),
		(position_set_y, pos1, ":size"),
		(overlay_set_size, reg1, pos1),
		(overlay_set_text, reg1, ":string"),
	]),
	
	("gpu_create_mesh_overlay",
	[
		(store_script_param, ":mesh", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		(store_script_param, ":size", 4),
		
		(set_fixed_point_multiplier, 1000),
		(create_mesh_overlay, reg1, ":mesh"),
		(position_set_x, pos2, ":pos_x"),
		(position_set_y, pos2, ":pos_y"),
		(overlay_set_position, reg1, pos2),
		(position_set_x, pos3, ":size"),
		(position_set_y, pos3, ":size"),
		(overlay_set_size, reg1, pos3),
	]),
	
	# script_gpu_create_item_overlay
	("gpu_create_item_overlay",
	[
		(store_script_param, ":item", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		(store_script_param, ":size", 4),
		
		(set_fixed_point_multiplier, 1000),
		(create_mesh_overlay_with_item_id, reg1, ":item"),
		(position_set_x, pos2, ":pos_x"),
		(position_set_y, pos2, ":pos_y"),
		(overlay_set_position, reg1, pos2),
		(position_set_x, pos3, ":size"),
		(position_set_y, pos3, ":size"),
		(overlay_set_size, reg1, pos3),
	]),
	
	("gpu_create_combo_button_overlay",
	[
		(store_script_param, ":pos_x", 1),
		(store_script_param, ":pos_y", 2),
		
		(set_fixed_point_multiplier, 1000),
		(create_combo_button_overlay, reg1),
		(position_set_x, pos1, ":pos_x"),
		(position_set_y, pos1, ":pos_y"),
		(overlay_set_position, reg1, pos1),
	]),
	
	# script_gpu_create_troop_image
	# Creates a mesh image based on troop ID, (x,y) position, size.
	# Input: troop_id, pos_x, pos_y, size
	# Output: reg1 - overlay
	("gpu_create_troop_image",
	[
		(store_script_param, ":troop_no", 1),
		(store_script_param, ":pos_x", 2),
		(store_script_param, ":pos_y", 3),
		(store_script_param, ":size", 4),

		(set_fixed_point_multiplier, 1000),
		(store_mul, ":cur_troop", ":troop_no", 2),
		(create_image_button_overlay_with_tableau_material, reg1, -1, "tableau_game_party_window", ":cur_troop"),
		#(create_mesh_overlay_with_tableau_material, reg1, -1, "tableau_troop_note_mesh", ":troop_no"),
		(position_set_x, pos2, ":pos_x"),
		(position_set_y, pos2, ":pos_y"),
		(overlay_set_position, reg1, pos2),
		(position_set_x, pos3, ":size"),
		(position_set_y, pos3, ":size"),
		(overlay_set_size, reg1, pos3),
		]
	),
		
	# script_gpu_create_image_button
	# Creates an image button based on normal and pressed mesh, (x,y) position, size.
	# Input: mesh_1, mesh_2, pos_x, pos_y, size
	# Output: reg1 - overlay
	("gpu_create_image_button",
	[
		(store_script_param, ":mesh_1", 1),
		(store_script_param, ":mesh_2", 2),
		(store_script_param, ":pos_x", 3),
		(store_script_param, ":pos_y", 4),
		(store_script_param, ":size", 5),

		(set_fixed_point_multiplier, 1000),
		(create_image_button_overlay, reg1, ":mesh_1", ":mesh_2"),
		(position_set_x, pos2, ":pos_x"),
		(position_set_y, pos2, ":pos_y"),
		(overlay_set_position, reg1, pos2),
		(position_set_x, pos3, ":size"),
		(position_set_y, pos3, ":size"),
		(overlay_set_size, reg1, pos3),
		]
	),
	
	# script_gpu_get_grid_position
	("gpu_get_grid_position",
	[
		(store_script_param, ":index", 1),
		(store_script_param, ":num_items", 2),
		(store_script_param, ":num_cols", 3),
		(store_script_param, ":col_width", 4),
		(store_script_param, ":col_height", 5),
		
		(store_mod, ":x", ":index", ":num_cols"),
		(store_mul, ":pos_x", ":x", ":col_width"),
		
		(store_sub, ":row", ":index", ":x"),
		(val_div, ":row", ":num_cols"),
		(val_sub, ":num_items", 1),
		(store_div, ":num_rows", ":num_items", ":num_cols"),
		(val_add, ":num_rows", 1),
		(store_sub, ":pos_y", ":num_rows", ":row"),
		(val_sub, ":pos_y", 1),
		(val_mul, ":pos_y", ":col_height"),
		
		(assign, reg0, ":pos_x"),
		(assign, reg1, ":pos_y"),
	]),
	
]