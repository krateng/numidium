import hashlib
import os
import subprocess as sp

from . import config
from . import brass
from . import build
from . import filesystem

from doreah.io import col

import pyfomod

instruction_types = {}

class Instruction:

	stack_dependent = True #whether this needs to be rebuilt when the below stack has changed

	def __init_subclass__(cls,abstract=False):
		if not abstract:
			instruction_types[cls.__name__] = cls

	def __init__(self,*args,**kwargs):
		self.args = args
		self.kwargs = kwargs

	# what to serialize into brass file
	def arguments(self):
		return self.args,self.kwargs

	def get_abs_path(self,path):
		return os.path.normpath(os.path.join(self.brassfile_context,path))

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
		return [self.args,self.kwargs]

	def __repr__(self):
		args, kwargs = self.arguments()
		return f"{self.__class__.__name__} {args} {kwargs}"

	def get_folder(self):
		return self.build()

# abstract class for anything that just means using a preexisting folder
# on the fs
class OnFilesystem(Instruction,abstract=True):

	stack_dependent = False




# any archive or folder that is in the mod folder
class Mod(OnFilesystem,abstract=True):
	def __init__(self,name):
		self.name = name
		self.path = self.get_abs_path()

	def get_abs_path(self):
		return os.path.join(config.PATHS['mods'],self.name)

	def arguments(self):
		return (self.name,),{}

# existing folder that will be used without any alteration
# generic path
class GenericFolder(OnFilesystem,abstract=True):
	def __init__(self,path):
		self.path = path

	def identifying_information(self):
		return [
			self.path,
			sp.run(['ls','-lhR',self.path],stdout=sp.PIPE).stdout
		]

	def build(self):
		return self.path

# mod without logic, just the data folder inside
class MODFOLDER(Mod):

	def identifying_information(self):
		return [
			self.path,
			sp.run(['ls','-lhR',self.path],stdout=sp.PIPE).stdout
		]

	def get_folder(self):
		return self.path

# existing archive that will be used without any alteration
class ARCHIVE(Mod):
	pass

# folder with FOMOD data
class FOMOD(Mod):
	def __init__(self,name,**files):
		self.name = name
		self.files = files

		self.fomod = pyfomod.parse(self.get_abs_path())

	def arguments(self):
		return (self.name,),{**self.files}

	def build(self):
		return ""


class INCLUDE(Instruction):
	def __init__(self,modlist):
		self.modlist = modlist
		self.brassfile = brass.BrassModlist(self.modlist)

	def build(self):

		layers = list(build.build_layers(self.brassfile.instructions[1:]))
		tmpfolder = os.path.join(config.PATHS['staging'],self.modlist)
		os.makedirs(tmpfolder,exist_ok=True)
		filesystem.mount(tmpfolder,layers,writelayer=None)
		return tmpfolder

	def arguments(self):
		return (self.modlist,),{}

	def identifying_information(self):
		return [
			self.modlist,
			*[i.identifying_information() for i in self.brassfile.instructions]
		]


class GAME(GenericFolder):
	def __init__(self,gamename):
		self.gamename = gamename
		fullgamepath = os.path.join(config.PATHS['games'],config.GAMES[gamename]['path'])
		super().__init__(fullgamepath)

	def arguments(self):
		return (self.gamename,),{}
