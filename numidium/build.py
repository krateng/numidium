import os
import yaml
import hashlib

from doreah.io import col

from . import config


def console_output_instruction(i,contextual_identifier=None):
	hash = col['yellow'](contextual_identifier or i.identify())
	desc = col['lightblue'](i)

	print(f"\t[{hash}] {desc}")


# for each instruction object, check if we we have a cached layer, otherwise build new
# yield paths to folders
def build_layers(instructions):
	print("Building layers")
	existing_layers = {}
	layerdir = config.PATHS['layers']
	for f in os.listdir(layerdir):
		if not f.endswith('.layer'): continue

		with open(os.path.join(layerdir,f),'r') as fd:
			existing_layers[f.split('.')[0]] = yaml.safe_load(fd)

	contextual_identifier = 0
	for i in instructions:
		identifier = i.identify()
		contextual_identifier = i.identify_with_context(contextual_identifier)
		console_output_instruction(i,contextual_identifier)
		if contextual_identifier in existing_layers:
			print(f"\t\tCached, reusing...")
			yield existing_layers[contextual_identifier]['path']
		else:
			print(f"\t\tBuilding...")
			path = i.get_folder()
			with open(os.path.join(layerdir,contextual_identifier + '.layer'),'w') as fd:
				yaml.dump({'path':path},fd)
			yield path
