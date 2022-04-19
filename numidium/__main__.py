import sys
import os

from . import brass
from . import config
from . import filesystem
from . import build
from . import stage_mod
from . import instructionclasses

from doreah.io import col



if __name__ == '__main__':

	action, *args = sys.argv[1:]

	# print information about used paths
	if action == 'folders':
		for k in config.PATHS:
			print(col['magenta'](k) + " " + config.PATHS[k])

	# 'install' a mod to a modlist
	if action == 'install':

		mod,modlist = args

		modfolder = os.path.join(config.PATHS['mods'],mod)

		brassfile = brass.BrassModlist(modlist)

		options,files = stage_mod.create_config(modfolder)
		print(options)
		brassfile.add_instruction(instructionclasses.FOMOD(mod,options=options))

		brassfile.save()

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
