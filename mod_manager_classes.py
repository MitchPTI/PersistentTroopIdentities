import collections, importlib

def list_of(cls):
	return lambda *obj_tuples: [cls(*obj_tuple) for obj_tuple in obj_tuples]

class ModObject(object):
	# Used in constructor, this method assigns values to fields and removes those used so as to leave only excess fields/values remaining
	def process_field_values(self, fields, values):
		last_field = None
		for field, value in zip(fields, values):
			if hasattr(self, "_field_classes") and field in self._field_classes:
				self._dict[field] = self._field_classes[field](*value)
			else:
				self._dict[field] = value
			
			values.remove(value)
			fields.remove(field)
			
			last_field = field
		
		# Special case; where the very last field is a sub-object (e.g. Sequence within Animation) and there are excess values, try instantiating those as sub-objects
		if values and hasattr(self, "_field_classes") and last_field in self._field_classes and not hasattr(self, "_optional_fields"):
			self._expand_last = True
			
			self._dict[last_field] = [self._dict[last_field]]
			self._dict[last_field].extend([self._field_classes[last_field](*value) for value in values])
			
			del values[:]
	
	def __init__(self, *args):
		self._dict = collections.OrderedDict()
		self._expand_last = False
		
		fields = list(self._required_fields)
		args = list(args)
		
		self.process_field_values(fields, args)
		
		# If all arguments have been exhausted but required fields still remain, not enough arguments have been supplied
		if fields:
			raise ValueError(
				"Not enough arguments supplied to {} constructor.\n{}".format(
					self.__class__.__name__, 
					", ".join(["{}: {}".format(field, value) for field, value in list(self._dict.iteritems()) + [(field, "NOT SPECIFIED") for field in fields]])
				)
			)
		
		optional_fields = self._optional_fields if hasattr(self, "_optional_fields") else []
		
		fields += optional_fields
		self.process_field_values(fields, args)
		
		# If all fields have now been exhausted - even optional ones - but arguments remain, too many arguments have been supplied
		if args:
			raise ValueError(
				"Too many arguments supplied to {} constructor. Expected a maximum of {} arguments, got {}.\n{}".format(
					self.__class__.__name__,
					len(self._required_fields) + len(optional_fields),
					len(self._required_fields) + len(optional_fields) + len(args),
					", ".join(["{}: {}".format(field, value) for field, value in list(self._dict.iteritems()) + [("Unexpected Argument", arg) for arg in args]])
				)
			)
	
	# Defining __iter__ allows conversion to tuple/list, for returning objects to their original form
	def __iter__(self):
		values = list(self._dict.values()[:-1]) + [tuple(value) for value in self._dict.values()[-1]] if self._expand_last else self._dict.values()
		for value in values:
			if isinstance(value, list) and value and isinstance(value[0], ModObject):
				yield [tuple(element) for element in value]
			elif isinstance(value, ModObject):
				yield tuple(value)
			else:
				yield value
	
	# Allow attributes to be accessed with .<attr_name>, e.g. script.operations
	def __getattr__(self, attr):
		try:
			super(ModObject, self).__getattr__(attr)
		except AttributeError as e:
			if attr in self._dict:
				return self._dict[attr]
			else:
				raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, attr))
	
	# Allow attributes to be set with .<attr_name>, e.g. script.operations = []
	def __setattr__(self, attr, value):
		if attr.startswith("_"):
			self.__dict__[attr] = value
		else:
			self._dict[attr] = value
	
	# Allow attributes to be accessed with numeric indexes as if they were still tuples/lists and also with attribute name in square brackets (good for if attribute name is stored in a variable for some reason), e.g. script[1] or script["operations"]
	def __getitem__(self, item):
		if isinstance(item, int):
			return self._dict[self._dict.keys()[item]]
		else:
			return self._dict[item]
	
	# Allow attributes to be set with numeric indexes as if they were still tuples/lists and also with attribute name in square brackets (good for if attribute name is stored in a variable for some reason), e.g. script[1] = [] or script["operations"] = []
	def __setitem__(self, item, value):
		if isinstance(item, int):
			self._dict[self._dict.keys()[item]] = value
		else:
			self._dict[item] = value
	
	def __str__(self):
		return "{}<{}>".format(self.__class__.__name__, ", ".join(["{}: {}".format(field, value) for field, value in self._dict.iteritems()]))
	
	def __repr__(self):
		return str(self)

class Animation(ModObject):
	class Sequence(ModObject):
		_required_fields = ("duration", "resource", "begin_frame", "end_frame", "sequence_flags")
		_optional_fields = ("unknown_1", "unknown_2", "unknown_3")
	
	_required_fields = ("id", "flags", "master_flags", "sequences")
	_field_classes = {"sequences": Sequence}
		
class Dialog(ModObject):
	_required_fields = ("partner", "state", "conditions", "text", "end_state", "consequences")
	_optional_fields = ("voice_over")

class Faction(ModObject):
	_required_fields = ("id", "name", "flags", "coherence", "relations", "ranks")
	_optional_fields = ("colour")

class InfoPage(ModObject):
	_required_fields = ("id", "name", "text")

class Item(ModObject):
	class Mesh(ModObject):
		_required_fields = ("name", "modbits")
	
	_required_fields = ("id", "name", "meshes", "flags", "capabilities", "value", "stats", "modbits")
	_optional_fields = ("triggers", "factions")
	_field_classes = {"meshes": list_of(Mesh)}

class GameMenu(ModObject):
	class MenuOption(ModObject):
		_required_fields = ("id", "conditions", "text", "consequences")
		_optional_fields = ("alt_text")
	
	_required_fields = ("id", "flags", "text", "mesh_name", "operations", "options")
	_field_classes = {"options": list_of(MenuOption)}

class MapIcon(ModObject):
	_required_fields = ("id", "flags", "name", "scale", "sound")
	_optional_fields = ("offset_x", "offset_y", "offset_z")

class Mesh(ModObject):
	_required_fields = ("id", "flags", "resource", "translate_x", "translate_y", "translate_z", "rotate_x", "rotate_y", "rotate_z", "scale_x", "scale_y", "scale_z")

class MissionTemplate(ModObject):
	class SpawnRecord(ModObject):
		_required_fields = ("entry_no", "spawn_flags", "alter_flags", "ai_flags", "num_troops", "equipment")
	
	_required_fields = ("id", "flags", "type", "text", "spawn_records", "triggers")
	_field_classes = {"spawn_records": list_of(SpawnRecord)}

class Music(ModObject):
	_required_fields = ("id", "file", "flags", "continue_flags")

class ParticleSystem(ModObject):
	class Key(ModObject):
		_required_fields = ("time", "magnitude")
	
	_required_fields = ("id", "flags", "mesh_name", "particles_per_second", "particle_life", "damping", "gravity_strength", "turbulence_size", "turbulence_strength")
	_field_classes = {}
	for key in ("alpha", "red", "green", "blue", "scale"):
		_required_fields += (key + "_key_1", key + "_key_2")
		_field_classes[key + "_key_1"] = Key
		_field_classes[key + "_key_2"] = Key
	
	_required_fields += ("emit_box_size", "emit_velocity", "emit_dir_randomness")
	_optional_fields = ("particle_rotation_speed", "particle_rotation_damping")

class Party(ModObject):
	class Stack(ModObject):
		_required_fields = ("troop_id", "num_troops", "member_flags")
	
	_required_fields = ("id", "name", "flags", "menu", "template", "faction", "personality", "ai_behaviour", "ai_target_party", "initial_coordinates", "stacks")
	_optional_fields = ("direction")
	_field_classes = {"stacks": list_of(Stack)}

class PartyTemplate(ModObject):
	class Stack(ModObject):
		_required_fields = ("troop_id", "min", "max")
		_optional_fields = ("member_flags")
	
	_required_fields = ("id", "name", "flags", "menu", "faction", "personality", "stacks")
	_field_classes = {"stacks": list_of(Stack)}

class PostFX(ModObject):
	_required_fields = ("id", "flags", "tonemap_operator_type", "shader_parameters_1", "shader_parameters_2", "shader_parameters_3")

class Presentation(ModObject):
	_required_fields = ("id", "flags", "background_mesh", "triggers")

class Quest(ModObject):
	_required_fields = ("id", "name", "flags", "description")

class SceneProp(ModObject):
	_required_fields = ("id", "flags", "mesh_name", "physics_object_name", "triggers")

class Scene(ModObject):
	_required_fields = ("id", "flags", "mesh_name", "body_name", "min_pos", "max_pos", "water_level", "terrain_code", "other_scenes", "chest_troops")
	_optional_fields = ("alt_id")

class Script(ModObject):
	_required_fields = ("id", "operations")

class SimpleTrigger(ModObject):
	_required_fields = ("check_interval", "operations")

class Skill(ModObject):
	_required_fields = ("id", "name", "flags", "max_level", "description")

class Skin(ModObject):
	_required_fields = ("id", "flags", "body_mesh", "calf_mesh", "hand_mesh", "head_mesh", "face_keys", "hair_meshes", "beard_meshes", "hair_textures", "beard_textures", "face_textures", "voices", "skeleton_name", "scale", "blood_particles_1", "blood_particles_2")
	_optional_fields = ("face_key_constraints")

class Sound(ModObject):
	_required_fields = ("id", "flags", "files")

class String(ModObject):
	_required_fields = ("id", "string")

class TableauMaterial(ModObject):
	_required_fields = ("id", "flags", "sample_material", "width", "height", "mesh_min_x", "mesh_min_y", "mesh_max_x", "mesh_max_y", "operations")

class Trigger(ModObject):
	_required_fields = ("check_interval", "delay_interval", "rearm_interval", "conditions", "consequences")

class Troop(ModObject):
	_required_fields = ("id", "name", "plural_name", "flags", "scene", "reserved", "faction", "inventory", "attributes", "weapon_proficiencies", "skills", "face_code_1")
	_optional_fields = ("face_code_2", "troop_image", "upgrade_1", "upgrade_2")

object_classes = {
	"animations": Animation
	, "dialogs": Dialog
	, "factions": Faction
	, "game_menus": GameMenu
	, "info_pages": InfoPage
	, "items": Item
	, "map_icons": MapIcon
	, "meshes": Mesh
	, "mission_templates": MissionTemplate
	, "music": Music
	, "particle_systems": ParticleSystem
	, "parties": Party
	, "party_templates": PartyTemplate
	, "postfx": PostFX
	, "presentations": Presentation
	, "quests": Quest
	, "scene_props": SceneProp
	, "scenes": Scene
	, "scripts": Script
	, "simple_triggers": SimpleTrigger
	, "skills": Skill
	, "skins": Skin
	, "sounds": Sound
	, "strings": String
	, "tableau_materials": TableauMaterial
	, "triggers": Trigger
	, "troops": Troop
}