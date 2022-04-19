# Numidium

I felt it's somewhat silly to go through the trouble of running Windows Mod Managers via Proton only for them to then go through extra trouble to make things on Windows work that already are much easier on Linux.

Numidium uses OverlayFS, which can simply put any number of layers on top of the base game directory and then mount the result on the very same path, making the process completely invisible to Steam or the game itself. Even something like SKSE can simply be overlaid over the game directory without affecting it in any way.

Numidium is not a mod manager in the same sense that e.g. Vortex is. Instead of an interactive window with the ability to edit your load order, mod configuration etc. on the fly, Numidium is centered around the concept of having your modlist stored as repeatable instructions that can then be deployed at any time. For this, Numidium uses so-called Brassfiles. Their syntax should be familiar to anyone who has used Docker:

```
GAME skyrim64
MODFOLDER unofficial_skyrim_patch
MODFOLDER hd_textures
MODFOLDER immersive_sweetrolls
MODFOLDER blackpink_main_menu_music_replacer
```

Right now, I'm just experimenting a bit, but if you have your properly configured mods already in extracted folders, you can try it out with:

`python -m numidium deploy mymodlist`

where `mymodlist.brass` contains your load order. and all the mods are in your configured mod folder.


## Planned features

* INCLUDE Statement to have sub-modlists
* Proper configuration for fomod-enabled mods
