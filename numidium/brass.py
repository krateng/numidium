import yaml
import os

from . import config
from . import instructionclasses



# loads instruction dicts from brassfile, also specifically extracts game (which remains also an instruction)
def load_brassfile(inputf):
	gamefolder = None
	instructionlist = []
	brassfile_context = os.path.dirname(os.path.abspath(inputf))
	with open(inputf) as inputfd:

		for line in inputfd:
			line = line[:-1] # remove newline
			if not line: continue # empty lines
			if line.startswith('#'): continue # comments

			instruction,argsstring = line.split(" ",1)

			# leave instructions untouched, but return gamefolder consistently
			if instruction in ['GAME','GAMEFOLDER']:
				assert gamefolder is None
				if instruction == 'GAME':
					gamefolder = config.GAMES[argsstring]
				else:
					gamefolder = argsstring

			instructionlist.append(instructionclasses.instruction_types[instruction](argsstring,brassfile_context=brassfile_context))

	assert gamefolder is not None

	return {
		'gamefolder':gamefolder,
		'instructions':instructionlist
	}
