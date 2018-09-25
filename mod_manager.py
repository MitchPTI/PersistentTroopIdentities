import importlib, logging, sys, collections, os

import mod_manager_options as options
from mod_manager_logging import BuildLogger
from mod_manager_classes import object_classes

# The ModObjContainer is a collection class for mod objects (e.g. scripts, troops, etc).
# It stores the data internally within an ordered dictionary and can be treated interchangeably as either a dict (default) or list.
# When list methods are called, it gets the objects as a list using the dict values method, applies the method to that list and then
# reconstructs the ordered dictionary, extracting each mod object's ID to be used as the key.
# Any new objects added as tuples/lists will be automatically converted to the relevant class if applicable.
# For object types with no ID, the objects will be stored in a list and dict methods will not work.
class ModObjContainer(object):
	def __init__(self, obj_type, cls, *args):
		self._obj_type = obj_type
		self._obj_cls = cls
		
		self._items = collections.OrderedDict() if cls and cls._required_fields[0] == "id" else []
		
		if cls:
			self.extend([cls(*arg) for arg in args])
		else:
			self.extend(args)
	
	def wrap_list_method(self, method_name):
		items_list = self._items.values()
		def method_wrapper(*args, **kwargs):
			result = getattr(items_list, method_name)(*args, **kwargs)
			self._items = OrderedDict([(item[0], self._obj_cls(*item) if not isinstance(item, self._obj_cls) else item) 
						   for item in items_list])
			return result
		
		return method_wrapper
	
	def __getattr__(self, attr):
		if hasattr(self._items, attr):
			return getattr(self._items, attr)
		elif hasattr(list, attr) and isinstance(self._items, collections.OrderedDict):
			value = getattr(self._items.values(), attr)
			if callable(value):
				value = self.wrap_list_method(attr)
			
			return value
		else:
			raise AttributeError("{} has no attribute {}".format(self.__class__.__name__, attr))
	
	def __getitem__(self, item):
		if isinstance(self._items, collections.OrderedDict) and isinstance(item, int):
			return self._items.values()[item]
		else:
			return self._items[item]
	
	def __setitem__(self, item, value):
		if self._obj_cls and not isinstance(item, self._obj_cls):
			self._items[item] = self._obj_cls(*item)
		else:
			self._items[item] = item
	
	def __delitem__(self, item):
		if isinstance(self._items, collections.OrderedDict) and isinstance(item, int):
			del self._items[self._items.keys()[item]]
		else:
			del self._items[item]
	
	def __contains__(self, item):
		return item in self._items
	
	def __iter__(self):
		items = self._items.values() if isinstance(self._items, collections.OrderedDict) else self._items
		for item in items:
			yield item
	
	def append(self, obj):
		if self._obj_cls and not isinstance(obj, self._obj_cls):
			obj = self._obj_cls(*obj)
		
		if isinstance(self._items, collections.OrderedDict):
			self._items[obj[0]] = obj
		else:
			self._items.append(obj)
	
	def extend(self, objects):
		for obj in objects:
			self.append(obj)

logger = BuildLogger.getLogger(__name__)

def merge(obj_type, objects):
	logger.debug("Creating {} container from module_{}".format(obj_type, obj_type))
	objects = ModObjContainer(obj_type, object_classes[obj_type], *objects)
	
	for mod in options.mods:
		module_name = "{}_{}".format(mod, obj_type)
		logger.debug("Attempting to import {} from {}".format(obj_type, module_name))
		try:
			module = importlib.import_module(module_name)
		except ImportError as e:
			error_module = str(e).split(" ")[-1]
			if error_module == module_name:
				logger.debug("{} not found".format(module_name))
			else:
				logger.exception("Exception arose in {}".format(module_name))
			continue
		except Exception:
			print "Exception arose in {}, refer to log for details.".format(module_name)
			logger.exception("Exception arose in {}".format(module_name))
			continue
		
		logger.debug("Importing {} from {} was successful, attempting to merge {}".format(obj_type, module_name, obj_type))
		if hasattr(module, "merge") and callable(module.merge):
			try:
				module.merge(objects)
			except Exception:
				print "Merging {} from {} failed, refer to log for details.".format(obj_type, module_name)
				logger.exception("Exception arose in merging {} from {}".format(obj_type, module_name))
				continue
		elif hasattr(module, obj_type) and hasattr(getattr(module, obj_type), "__iter__"):
			objects.extend(getattr(module, obj_type))
		else:
			logger.error("{} does not have the merge function or an iterable named {}".format(module_name, obj_type))
			continue
		
		logger.info("Successfully merged {} from {}".format(obj_type, module_name))
	
	return [tuple(object) for object in objects]
