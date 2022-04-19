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

GAMES = {
	'skyrim64':"Skyrim Special Edition",
	'skyrim32':"Skyrim",
	'oblivion':"Oblivion"
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
		break

# dependent paths
PATHS['workdir'] = os.path.join(PATHS['application_data'],'workdir')
PATHS['layers'] = os.path.join(PATHS['application_data'],'layers')
PATHS['runtime_changes'] = os.path.join(PATHS['application_data'],'runtime_layers')

os.makedirs(PATHS['workdir'],exist_ok=True)
os.makedirs(PATHS['layers'],exist_ok=True)
os.makedirs(PATHS['runtime_changes'],exist_ok=True)
