Numidium is a very simple mod manager for Bethesda games (for now only Skyrim) running with Proton on Linux.

It is not a mod manager in the sense that MO2 or Vortex are - it does not fix your load order, resolve dependencies or integrate with mod hosting platforms.
It's more meant for people who like installing mods manually and have full control over the file structure logic, but don't want to pollute their Data directory.
It allows you to keep your modlists as simple files and then instantly activate them without ever touching the base game directory, by simply mounting the combined virtual directory on top.
The game executable sees a fully modded game, the real folder stays completely clean.

## How to use

1) Put the numidium binary in your base game folder (the same where `Data` and the executable live)
2) Create a `Numidium` folder in the same directory, with a `lists` and a `staged` folder inside
3) Extract the `Data` folder of a mod to a folder inside `staged` that represents this specific configuration of this mod, e.g. `Numidium/staged/SeranaJihyoReplacer`
4) Write a file for your modlist, ending in the extension `.brass`, in your `lists` folder. This file references each installed mod in order by its folder name. Lines that start with `#` are comments. Example:

`epicimmersive.brass`:
```
### name = Epic Immersive Modlist

# base mechanics
NoFastTravel
PaperMap

# npc stuff
SeranaJihyoReplacer
AllNPCsAreNeverland

# pretty nature
VeryCoolWater
AmazingTrees
FantasticPlants
```

5) Execute the binary from console: `./numidium mount epicimmersive`
6) Play the game
7) Press Ctrl+C in the numidium console to unmount again.