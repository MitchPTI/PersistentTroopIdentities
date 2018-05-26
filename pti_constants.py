from header_operations import call_script

class Individual:
	attribute_offsets = {}
	attribute_bitshifts = {}
	attribute_sizes = {}
   
	@classmethod
	def set_attribute_sizes(cls, attribute_sizes):
		attribute_sizes = list(attribute_sizes.iteritems())
		attribute_sizes.sort(key=lambda pair: pair[1], reverse=True)
		slots = []
		for attribute, size in attribute_sizes:
			eligible_slots = [slot for slot in slots if 63 - sum([pair[1] for pair in slot]) >= size]
			if eligible_slots:
				eligible_slots[0].append((attribute, size))
			else:
				slots.append([(attribute, size)])
	   
		for offset, slot in enumerate(slots):
			bitshift = 0
			for attribute, size in slot:
				cls.attribute_offsets[attribute] = offset
				cls.attribute_bitshifts[attribute] = bitshift
				cls.attribute_sizes[attribute] = size
			   
				bitshift += size
		
		cls.num_attribute_slots = max(cls.attribute_offsets.values()) + 1
		cls.attribute_slots_bitshift = 10
		cls.attributes_slot_max = (2 ** cls.attribute_slots_bitshift) - cls.num_attribute_slots
   
	@classmethod
	def get(cls, individual, attribute):
		return (call_script, "script_pti_individual_get_attribute", individual, cls.attribute_offsets[attribute], cls.attribute_bitshifts[attribute], (2 ** cls.attribute_sizes[attribute]) - 1)
	
	@classmethod
	def set(cls, individual, attribute, value):
		return (call_script, "script_pti_individual_set_attribute", individual, cls.attribute_offsets[attribute], cls.attribute_bitshifts[attribute], (2 ** cls.attribute_sizes[attribute]) - 1, ((2 ** 64) - 1) ^ (((2 ** cls.attribute_sizes[attribute]) - 1) << cls.attribute_bitshifts[attribute]), value)

Individual.set_attribute_sizes({
	"troop_type": 14
	, "home": 14
	, "name": 12
})

troop_slots = (200, [
	"nps_slot_troop_stack_overlay"
])

array_slots = (0, [
	"slot_array_size"
	, "slot_array_next_array"
])

faction_slots = (250, [
	"slot_faction_boy_names_begin"
	, "slot_faction_boy_names_end"
	, "slot_faction_girl_names_begin"
	, "slot_faction_girl_names_end"
])

for (start_index, object_slots) in [array_slots, faction_slots, troop_slots]:
	for i, slots in enumerate(object_slots):
		if not hasattr(slots, "__iter__"):
			slots = [slots]
		
		for slot in slots:
			locals()["pti_" + slot] = start_index + i

faction_naming_regions = {
	"fac_kingdom_1": ["teutonic", "german", "french", "dutch"] # Swadia
	, "fac_kingdom_2": ["russian", "lithuanian", "polish", "czechandslovak", "ukrainian", "finnish"] # Vaegirs
	, "fac_kingdom_3": ["turkish", "mongolian", "persian", "kazakh"] # Khergits
	, "fac_kingdom_4": ["scandinavian", "norwegian", "danish", "finnish"] # Nords
	, "fac_kingdom_5": ["italian", "swiss", "french"] # Rhodok
	, "fac_kingdom_6": ["persian", "arabic", "egyptian"] # Sarranids
	, "default": ["english"]
}