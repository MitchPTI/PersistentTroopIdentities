from header_operations import call_script
from collections import OrderedDict
from module_info import export_dir

import re
try:
	with open(export_dir + "/module.ini") as fh:
		lines = fh.readlines()
	
	module_ini_dict = dict([re.split("\s*=\s*", line) for line in lines if "=" in line])
	for key, value in module_ini_dict.iteritems():
		module_ini_dict[key] = value.strip()
		if "#" in value:
			module_ini_dict[key] = re.sub("\s*#.*$", "", value).strip()
	
	troop_xp_multiplier = float(module_ini_dict["regulars_xp_multiplier"]) if "regulars_xp_multiplier" in module_ini_dict else 1.0
except Exception as e:
	print "Something went wrong trying to extract troop xp multiplier from module.ini, setting to 1"
	troop_xp_multiplier = 1.0

def mask(bits):
	return (2 ** bits) - 1

## Array/Linked List constants
pti_list_node_bits = 20
pti_list_node_value_bits = 63 - pti_list_node_bits * 2	# From available 63 bits, leave room only for the 2 neighbour nodes

pti_array_slot_max = 2 ** pti_list_node_bits

pti_list_next_node_bitshift = pti_list_node_value_bits
pti_list_prev_node_bitshift = pti_list_next_node_bitshift + pti_list_node_bits

pti_list_node_mask = mask(pti_list_node_bits)
pti_list_node_value_mask = mask(pti_list_node_value_bits)

pti_list_next_node_clear_mask = mask(64) ^ (mask(pti_list_node_bits) << pti_list_node_value_bits)
pti_list_prev_node_clear_mask = mask(64) ^ (mask(pti_list_node_bits) << (pti_list_node_value_bits + pti_list_node_bits))
pti_list_node_value_clear_mask = mask(64) ^ (mask(pti_list_node_bits) << (pti_list_node_value_bits + pti_list_node_bits))

## Individual Reference constants
pti_reference_array_bitshift = 10
pti_reference_slot_mask = (2 ** pti_reference_array_bitshift) - 1

## The Individual class exists for the sake of defining the get and set parameters for any given attribute
## The attributes have to be stored in slots, but it would be a tremendous waste to just have one slot per attribute.
## Instead, we can pack multiple attributes into a single slot through bit-wise operations (TaleWorlds uses the same tactic on stats/skills of troops)
## Slots appear to be able to store up to 63 bits, the number of bits for each attribute must be defined to see how many can fit in a given slot.
## As it turns out, working out how to fit each attribute into a slot such that miminal slots are used is an example of bin-packing, which is an NP-hard problem.
## Thus, we must use an approximation algorithm, in this case the simple First-Fit Decreasing algorith.
## You can find some tutorials on YouTube if you wanna learn more about it, just search First-Fit Decreasing Bin Packing
class Individual:
	attribute_offsets = {}
	attribute_bitshifts = {}
	attribute_sizes = {}
	
	@classmethod
	def set_attribute_sizes(cls, attribute_sizes):
		# Sort the attributes by size (decreasing)
		attribute_sizes = list(attribute_sizes.iteritems())
		attribute_sizes.sort(key=lambda pair: pair[1], reverse=True)
		attribute_sizes.sort(key=lambda pair: pair[0], reverse=True)
		
		slots = []
		# For each attribute, find the first eligible slot it can fit into and add it to the given slot
		for attribute, size in attribute_sizes:
			eligible_slots = [slot for slot in slots if 63 - sum([pair[1] for pair in slot]) >= size]
			if eligible_slots:
				eligible_slots[0].append((attribute, size))
			else:
				slots.append([(attribute, size)])
		
		# For each attribute define the slot offset (i.e. 0 for the first slot, 1 for the second, so on) and the bitshift and size required to extract it from the slot
		for offset, slot in enumerate(slots):
			bitshift = 0
			for attribute, size in slot:
				cls.attribute_offsets[attribute] = offset
				cls.attribute_bitshifts[attribute] = bitshift
				cls.attribute_sizes[attribute] = size
				
				bitshift += size
		
		# Define the number of slots required per individual
		cls.num_attribute_slots = max(cls.attribute_offsets.values()) + 1
		cls.attribute_slots_bitshift = 10
		cls.attributes_slot_max = (2 ** cls.attribute_slots_bitshift) - cls.num_attribute_slots
	
	@classmethod
	def get(cls, individual, attribute):
		return (call_script, "script_pti_individual_get_attribute", individual, cls.attribute_offsets[attribute], cls.attribute_bitshifts[attribute], (2 ** cls.attribute_sizes[attribute]) - 1)
	
	@classmethod
	def set(cls, individual, attribute, value):
		return (call_script, "script_pti_individual_set_attribute", individual, cls.attribute_offsets[attribute], cls.attribute_bitshifts[attribute], (2 ** cls.attribute_sizes[attribute]) - 1, ((2 ** 64) - 1) ^ (((2 ** cls.attribute_sizes[attribute]) - 1) << cls.attribute_bitshifts[attribute]), value)

TROOP_BITS = 14
ITEM_BITS = 14
PARTY_BITS = 12
NAME_BITS = 12
NUM_DAYS_BITS = 14
FACE_KEY_BITS = 6
TOTAL_KILLS_BITS = 14
BATTLE_KILLS_BITS = 10
TIMES_WOUNDED_BITS = 7	# 7 bits gives a maximum of 127 times. Even at max surgery there is only a 0.00000000024% chance of a troop surviving this many times
XP_BITS = 30
CLASS_BITS = 4

Individual.set_attribute_sizes({
	"troop_type": TROOP_BITS
	, "home": PARTY_BITS
	, "name": NAME_BITS
	, "day_joined": NUM_DAYS_BITS
	, "base_weapons": ITEM_BITS * 4
	, "base_armour": ITEM_BITS * 4
	, "base_horse": ITEM_BITS
	, "looted_weapons": ITEM_BITS * 4
	, "looted_armour": ITEM_BITS * 4
	, "looted_horse": ITEM_BITS
	, "hair": FACE_KEY_BITS
	, "beard": FACE_KEY_BITS
	, "face_texture": FACE_KEY_BITS
	, "hair_texture": FACE_KEY_BITS
	, "hair_colour": FACE_KEY_BITS
	, "age": FACE_KEY_BITS
	#, "skin": FACE_KEY_BITS
	, "is_wounded": 1
	, "kill_count": TOTAL_KILLS_BITS
	, "knock_out_count": TOTAL_KILLS_BITS
	, "most_kills": BATTLE_KILLS_BITS
	, "best_kill": TROOP_BITS
	, "times_wounded": TIMES_WOUNDED_BITS
	, "xp": XP_BITS
	, "class": CLASS_BITS
	, "class_overridden": 1
})

troop_slots = (200, [
	"nps_slot_troop_stack_overlay"
	, "slot_troop_individual"
])

agent_slots = (50, [
	"slot_agent_individual"
	, "slot_agent_best_kill"
	, "slot_agent_best_kill_level"
	, "slot_agent_xp_gained"
])

array_slots = (0, [
	"slot_array_next_array"
	, "slot_array_size"
	, "slot_list_head"
])

faction_slots = (250, [
	"slot_faction_boy_names_begin"
	, "slot_faction_boy_names_end"
	, "slot_faction_girl_names_begin"
	, "slot_faction_girl_names_end"
])

party_slots = (500, [
	"slot_party_individuals"
])

for (start_index, object_slots) in [troop_slots, agent_slots, array_slots, faction_slots, party_slots]:
	for i, slots in enumerate(object_slots):
		if not hasattr(slots, "__iter__"):
			slots = [slots]
		
		for slot in slots:
			locals()["pti_" + slot] = start_index + i

pti_array_slots_start = max([locals()["pti_" + slot] for slot in array_slots[1]]) + 1

faction_naming_regions = OrderedDict([
	("fac_kingdom_1", ["teutonic", "german", "french", "dutch"]) # Swadia
	, ("fac_kingdom_2", ["russian", "lithuanian", "polish", "czechandslovak", "ukrainian", "finnish"]) # Vaegirs
	, ("fac_kingdom_3", ["turkish", "mongolian", "persian", "kazakh"]) # Khergits
	, ("fac_kingdom_4", ["scandinavian", "norwegian", "danish", "finnish"]) # Nords
	, ("fac_kingdom_5", ["italian", "swiss", "french"]) # Rhodok
	, ("fac_kingdom_6", ["persian", "arabic", "egyptian"]) # Sarranids
	, ("default", ["english"])
])

pti_nps_containers = ("upper_left", "upper_right", "lower_left", "lower_right")
pti_nps_objects = ("button", "highlight", "text", "image")