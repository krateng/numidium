#[derive(Clone)]
pub struct Game {
    pub name: &'static str,
    pub executable: &'static str,
    pub steam_id: u32,
    pub plugin_file_path: &'static str, //relative to compatdata game root
    pub datafolder: &'static str,
}