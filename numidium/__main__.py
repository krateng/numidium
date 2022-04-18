import sys
import os

from . import brass
from . import config
from . import filesystem
from . import build



if __name__ == '__main__':

	action, *args = sys.argv[1:]
	if action == 'deploy':
		#filesystem.umount()
		brassfile = os.path.abspath(args[0])
		brassfile_context = os.path.dirname(brassfile)
		info = brass.load_brassfile(brassfile)

		gamefolder = os.path.join(config.PATHS['games_folder'],info['gamefolder'])

		layers = []
		for i in info['instructions']:
			layers.append(build.create_layer(i,brassfilecontext=brassfile_context))

		filesystem.mount(gamefolder,layers,config.PATHS['dynamic_folder'])

	if action == 'disband':
		filesystem.umount()
