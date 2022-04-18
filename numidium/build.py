import os
import yaml
import hashlib

from doreah.io import col

from . import config


def console_output_instruction(i):
	hash = col['yellow'](i.identify())
	desc = col['lightblue'](i)

	print(f"\t[{hash}] {desc}")

def build_layers(instructions,brassfilecontext=os.getcwd()):
	print("Building layers")
	existing_layers = {}
	layerdir = config.PATHS['layers']
	for f in os.listdir(layerdir):
		if not f.endswith('.layer'): continue

		with open(os.path.join(layerdir,f),'r') as fd:
			existing_layers.append(yaml.safe_load(fd))

	contextual_identifier = ''
	for i in instructions:
		identifier = i.identify()
		if i.stack_dependent:
			contextual_identifier = contextual_identifier + str(identifier)
		else:
			contextual_identifier = str(identifier)
		console_output_instruction(i)
		if contextual_identifier in existing_layers:
			print(f"\t\tCached, reusing...")
		else:
			print(f"\t\tBuilding...")
			layer = create_layer(i,brassfilecontext=brassfilecontext)
			yield layer




# takes an instruction object, returns a ready folder to use
def create_layer(i,brassfilecontext=os.getcwd()):
	return i.get_folder()


	return os.path.join(brassfilecontext,args[0])
