### File to find out what the user wants installed and give them an according entry
### NOTE: numidium should never actually INSTALL based on user input
## the whole point is that the brassfile is the source of truth and leads to a repeatable end state
## there should be no interactive user choice

import inquirer
from doreah.io import col
import pyfomod


def install(modfolder):

	fomod = pyfomod.parse(modfolder)

	i = pyfomod.Installer(fomod)
	selections = []
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
				answers = inquirer.prompt(questions)

			elif group.type is pyfomod.GroupType.EXACTLYONE:
				questions = [
					inquirer.List(group.name,
						message=group.name,
						choices=[option.name for option in group],
					),
				]
				answers = inquirer.prompt(questions)

			elif group.type is pyfomod.GroupType.ALL:
				print(group.name)
				print()
				for o in group:
					print(o.description.replace('\r\n\n','\n'))
				print()
				input("Enter to Proceed")
				answers = {option.name:option.name for option in group}

			else:
				print(col['red'](f"Installer does not yet know how to handle {group.type}!"))
				continue

			for opt in group:
				if opt.name in answers.values():
					selections.append(opt)

	files = i.files()
	print("The following files will be installed:")
	for k in files:
		print("\t\t" + files[k])
	return files
