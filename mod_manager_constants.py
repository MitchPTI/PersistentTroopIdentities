'''
This module brings together all constants from all the mods specified in mod_manager_options.

This allows modders to add their new constants to {mod_prefix}_constants files and have it all be brought together by simply adding "from mod_manager_options import *" to module_constants (this is done automatically by the installer).
If the same constant name is used in multiple files, the order in mod_manager_options.mods will apply (later ones will override earlier ones). For example:

mods = [
	"mod_1",
	"mod_2"
]

If mod_1_constants and mod_2_constants both have the variable x, mod_2_constants.x will be imported.

Care has been taken with the names of variables used in the process to avoid any collisions. If for some reason a mod assigns a constant to any of __constants, __constant_name, __constant_value or __sys, there could be unexpected results.
'''

from importlib import import_module
from mod_manager_options import mods

__constants = {}

for mod in mods:
	module_name = mod + "_constants"
	try:
		try:
			module = import_module(module_name)
		except ImportError as e:
			error_module = str(e).split(" ")[-1]
			if error_module == module_name:
				#print "Hmmm, couldn't find {}".format(module_name)
				continue
			else:
				raise e
		
		for attr in dir(module):
			__constants[attr] = getattr(module, attr)
			#print "Getting {}".format(attr)
	except Exception as e:
		print "Uh oh, something went wrong trying to import from {}.\n{}: {}".format(module_name, e.__class__.__name__, str(e))

for __attr in globals().keys():
	if not __attr.startswith("__"):
		del globals()[__attr]

for __constant_name, __constant_value in __constants.iteritems():
	import sys as __sys
	globals()[__constant_name] = __constant_value

for __attr in ("__constants", "__constant_name", "__constant_value", "__sys"):
	if __attr in globals():
		del globals()[__attr]

del globals()["__attr"]