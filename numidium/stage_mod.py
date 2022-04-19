### File to find out what the user wants installed and give them an according entry
### NOTE: numidium should never actually INSTALL based on user input
## the whole point is that the brassfile is the source of truth and leads to a repeatable end state
## there should be no interactive user choice

import inquirer
from doreah.io import col
import pyfomod


def create_config(modfolder):

	fomod = pyfomod.parse(modfolder)

	i = pyfomod.Installer(fomod)
	selections = []
	allanswers = []
	while True:
		page = i.next(selections)
		if page is None: break

		print()
		print(col['yellow'](page.name))
		print()

		selections = []
		for group in page:

			if group.type is pyfomod.GroupType.ANY:
				questions = [
					inquirer.Checkbox(group.name,
						message=group.name,
						choices=[option.name for option in group],
					),
				]
				answers = inquirer.prompt(questions)[group.name]

			elif group.type is pyfomod.GroupType.EXACTLYONE:
				questions = [
					inquirer.List(group.name,
						message=group.name,
						choices=[option.name for option in group],
					),
				]
				answers = [inquirer.prompt(questions)[group.name]]

			elif group.type is pyfomod.GroupType.ALL:
				print(group.name)
				print()
				for o in group:
					print(o.description.replace('\r\n\n','\n'))
				print()
				input("Enter to Proceed")
				answers = [option.name for option in group]

			else:
				print(col['red'](f"Installer does not yet know how to handle {group.type}!"))
				continue

			for opt in group:
				if opt.name in answers:
					selections.append(opt)

			allanswers += answers


	files = i.files()
	print("The following files will be installed:")
	for k in files:
		print("\t\t" + files[k])

	return allanswers,files
