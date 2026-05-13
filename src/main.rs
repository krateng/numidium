use std::path::{Path, PathBuf};
use std::str::FromStr;
use std::{thread, time};
use std::error::Error;
use std::io::{stdout, Write};
use std::sync::Arc;
use std::sync::mpsc::channel;
use colored::Colorize;
use crate::structs::SkyrimInstall;

mod filesystem;
mod modlists;
mod plugins;
mod structs;



static MODLIST: &str = "immersive";

fn main() -> Result<(), Box<dyn Error>> {

    let skyrim_install: SkyrimInstall = SkyrimInstall {
        skyrim_folder: PathBuf::from("/mnt/Games/SteamLibrary/steamapps/common/Skyrim Special Edition"),
        plugins_file: PathBuf::from("/mnt/Games/SteamLibrary/steamapps/compatdata/489830/pfx/drive_c/users/steamuser/AppData/Local/Skyrim Special Edition/Plugins.txt"),
    };
    let arc_skyrim_install = Arc::new(skyrim_install);

    let mods = modlists::get_staging_mods_for_list(&arc_skyrim_install, MODLIST)?;
    println!("The following mods are active:");
    for m in &mods {
        println!("\t{}", m.identifier.blue());
        for p in m.get_plugins()? {
            println!("\t * {}", p.yellow())
        }
    }
    println!();

    let plugins = plugins::write_plugins_file(&arc_skyrim_install, &mods)?;
    //println!("The following plugins will be loaded:");
    //for p in &plugins {
    //    println!("\t{}", p.yellow());
    //}
    //println!();

    filesystem::build_skyrim_folder(&arc_skyrim_install, &mods)?;
    println!("Modlist mounted! You can now start the game.");
    println!("After quitting, press CTRL+C to unmount.");
    stdout().flush()?;


    let (tx, rx) = channel();
    ctrlc::set_handler(move || tx.send(()).unwrap())?;
    rx.recv()?; // blocks here until Ctrl+C

    println!("Modlist unmounted. Goodbye, traveller!");
    filesystem::unmount(&arc_skyrim_install);
    Ok(())
}
