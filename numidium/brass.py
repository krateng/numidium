import yaml
import os

from . import config
from . import instructionclasses



class BrassModlist:

	def __init__(self,name):
		self.file = os.path.join(config.PATHS['modlists'],f"{name}.brass")
		self.game = None
		self.instructions = []
		try:
			self.load()
		except FileNotFoundError:
			pass

	def load(self):
		with open(self.file,'r') as fd:
			for line in fd:
				line = line[:-1] # remove newline
				if not line: continue # empty lines
				if line.startswith('#'): continue # comments

				instruction,argsstring = line.split(" ",1)
				# object saves the game its associated to separately
				# but also leave it in the instruction stack
				if instruction == 'GAME':
					assert self.game is None
					self.game = argsstring

				allargs = [part for part in argsstring.split(',')]
				args = [part for part in allargs if not "=" in part]
				kwargs = dict(part.split("=") for part in allargs if "=" in part)

				self.instructions.append(
					instructionclasses.instruction_types[instruction](*args,**kwargs)
				)

			if self.game is None:
				print("Not a valid brassfile, missing Game!")

	def save(self):
		with open(self.file,'w') as fd:
			for i in self.instructions:
				args,kwargs = i.arguments()
				argsstring = ','.join([
					*args,
					*['='.join([k,str(v)]) for k,v in kwargs.items()]
				])
				fd.write(i.__class__.__name__ + " " + argsstring)
			fd.write("\n")

	def add_instruction(self,i):
		self.instructions.append(i)
