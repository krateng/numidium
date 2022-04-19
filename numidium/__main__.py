import sys
import os

from . import brass
from . import config
from . import filesystem
from . import build
from . import install

from doreah.io import col



if __name__ == '__main__':

	action, *args = sys.argv[1:]
	if action == 'folders':
		for k in config.PATHS:
			print(col['magenta'](k) + " " + config.PATHS[k])
	if action == 'configure':

		mod = args[0]
		modfolder = os.path.join(config.PATHS['mods'],mod)
		install.install(modfolder)


	if action == 'deploy':

		brassfile = args[0]

		info = brass.load_brassfile(brassfile)

		gamefolder = os.path.join(config.PATHS['games'],info['gamefolder'])

		# unmount if already mounted
		filesystem.umount(gamefolder)
		# build layers, return folders
		layers = list(build.build_layers(info['instructions']))
		# create layered fs
		filesystem.mount(gamefolder,layers,config.PATHS['runtime_changes'])

	if action == 'disband':
		filesystem.umount()
