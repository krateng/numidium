import os
import yaml
import hashlib
import shutil

from doreah.io import col

from . import config


ALLOW_CACHING = False

def console_output_instruction(i,contextual_identifier=None):
	hash = col['yellow'](contextual_identifier or i.identify())
	desc = col['lightblue'](i)

	print(f"   [{hash}] {desc}")


# for each instruction object, check if we we have a cached layer, otherwise build new
# yield paths to folders
def build_layers(instructions):
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
		if (contextual_identifier in existing_layers) and ALLOW_CACHING:
			print(col['lawngreen'](f"   ☑Reusing from cache"))
			layer = existing_layers[contextual_identifier]
		else:
			layer = i.get_layer()
			with open(os.path.join(layerdir,contextual_identifier + '.layer'),'w') as fd:
				yaml.dump(layer,fd)


		if layer['type'] == 'skip':
			print(col['orange'](f"   ☒No layer returned, skipping"))
		elif layer['type'] == 'existing_path':
			print(col['lawngreen']("   ☑ Returned existing static layer"))
			yield layer['path']
		elif layer['type'] == 'file_map':
			l = create_staging_layer(layer['files'],layer['srcfolder'],contextual_identifier)
			print(col['lawngreen']("   ☑ Built layer"))
			yield l





def create_staging_layer(filesdict,srcfolder,identifier):
	newdir = os.path.join(config.PATHS['staging'],str(identifier))
	os.makedirs(newdir,exist_ok=True)

	for f in filesdict:
		srcfile = os.path.join(srcfolder,f)
		targetfile = os.path.join(newdir,filesdict[f])
		print("     Copying",col['orange'](f),"to",col['magenta'](filesdict[f]))
		os.makedirs(os.path.dirname(targetfile),exist_ok=True)
		shutil.copyfile(srcfile,targetfile)

	return newdir
