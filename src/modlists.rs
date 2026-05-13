use std::path::PathBuf;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::sync::Arc;
use crate::structs::{SkyrimInstall, StagedMod};

/// Returns the staged mods demanded by the list and guarantees their existence
pub fn get_staging_mods_for_list(skyrim_install: &Arc<SkyrimInstall>, modlist_identifier: &str) -> Result<Vec<StagedMod>, std::io::Error> {

    let modlist_folder = skyrim_install.modlist_folder();
    let modlist_file = format!("{}.brass", modlist_identifier);
    let modlist_path = modlist_folder.join(modlist_file);

    println!("Modlist path: {:?}", modlist_path);
    let modlist = read_modlist(&modlist_path)?;
    let mut mod_staged_list: Vec<StagedMod> = vec![];

    for mod_identifier in modlist.clone() {
        let stg_mod = StagedMod {
            install: Arc::clone(skyrim_install),
            identifier: mod_identifier,
        };
        let _ = &stg_mod.verify_exist()?;
        mod_staged_list.push(stg_mod);
    }

    Ok(mod_staged_list)
}

fn read_modlist(listfile: &PathBuf) -> Result<Vec<String>, std::io::Error> {
    let file = File::open(listfile)?;
    let reader = BufReader::new(file);
    let mut identifiers = vec![];
    for line_result in reader.lines() {
        let line = line_result?;
        if !line.starts_with('#') && !line.is_empty() {
            identifiers.push(line);
        }
    }
    Ok(identifiers)
}