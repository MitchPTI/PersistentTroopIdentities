'''
In this module options can be set, such as which mods will be merged in.
'''

# All mods to be merged must be listed here (e.g. if "test" is added, code from files like test_scripts.py will be merged)
mods = [
	"pti"
	, "gpu"
]

# The below list tells the installer which modules to install mod_manager in (e.g. "animations" for module_animations.py). There is unlikely to be any reason to ever change this, but you can if you wish.
object_types = [
	"animations"
	, "constants"
	, "dialogs"
	, "factions"
	, "game_menus"
	, "info_pages"
	, "items"
	, "map_icons"
	, "meshes"
	, "mission_templates"
	, "music"
	, "particle_systems"
	, "parties"
	, "party_templates"
	, "postfx"
	, "presentations"
	, "quests"
	, "scene_props"
	, "scenes"
	, "scripts"
	, "simple_triggers"
	, "skills"
	, "skins"
	, "sounds"
	, "strings"
	, "tableau_materials"
	, "triggers"
	, "troops"
]