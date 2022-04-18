from os import path as pth
import os
import yaml

CONFIG_FILE = "./numidium.yml"

configfile = pth.abspath(CONFIG_FILE)
configfile_context = pth.dirname(configfile)

GAMES = {
	'skyrim64':"Skyrim Special Edition",
	'oblivion':"Oblivion"
}

PATHS = {
	'configfile':configfile
}

with open(configfile) as configfiled:
	for k,v in yaml.safe_load(configfiled).items():
		# replace relative paths
		PATHS[k] = pth.normpath(pth.join(configfile_context,v))

PATHS['workdir'] = pth.join(PATHS['system_folder'],'workdir')

os.makedirs(PATHS['workdir'],exist_ok=True)
os.makedirs(PATHS['dynamic_folder'],exist_ok=True)
