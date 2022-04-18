import yaml
import os

from . import config



# loads instruction dicts from brassfile, also specifically extracts game (which remains also an instruction)
def load_brassfile(inputf):
	gamefolder = None
	instructions = []
	with open(inputf) as inputfd:

		for line in inputfd:
			line = line[:-1] # remove newline
			if not line: continue # empty lines
			if line.startswith('#'): continue # comments

			instruction,*args = line.split(" ")

			# leave instructions untouched, but return gamefolder consistently
			if instruction in ['GAME','GAMEFOLDER']:
				assert gamefolder is None
				if instruction == 'GAME':
					gamefolder = config.GAMES[args[0]]
				else:
					gamefolder = args[0]

			instructions.append({'instruction':instruction,'args':args})

	assert gamefolder is not None

	return {
		'gamefolder':gamefolder,
		'instructions':instructions
	}
