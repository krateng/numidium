from os import path as pth
import subprocess

from . import config


# creates the mount on the game directory with specified layers
def mount(targetdir,readlayers,writelayer,dry_run=False):

	dirs = []
	dirs.append(f"lowerdir={':'.join(reversed(readlayers))}")
	# read only system needs neither of these two
	if writelayer is not None:
		dirs.append(f"upperdir={writelayer}")
		dirs.append(f"workdir={config.PATHS['workdir']}")

	cmd = [
		"mount","-t","overlay","overlay",
		"-o",','.join(dirs),
		# gamefolder will be overloaded
		targetdir
	]

	if dry_run:
		print(cmd)
	else:
		subprocess.run(cmd)

# unmounts game directory if it is a mount point
def umount(targetdir):
	if pth.ismount(targetdir):
		print(targetdir,"is currently managed by Numidium, unmounting...")
		cmd = ["umount",targetdir]
		subprocess.run(cmd)
