from module_constants import *
from header_common import *
from header_operations import *
from header_presentations import *

def gpu_create_text_overlay(pos_x, pos_y, str = "str_s0", text_size = 1000, size_x = 100, size_y = 27, flags = tf_left_align):
	return (call_script, "script_gpu_create_text_overlay", "str_s0", pos_x, pos_y, text_size, size_x, size_y, flags)
