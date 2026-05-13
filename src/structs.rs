use std::error::Error;
use std::fs;
use walkdir::WalkDir;
use std::path::PathBuf;
use std::sync::Arc;

pub struct SkyrimInstall {
    pub skyrim_folder: PathBuf,
    pub plugins_file: PathBuf,
}

pub struct StagedMod {
    pub install: Arc<SkyrimInstall>,
    pub identifier: String,
}


impl SkyrimInstall {
    pub fn data_folder(&self) -> PathBuf {
        self.skyrim_folder.join("Data")
    }

    pub fn numidium_folder(&self) -> PathBuf {
        self.skyrim_folder.join("Numidium")
    }

    pub fn modlist_folder(&self) -> PathBuf {
        self.numidium_folder().join("lists")
    }

    pub fn staging_folder(&self) -> PathBuf {
        self.numidium_folder().join("staging")
    }

    pub fn working_folder(&self) -> PathBuf {
        self.numidium_folder().join(".working")
    }

    // TODO make this modlist specific
    pub fn tmp_folder(&self) -> PathBuf {
        self.numidium_folder().join(".tmp")
    }
}

static PLUGIN_EXTENSIONS: [&str; 3] = ["esp", "esm", "esl"];
impl StagedMod {
    pub fn mod_folder(&self) -> PathBuf {
        self.install.staging_folder().join(&self.identifier)
    }

    pub fn verify_exist(&self) -> Result<(), std::io::Error> {
        if !self.mod_folder().exists() {
            Err(std::io::Error::new(std::io::ErrorKind::NotFound, format!("Mod {} not found in staging", self.identifier)))?
        }
        Ok(())
    }

    pub fn get_plugins(&self) -> Result<Vec<String>, Box<dyn Error>> {

        let names: Vec<String> = fs::read_dir(&self.mod_folder())?
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.extension()
                .map_or(false, |ext| PLUGIN_EXTENSIONS.contains(&ext.to_str().unwrap_or(""))))
            .filter_map(|p| p.file_name()?.to_str().map(String::from))
            .collect();
        Ok(names)
    }

    pub fn fix_case(&self) -> Result<(), Box<dyn Error>> {
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