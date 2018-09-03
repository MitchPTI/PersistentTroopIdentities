import importlib, logging, sys, collections, os

import mod_manager_options as options
from mod_manager_logging import BuildLogger
from mod_manager_classes import object_classes

class ModObjContainer(object):
	def __init__(self, obj_type, cls, *args):
		self._obj_type = obj_type
		self._obj_cls = cls
		
		self._items = collections.OrderedDict() if cls._required_fields[0] == "id" else []
		
		if cls:
			self.extend([cls(*arg) for arg in args])
		else:
			self.extend(args)
	
	def __getitem__(self, item):
		try:
			return self._items[item]
		except KeyError:
			raise AttributeError("There are no {} with an ID of {}".format(self._obj_type, item))
	
	def __setitem__(self, item, value):
		self._items[item] = value
	
	def __contains__(self, key):
		return key in self._items
	
	def __getattr__(self, attr):
		return self[attr]
	
	def __setattr__(self, attr, value):
		if not attr.startswith("_"):
			self[attr] = value
		else:
			self.__dict__[attr] = value
	
	def __iter__(self):
		items = self._items.values() if isinstance(self._items, collections.OrderedDict) else self._items
		for item in items:
			yield item
	
	def __str__(self):
		return "\n".join([str(item) for item in self._items.values()])
	
	def __repr__(self):
		return str(self)
	
	def append(self, item):
		if not isinstance(item, self._obj_cls):
			item = self._obj_cls(*item)
		
		if isinstance(self._items, collections.OrderedDict):
			try:
				item_id = item["id"]
			except Exception:
				raise ValueError("Tried to append an invalid object to '{}' instance. ".format(self.__class__.__name__) + \
								 "Valid objects must be tuples or lists that have an ID as their first element. " + \
								 "Invalid object: {}".format(item))
			
			self._items[item_id] = item
		else:
			self._items.append(item)
	
	def extend(self, items):
		for item in items:
			self.append(item)

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