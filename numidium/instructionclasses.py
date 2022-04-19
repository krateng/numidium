import hashlib
import os
import subprocess as sp

from . import config

from doreah.io import col

import pyfomod

instruction_types = {}

class Instruction:

	stack_dependent = True #whether this needs to be rebuilt when the below stack has changed

	def __init_subclass__(cls):
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
		return f"{self.__class__.__name__} {self.args} {self.kwargs}"

	def get_folder(self):
		return self.build()

# abstract class for anything that just means using a preexisting folder
# on the fs
class OnFilesystem(Instruction):

	stack_dependent = False

	def get_abs_path(self):
		return os.path.join(config.PATHS['mods'],self.name)

# existing folder that will be used without any alteration
class FOLDER(OnFilesystem):

	def __init__(self,path):
		self.path = self.get_abs_path(path)

	def identifying_information(self):
		return [
			self.path,
			sp.run(['ls','-lhR',self.path],stdout=sp.PIPE).stdout
		]

	def get_folder(self):
		return self.path

# existing archive that will be used without any alteration
class ARCHIVE(OnFilesystem):
	def __init__(self,archive):
		self.archivepath = archive

# folder with FOMOD data
class FOMOD(OnFilesystem):
	def __init__(self,name,**files):
		self.name = name
		self.files = files

		self.fomod = pyfomod.parse(self.get_abs_path())

	def arguments(self):
		return (self.name,),{**self.files}

	def build(self):
		return ""


class INCLUDE(Instruction):
	def build(self):
		return ""


class GAME(FOLDER):
	def __init__(self,gamename):
		fullgamepath = os.path.join(config.PATHS['games'],config.GAMES['games'][gamename]['path'],path)
		super().init(gamepath)
