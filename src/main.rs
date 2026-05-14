use clap::{Parser, Subcommand};
use colored::Colorize;
use common::ConsoleDisplay;
use entities::{Modlist, Install};
use std::io::{stdout, Write};
use std::path::PathBuf;
use std::sync::mpsc::channel;
use std::sync::Arc;
use crate::entities::Game;

mod filesystem;
mod plugins;
mod entities;
mod common;


static GAMES: [Game; 2] = [
    Game { name: "Skyrim SE", executable: "SkyrimSE.exe", steam_id: 489830, plugin_file_path: "pfx/drive_c/users/steamuser/AppData/Local/Skyrim Special Edition/Plugins.txt" },
    Game { name: "Skyrim VR", executable: "SkyrimVR.exe", steam_id: 611670, plugin_file_path: "tbd" },
];

#[derive(Parser)]
struct Args {
    /// Path to the Game installation (parent of the Data folder). Put the Numidium executable in the folder to avoid having to specify this.
    #[arg(short, long, global = true)]
    gamefolder: Option<PathBuf>,

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
    let game_install = determine_install()?;
    let arc_game_install = Arc::new(game_install);

    let op = Args::parse().operation;

    match op {
        Operation::Mount { modlist } => {
            let modlist_obj = Modlist {
                install: Arc::clone(&arc_game_install),
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

            let _plugins = plugins::write_plugins_file(&arc_game_install, &mods)?;
            //println!("The following plugins will be loaded:");
            //for p in &plugins {
            //    println!("\t{}", p.yellow());
            //}
            //println!();

            filesystem::build_skyrim_folder(&arc_game_install, &mods, &modlist_obj.mutable_folder())?;
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
            filesystem::unmount(&arc_game_install);
            Ok(())
        }
        Operation::Install { archive } => {
            anyhow::bail!("Not yet implemented.");
        }
    }


}

/// find out what install we're working with, which game and what the actual folder is
fn determine_install() -> anyhow::Result<Install> {
    let args = Args::parse();
    let game_folder = args.gamefolder.unwrap_or_else(|| {
        // numidium binary should always be located in the root folder, same as the game .exe itself
        let binary_location = std::env::current_exe().unwrap();
        binary_location.parent().unwrap().to_path_buf()
    });

    if !game_folder.exists() {
        anyhow::bail!(
            "Folder {} does not exist. Put the Numidium executable in your Game folder, or use {} to provide a custom install location.",
            game_folder.colorized(),
            "--install".dimmed().italic()
        );
    }
    if !game_folder.join("Data").exists() {
        anyhow::bail!(
            "No valid game installation could be found at {}. Put the Numidium executable in your game folder, or use {} to provide a custom install location.",
            game_folder.colorized(),
            "--install".dimmed().italic()
        )
    }

    let Some(detected_game) = GAMES.iter().find(|game| game_folder.join(game.executable).exists()) else {
        anyhow::bail!(
            "No valid game installation could be found at {}. Put the Numidium executable in your game folder, or use {} to provide a custom install location.",
            game_folder.colorized(),
            "--install".dimmed().italic()
        )
    };

    println!("Using {} install at {}", &detected_game.name.bold().underline(), game_folder.colorized());

    let plugins_file = args.pluginsfile.unwrap_or_else(|| {
        let steam_folder = game_folder.parent().unwrap().parent().unwrap();
        steam_folder
            .join("compatdata")
            .join(detected_game.steam_id.to_string())
            .join(detected_game.plugin_file_path)
    });

    if !plugins_file.exists() {
        anyhow::bail!(
            "No plugins file found at {}. Use {} to provide a custom location.",
            plugins_file.colorized(),
            "--pluginsfile".dimmed().italic()
        )
    }
    println!("Using Plugins file at {}", plugins_file.colorized());

    let install: Install = Install {
        game: detected_game.clone(),
        install_folder: game_folder,
        plugins_file,
    };

    Ok(install)
}
