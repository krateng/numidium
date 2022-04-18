from os import path as pth
import subprocess

from . import config


# creates the mount on the game directory with specified layers
def mount(gamedir,readlayers,writelayer):

	cmd = [
		"mount","-t","overlay","overlay",
		"-o",f"lowerdir={':'.join(reversed(readlayers))},upperdir={writelayer},workdir={config.PATHS['workdir']}",
		# gamefolder will be overloaded
		gamedir
	]

	print(cmd)
	return cmd

# unmounts game directory if it is a mount point
def umount(gamedir):
	if pth.ismount(gamedir):
		print(gamedir,"is currently managed by Numidium, unmounting...")
		cmd = ["umount",gamedir]
		subprocess.run(cmd)
