import os
import subprocess
import sys
import yaml
from os import path as pth

WORKDIR = os.path.join(os.getcwd(),".workdir")
CONFIG_FILE = "./numidium.yml"

GAMES = {
	'skyrim64':"Skyrim Special Edition",
	'oblivion':"Oblivion"
}

def load_config(inputf):
	with open(inputf) as inputfd:
		data = yaml.safe_load(inputfd)
	
	return data

def load_loadorder(inputf):
	with open(inputf) as inputfd:
		lines = inputfd.readlines()
		lines = [l[:-1] for l in lines if l]
		instructions = [l.split(" ",1) for l in lines]
		
	return instructions
		
		
	
	
def create_fs(instructions,config):

	layers = []
	have_game = False
	for inst,value in instructions:
		if inst in ['GAME','GAMEFOLDER']:
			if have_game: raise Exception()
			# resolve game instruction or keep raw game folder
			relgamefolder = value if inst == 'GAMEFOLDER' else GAMES[value]
			gamefolder = pth.join(config['games_folder'],relgamefolder)
			layers.append(gamefolder)
			have_game = True
		elif inst == 'MOD':
			modfolder = pth.join(config['mod_folder'],value)
			layers.append(modfolder)
			
	cmd = [
		"mount","-t","overlay","overlay",
		"-o",f"lowerdir={':'.join(reversed(layers))},upperdir={config['dynamic_folder']},workdir={WORKDIR}",
		# gamefolder will be overloaded
		gamefolder
	]
	
	os.makedirs(config['dynamic_folder'],exist_ok=True)
	os.makedirs(WORKDIR,exist_ok=True)
	
	
	print(" ".join(cmd))
	subprocess.run(cmd)
	
	
if __name__ == '__main__':
	_, inputf = sys.argv
	configfile = pth.abspath(CONFIG_FILE)
	configfile_context = pth.dirname(configfile)
	config = load_config(configfile)
	for k in config:
		# replace relative paths
		config[k] = pth.normpath(pth.join(configfile_context,config[k]))
	
	instructions = load_loadorder(inputf)
	create_fs(instructions,config)
