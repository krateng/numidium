import os
from . import config


# takes an instruction dict, creates a folder, returns its path
def create_layer(i,brassfilecontext=os.getcwd()):
	inst = i['instruction']
	args = i['args']
	if inst == 'GAME':
		# convert to gamefolder and pass on
		inst = 'GAMEFOLDER'
		args[0] = config.GAMES[args[0]]
	if inst == 'GAMEFOLDER':
		# convert to folder and pass on
		inst = 'FOLDER'
		args[0] = os.path.join(config.PATHS['games_folder'],args[0])
	if inst == 'FOLDER':
		# maybe relative
		return os.path.join(brassfilecontext,args[0])
