import logging, sys

class BuildLogger(logging.Logger):
	fh = logging.FileHandler("build.log", mode="w")
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter("%(filename)s LINE %(lineno)s %(levelname)s: %(message)s"))
	
	#sh = logging.StreamHandler(stream=sys.stdout)
	#sh.setLevel(logging.ERROR)
	#sh.setFormatter(logging.Formatter("%(message)s"))
	
	@classmethod
	def getLogger(cls, name):
		logger = logging.getLogger(name)
		logger.setLevel(logging.DEBUG)
		logger.addHandler(cls.fh)
		#logger.addHandler(cls.sh)
		
		return logger