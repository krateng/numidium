import os
import yaml

CONFIG_FILE = "./numidium.yml"

configfile = os.path.abspath(CONFIG_FILE)
configfile_context = os.path.dirname(configfile)

GAMES = {
	'skyrim64':"Skyrim Special Edition",
	'skyrim32':"Skyrim",
	'oblivion':"Oblivion"
}

PATHS = {
	'configfile':configfile,
	'configfile_context':configfile_context,
	'games_folder': os.path.expanduser("~/.steam/steam/SteamApps/common")
}

with open(configfile) as configfiled:
	for k,v in yaml.safe_load(configfiled).items():
		# replace relative paths
		PATHS[k] = os.path.normpath(os.path.join(configfile_context,v))

PATHS['workdir'] = os.path.join(PATHS['system_folder'],'workdir')
PATHS['layers'] = os.path.join(PATHS['system_folder'],'layers')

os.makedirs(PATHS['workdir'],exist_ok=True)
os.makedirs(PATHS['dynamic_folder'],exist_ok=True)
os.makedirs(PATHS['layers'],exist_ok=True)
