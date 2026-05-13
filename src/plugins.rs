use std::error::Error;
use std::path::PathBuf;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::fs;
use crate::structs::{SkyrimInstall, StagedMod};

pub fn write_plugins_file(skyrim_install: &SkyrimInstall, mods: &Vec<StagedMod>) -> Result<Vec<String>, Box<dyn Error>> {
    let mut ordered_plugins: Vec<String> = vec![];

    for stg_mod in mods {
        let plugins = stg_mod.get_plugins()?;
        for plugin in plugins {
            ordered_plugins.push(plugin);
        }
    }

    let file = File::create(&skyrim_install.plugins_file)?;
    let mut writer = BufWriter::new(file);

    writeln!(writer, "# This file was written my Numidium")?;
    writeln!(writer, "# It only makes sense for the last selected modlist.")?;
    for plugin in &ordered_plugins {
        writeln!(writer, "*{}", plugin)?;
    }

    Ok(ordered_plugins)

}