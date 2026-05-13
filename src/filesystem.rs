use std::error::Error;
use vfs::{OverlayFS, PhysicalFS, VfsPath};
use libmount::Overlay;
use std::path::{Path, PathBuf};
use crate::structs::{SkyrimInstall, StagedMod};


pub fn build_skyrim_folder(
    skyrim_install: &SkyrimInstall,
    mods: &Vec<StagedMod>,
) -> Result<(), Box<dyn Error>> {

    let mut mod_folders_to_stage: Vec<PathBuf> = vec![];
    for stg_mod in mods {
        stg_mod.fix_case()?;
        let mod_folder = stg_mod.mod_folder();
        mod_folders_to_stage.push(mod_folder);
    }

    build_folder(
        skyrim_install.data_folder(),
        mod_folders_to_stage,
        skyrim_install.tmp_folder(),
        skyrim_install.working_folder()
    );
    Ok(())
}

pub fn unmount(skyrim_install: &SkyrimInstall) {
    let data_folder: PathBuf = skyrim_install.data_folder();
    std::process::Command::new("umount")
        .arg(&data_folder)
        .status()
        .unwrap();
}

fn build_folder(
    base_folder: PathBuf,
    mod_folders: Vec<PathBuf>,
    write_folder: PathBuf,
    working_folder: PathBuf
) {
    let mut layers_sorted: Vec<PathBuf> = vec![];

    for folder in mod_folders.into_iter().rev() {
        layers_sorted.push(folder);
    }
    layers_sorted.push(base_folder.clone());

    let layers_sorted_paths = layers_sorted.iter().map(|p| p.as_path()).collect::<Vec<&Path>>();


    let overlayfs = Overlay::writable(
        // lowerdirs: mods + base game in reverse order
        layers_sorted_paths.into_iter(),
        // upperdir: where game can write stuff (racemenu presets maybe?)
        write_folder,
        // workdir: for the fs admin
        working_folder,
        // target: skyrim directory again to shadow
        base_folder
    );
    overlayfs.mount().expect("Filesystem could not be mounted");


}
