use std::path::PathBuf;
use colored::Colorize;
use crate::entities::{Modlist, StagedMod};

pub(crate) trait ConsoleDisplay {
    fn colorized(&self) -> colored::ColoredString;
}

impl ConsoleDisplay for Modlist {
    fn colorized(&self) -> colored::ColoredString {
        self.name().red()
    }
}

impl ConsoleDisplay for StagedMod {
    fn colorized(&self) -> colored::ColoredString {
        self.identifier.blue()
    }
}

impl ConsoleDisplay for PathBuf {
    fn colorized(&self) -> colored::ColoredString {
        self.to_str().unwrap().green()
    }
}