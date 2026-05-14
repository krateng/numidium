use std::fs;
use std::path::PathBuf;
use crate::entities::Game;

pub struct Install {
    pub game: Game,
    pub install_folder: PathBuf,
    pub plugins_file: PathBuf,
}


impl Install {
    pub fn data_folder(&self) -> PathBuf {
        let fol = self.install_folder.join("Data");
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn numidium_folder(&self) -> PathBuf {
        let fol = self.install_folder.join("Numidium");
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn modlist_folder(&self) -> PathBuf {
        let fol = self.numidium_folder().join("lists");
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn staging_folder(&self) -> PathBuf {
        let fol = self.numidium_folder().join("staging");
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn working_folder(&self) -> PathBuf {
        let fol = self.numidium_folder().join(".working");
        fs::create_dir_all(&fol).unwrap();
        fol
    }

    pub fn mutable_folder(&self) -> PathBuf {
        let fol = self.numidium_folder().join(".mutable");
        fs::create_dir_all(&fol).unwrap();
        fol
    }
}