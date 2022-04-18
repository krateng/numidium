import hashlib
import os
import subprocess as sp

from . import config

instruction_types = {}

class Instruction:

	stack_dependent = True #whether this needs to be rebuilt when the below stack has changed

	def __init_subclass__(cls):
		instruction_types[cls.__name__] = cls

	def __init__(self,argsstring,brassfile_context=os.getcwd()):
		self.rawargsstring = argsstring
		self.brassfile_context = brassfile_context
		self.init(argsstring)

	def get_abs_path(self,path):
		return os.path.normpath(os.path.join(self.brassfile_context,path))

	def init(self,argsstring):
		self.argsstring = argsstring

	def identify_with_context(self,context):
		m = hashlib.sha256()
		m.update(bytes(str(self.identify()),'utf-8'))
		if self.stack_dependent:
			m.update(bytes(str(context),'utf-8'))
		return m.hexdigest()

	def identify(self):
		m = hashlib.sha256()
		m.update(bytes(self.__class__.__name__,'utf-8'))
		for i in self.identifying_information():
			m.update(bytes(str(i),'utf-8'))
		return m.hexdigest()

	def identifying_information(self):
		return [self.rawargsstring]

	def __repr__(self):
		return f"{self.__class__.__name__} {self.rawargsstring}"

	def get_folder(self):
		return self.build()


class FOLDER(Instruction):

	stack_dependent = False

	def init(self,path):
		self.path = self.get_abs_path(path)

	def identifying_information(self):
		return [
			self.path,
			sp.run(['ls','-lhR',self.path],stdout=sp.PIPE).stdout
		]

	def get_folder(self):
		return self.path

class GAMEFOLDER(FOLDER):
	def init(self,path):
		fullgamepath = os.path.join(config.PATHS['games_folder'],path)
		super().init(fullgamepath)


class GAME(GAMEFOLDER):
	def init(self,gamename):
		gamepath = config.GAMES[gamename]
		super().init(gamepath)
