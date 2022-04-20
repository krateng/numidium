import hashlib
import os
import subprocess as sp
from urllib.parse import quote, unquote

from . import config
from . import brass
from . import build
from . import filesystem
from . import stage_mod

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


# everything that corresponds to a folder on the fs, whether ready-built or not
class OnFilesystem(Instruction,abstract=True):
	def __init__(self,path):
		self.path = path

	def is_present(self):
		return os.path.exists(self.get_abs_path())

	def get_abs_path(self):
		return self.path

	def arguments(self):
		return (self.path,),{}


# everything that doesn't depend on the stack below it
class Independent(Instruction,abstract=True):

	stack_dependent = False


# everything that has no options, is just a fixed folder
class Static(Independent,abstract=True):
	def identifying_information(self):
		if self.is_present():
			return [
				self.get_abs_path(),
				sp.run(['ls','-lhR',self.get_abs_path()],stdout=sp.PIPE).stdout
			]
		else:
			return []

	def get_layer(self):
		if self.is_present():
			return {'type':'existing_path','path':self.get_abs_path()}
		else:
			#print(f"{self.get_abs_path()} does not exist")
			return {'type':'skip'}




# any archive or folder that is in the mod folder
class NumidiumManaged(OnFilesystem,abstract=True):
	def __init__(self,name):
		self.name = name

	def get_abs_path(self):
		return os.path.join(config.PATHS['mods'],self.name)

	def arguments(self):
		return (self.name,),{}


# arbitrary folder on the fs, not relative to numidium dir
class FOLDER(OnFilesystem,Static):
	pass


# modfolder
class MOD(NumidiumManaged,Independent):
	def __init__(self,name,options=None,options_deserialized=[]):
		self.name = name
		if options:
			options_deserialized = [unquote(o) for o in options.split("&")]
		self.options = options_deserialized

		try:
			self.fomod = pyfomod.parse(self.get_abs_path())
			self.is_fomod = True
		except:
			self.is_fomod = False

	def arguments(self):
		return (self.name,),{'options':"&".join(quote(o) for o in self.options)}

	def build(self):
		return stage_mod.apply_config(self.get_abs_path(),self.options)

	def identifying_information(self):
		if self.is_present():
			return [
				self.get_abs_path(),
				sp.run(['ls','-lhR',self.get_abs_path()],stdout=sp.PIPE).stdout,
				self.options
			]
		else:
			return []

	def get_layer(self):
		if self.is_present():
			if self.is_fomod:
				return  {'type':'file_map','files':self.build(),'srcfolder':self.get_abs_path()}
			else:
				return {'type':'existing_path','path':self.get_abs_path()}
		else:
			#print(f"{self.get_abs_path()} does not exist")
			return {'type':'skip'}


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

	def get_layer(self):
		return {'type':'existing_path','path':self.build()}

	def arguments(self):
		return (self.modlist,),{}

	def identifying_information(self):
		return [
			self.modlist,
			*[i.identifying_information() for i in self.brassfile.instructions]
		]


class GAME(OnFilesystem,Static):
	def __init__(self,gamename):
		self.gamename = gamename
		fullgamepath = os.path.join(config.PATHS['games'],config.GAMES[gamename]['path'])
		super().__init__(fullgamepath)

	def arguments(self):
		return (self.gamename,),{}
