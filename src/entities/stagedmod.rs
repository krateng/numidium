use std::error::Error;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use walkdir::WalkDir;
use crate::entities::Install;

static PLUGIN_EXTENSIONS: [&str; 3] = ["esp", "esm", "esl"];


pub struct StagedMod {
    pub install: Arc<Install>,
    pub identifier: String,
}

impl StagedMod {
    pub fn mod_folder(&self) -> PathBuf {
        let fol = self.install.staging_folder().join(&self.identifier);
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn verify_exist(&self) -> anyhow::Result<()> {
        if !self.mod_folder().exists() {
            Err(std::io::Error::new(std::io::ErrorKind::NotFound, format!("Mod {} not found in staging", self.identifier)))?
        }
        Ok(())
    }

    pub fn get_plugins(&self) -> anyhow::Result<Vec<String>> {

        let names: Vec<String> = fs::read_dir(&self.mod_folder())?
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.extension()
                .map_or(false, |ext| PLUGIN_EXTENSIONS.contains(&ext.to_str().unwrap_or(""))))
            .filter_map(|p| p.file_name()?.to_str().map(String::from))
            .collect();
        Ok(names)
    }

    pub fn fix_case(&self) -> anyhow::Result<()> {
        let mut entries: Vec<_> = WalkDir::new(self.mod_folder())
            .min_depth(1)
            .into_iter()
            .filter_map(|e| e.ok())
            .collect();

        entries.sort_by_key(|e| std::cmp::Reverse(e.depth()));

        for entry in entries {
            let path = entry.path();
            let name = path.file_name().unwrap().to_str().unwrap();
            let lower = name.to_lowercase();

            if name != lower {
                let new_path = path.parent().unwrap().join(&lower);
                println!("Had to fix filename: {:?}", path);
                fs::rename(path, &new_path)?;
            }
        }

        Ok(())
    }
}