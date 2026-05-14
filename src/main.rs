use clap::{Parser, Subcommand};
use colored::Colorize;
use common::ConsoleDisplay;
use entities::{Modlist, SkyrimInstall};
use std::io::{stdout, Write};
use std::path::PathBuf;
use std::sync::mpsc::channel;
use std::sync::Arc;

mod filesystem;
mod plugins;
mod entities;
mod common;

static SKYRIM_STEAM_ID: u32 = 489830;

#[derive(Parser)]
struct Args {
    /// Path to the Skyrim installation. Put the Numidium executable in your Skyrim folder to avoid having to specify this.
    #[arg(short, long, global = true)]
    skyrimfolder: Option<PathBuf>,

    /// Path to the Plugins.txt file. Should only be needed for a non-standard location.
    #[arg(short, long, global = true)]
    pluginsfile: Option<PathBuf>,

    #[command(subcommand)]
    operation: Operation,
}

#[derive(Subcommand)]
enum Operation {
    /// Activate the specified modlist
    Mount {
        /// Identifier of the modlist to be activated. Name of the .brass-File without extension.
        #[arg()]
        modlist: String,
    },
    /// Install a mod to your staging area. Will be interactive if a fomod-enabled archive is provided.
    Install {
        /// Path to the archive to be installed
        #[arg()]
        archive: PathBuf,
    }
}


fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {e}");
        std::process::exit(1);
    }
}

fn run() -> anyhow::Result<()> {
    let skyrim_install = find_skyrim_install()?;
    let arc_skyrim_install = Arc::new(skyrim_install);

    let op = Args::parse().operation;

    match op {
        Operation::Mount { modlist } => {
            let modlist_obj = Modlist {
                install: Arc::clone(&arc_skyrim_install),
                identifier: modlist,
            };

            println!("Mounting modlist {}...", &modlist_obj.colorized().bold().underline());

            let mods = modlist_obj.read_mods()?;
            for m in &mods {
                m.verify_exist()?;
            }
            println!("The following mods are active:");
            for m in &mods {
                println!("\t{}", m.colorized());
                for p in m.get_plugins()? {
                    println!("\t * {}", p.yellow().italic());
                }
            }
            println!();

            let _plugins = plugins::write_plugins_file(&arc_skyrim_install, &mods)?;
            //println!("The following plugins will be loaded:");
            //for p in &plugins {
            //    println!("\t{}", p.yellow());
            //}
            //println!();

            filesystem::build_skyrim_folder(&arc_skyrim_install, &mods, &modlist_obj.mutable_folder())?;
            println!("Modlist mounted! You can now start the game or tools.");
            println!("After you're done, press CTRL+C to unmount.");
            stdout().flush()?;


            let (tx, rx) = channel();
            ctrlc::set_handler(move || tx.send(()).unwrap())?;
            rx.recv()?; // blocks here until Ctrl+C
            println!();
            println!("Modlist unmounted.");
            println!("Runtime changes are saved in {}.", &modlist_obj.mutable_folder().colorized());
            println!("If you want to make them permanent, copy them over to the staged mod folder they should belong to.");
            println!("{}", "Watch the skies, traveller!".magenta().dimmed());
            filesystem::unmount(&arc_skyrim_install);
            Ok(())
        }
        Operation::Install { archive } => {
            anyhow::bail!("Not yet implemented.");
        }
    }


}

fn find_skyrim_install() -> anyhow::Result<SkyrimInstall> {
    let args = Args::parse();
    let skyrim_folder = args.skyrimfolder.unwrap_or_else(|| {
        // get skyrim install. binary should always be located in the skyrim root folder, same as the skyrim.exe itself
        let binary_location = std::env::current_exe().unwrap();
        binary_location.parent().unwrap().to_path_buf()
    });

    if !skyrim_folder.exists() {
        anyhow::bail!(
            "Folder {} does not exist. Put the Numidium executable in your Skyrim folder, or use {} to provide a custom install location.",
            skyrim_folder.to_str().unwrap().green(),
            "--install".dimmed().italic()
        );
    }
    if !skyrim_folder.join("Data").exists() || !skyrim_folder.join("SkyrimSE.exe").exists() {
        anyhow::bail!(
            "No valid Skyrim installation could be found at {}. Put the Numidium executable in your Skyrim folder, or use {} to provide a custom install location.",
            skyrim_folder.to_str().unwrap().green(),
            "--install".dimmed().italic()
        )
    }
    println!("Using Skyrim install at {}", skyrim_folder.to_str().unwrap().green());

    let plugins_file = args.pluginsfile.unwrap_or_else(|| {
        let steam_folder = skyrim_folder.parent().unwrap().parent().unwrap();
        steam_folder
            .join("compatdata")
            .join(SKYRIM_STEAM_ID.to_string())
            .join("pfx/drive_c/users/steamuser/AppData/Local/Skyrim Special Edition/Plugins.txt")
    });

    if !plugins_file.exists() {
        anyhow::bail!(
            "No plugins file found at {}. Use {} to provide a custom location.",
            plugins_file.to_str().unwrap().green(),
            "--pluginsfile".dimmed().italic()
        )
    }
    println!("Using Plugins file at {}", plugins_file.to_str().unwrap().green());

    let skyrim_install: SkyrimInstall = SkyrimInstall {
        skyrim_folder,
        plugins_file,
    };

    Ok(skyrim_install)
}
