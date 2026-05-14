use std::error::Error;
use std::fs;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::sync::Arc;
use colored::Colorize;
use crate::common::ConsoleDisplay;
use crate::entities::{SkyrimInstall, StagedMod};

pub struct Modlist {
    pub install: Arc<SkyrimInstall>,
    pub identifier: String,
    //pub name: String,
}


impl Modlist {

    pub fn name(&self) -> String {
        let file = fs::File::open(self.get_modlist_file()).expect(
            format!("Modlist {} could not be found. It should be the file {}.", self.identifier.red(), self.get_modlist_file().colorized()).as_str()
        );
        let reader = BufReader::new(file);
        for line_result in reader.lines() {
            let line = line_result.unwrap();
            if line.starts_with("### name = ") {
                return line.split_at(11).1.parse().unwrap();
            }
        }
        self.identifier.clone()
    }

    pub fn mutable_folder(&self) -> PathBuf {
        let fol = self.install.mutable_folder().join(&self.identifier);
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn get_modlist_file(&self) -> PathBuf {
        let brassfile = format!("{}.brass", self.identifier);
        self.install.modlist_folder().join(brassfile)
    }

    pub fn read_mods(&self) -> anyhow::Result<Vec<StagedMod>> {
        let file = fs::File::open(self.get_modlist_file())?;
        let reader = BufReader::new(file);
        let mut mods = vec![];
        for line_result in reader.lines() {
            let line = line_result?;
            if !line.starts_with('#') && !line.is_empty() {
                let stg_mod = StagedMod {
                    install: Arc::clone(&self.install),
                    identifier: line,
                };
                mods.push(stg_mod);
            }
        }
        Ok(mods)
    }
}