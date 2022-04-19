import os
import toml

CONFIG_FILE = "./numidium.yml"

config_file_options = [
	"./numidium.toml",
	os.path.expanduser("~/.local/share/numidium/numidium.toml"),
	os.path.expanduser("~/.config/numidium.toml"),
	os.path.expanduser("~/.config/numidium/numidium.toml")
]

configfile = os.path.abspath(CONFIG_FILE)
configfile_context = os.path.dirname(configfile)


# game settings
GAMES = {
	'skyrim64':{
		'path':"Skyrim Special Edition"
	},
	'skyrim32':{
		'path':"Skyrim"
	},
	'oblivion':{
		'path':"Oblivion"
	}
}

PATHS = {
	'configfile':configfile,
	'configfile_context':configfile_context,
	# set defaults, to be overwritten by user config
	'games': os.path.expanduser("~/.steam/steam/SteamApps/common"),
	'application_data': os.path.expanduser("~/.local/share/numidium"),
	'mods': os.path.expanduser("~/.local/share/numidium/mods"),
	'modlists': os.path.expanduser("~/.local/share/numidium/modlists"),
}

for configfile in config_file_options:
	if os.path.exists(configfile):
		with open(configfile) as fd:
			data = toml.load(fd)

		for k,v in data.get('paths',{}).items():
			# replace relative paths
			PATHS[k] = os.path.normpath(os.path.join(configfile_context,os.path.expanduser(v)))

		for g in GAMES:
			# save as is, the instruction class will automatically resolve relative paths
			GAMES[g].update(data.get('games',{}).get(g,{}))

		break

# dependent paths
PATHS['workdir'] = os.path.join(PATHS['application_data'],'workdir')
PATHS['layers'] = os.path.join(PATHS['application_data'],'layers')
PATHS['runtime_changes'] = os.path.join(PATHS['application_data'],'runtime_layers')

os.makedirs(PATHS['workdir'],exist_ok=True)
os.makedirs(PATHS['layers'],exist_ok=True)
os.makedirs(PATHS['runtime_changes'],exist_ok=True)
