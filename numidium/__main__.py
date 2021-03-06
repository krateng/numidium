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

		brassfile = brass.BrassModlist(modlist)
		modfolder = os.path.join(config.PATHS['mods'],config.GAMES[brassfile.game]['modpath'],mod)



		options,files = stage_mod.create_config(modfolder)
		print(options)
		brassfile.add_instruction(instructionclasses.FOMOD(mod,options_deserialized=options))

		brassfile.save()

	if action == 'deploy' or action == 'test':

		modlist = args[0]
		brassfile = brass.BrassModlist(modlist)

		game = brassfile.game
		gamefolder = os.path.join(config.PATHS['games'],config.GAMES[game]['gamepath'])

		# unmount if already mounted
		filesystem.umount(gamefolder)
		# build layers, return folders
		layers = list(build.build_layers(brassfile.instructions))
		# create layered fs
		filesystem.mount(gamefolder,layers,config.PATHS['runtime_changes'],dry_run=(action == 'test'))

	if action == 'disband':
		if args:
			games = args
		else:
			games = config.GAMES.keys()

		for game in games:
			gamefolder = os.path.join(config.PATHS['games'],config.GAMES[game]['gamepath'])
			filesystem.umount(gamefolder)
