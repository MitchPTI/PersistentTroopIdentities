'''
Updates all module_*.py files to merge in code from any of the mods listed in mod_manager_options.

No backups are created prior to making changes, make sure to do this yourself and use at your own risk.
'''

import os

from mod_manager_options import object_types

list_names = {
	"music": "tracks"
	, "postfx": "postfx_params"
	, "tableau_materials": "tableaus"
}

def install(obj_type):
	module_name = "module_{}.py".format(obj_type)
	if os.path.isfile(module_name):
		with open(module_name, "a+") as module_file:
			if obj_type == "constants":
				new_lines = [
					"from mod_manager_constants import *"
				]
			else:
				try:
					list_name = list_names[obj_type]
				except KeyError:
					list_name = obj_type
				
				new_lines = [
					"import mod_manager"
					, "{} = mod_manager.merge(\"{}\", {})".format(obj_type, obj_type, list_name)
				]
			
			if new_lines[0] not in [line.strip() for line in module_file.readlines()]:
				module_file.write("\n\n{}".format("\n".join(new_lines)))
				print "Successfully installed mod_manager in {}".format(module_name)
			else:
				print "mod_manager already installed in {}".format(module_name)
	else:
		print "Could not find {}".format(module_name)

print "INSTALLING MOD_MANAGER\n"

for obj_type in object_types:
	install(obj_type)

print "\nFINISHED\n"

raw_input("Press any key to close")