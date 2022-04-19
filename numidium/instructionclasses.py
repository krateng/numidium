import hashlib
import os
import subprocess as sp

import pyfomod

from . import config

from doreah.io import col

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



class InstructionWithArgs(Instruction):

	def __init__(self,argsstring,brassfile_context=os.getcwd()):
		self.rawargsstring = argsstring
		self.brassfile_context = brassfile_context

		args = [part.split('=') for part in argsstring.split(',')]
		kwargs = {k:v for k,v in args}

		self.init(kwargs)

	def init(self,kwargs):
		self.kwargs = kwargs


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

class MODARCHIVE(Instruction):
	# archive that just has the Data contents in it
	def init(self,archive):
		self.archivepath = archive


class FOMOD(InstructionWithArgs):
	def init(self,kwargs):
		if 'folder' in kwargs:
			self.folder = kwargs['folder']
		elif 'archive' in kwargs:
			self.archive = kwargs['archive']

		self.fomod = pyfomod.parse(self.folder)


	def build(self):

		from . import install

		install.install(self.fomod)
		return ""


class INCLUDE(Instruction):
	def build(self):
		return ""
