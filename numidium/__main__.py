import sys
import os

from . import brass
from . import config
from . import filesystem
from . import build

from doreah.io import col



if __name__ == '__main__':

	action, *args = sys.argv[1:]
	if action == 'deploy':

		brassfile = args[0]

		info = brass.load_brassfile(brassfile)

		gamefolder = os.path.join(config.PATHS['games_folder'],info['gamefolder'])
		filesystem.umount(gamefolder)

		layers = list(build.build_layers(info['instructions']))

		filesystem.mount(gamefolder,layers,config.PATHS['dynamic_folder'])

	if action == 'disband':
		filesystem.umount()
