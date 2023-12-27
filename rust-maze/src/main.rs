extern crate raylib;
use raylib::prelude::*;
use rand::seq::SliceRandom;
use serde::{Serialize, Deserialize};
use serde_json;
use std::collections::BTreeMap;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::time::{Duration, Instant};

const WIDTH: i32 = 200;
const HEIGHT: i32 = 200;
const GRID_SIZE: i32 = 20;
const GRID_WIDTH: i32 = WIDTH / GRID_SIZE;
const GRID_HEIGHT: i32 = HEIGHT / GRID_SIZE;

struct Maze {
    grid: Vec<Vec<i32>>,
    rng: rand::rngs::ThreadRng,
}

impl Maze {
    fn new() -> Self {
        let grid = vec![vec![1; GRID_WIDTH as usize]; GRID_HEIGHT as usize];
        let rng = rand::thread_rng();
        Self { grid, rng }
    }

    fn generate_maze(&mut self, x: usize, y: usize) {
        self.grid[y][x] = 0;
        let mut dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)];

        dirs.shuffle(&mut self.rng);

        for (dx, dy) in dirs {
            let nx = (x as i32 + dx * 2) as usize;
            let ny = (y as i32 + dy * 2) as usize;

            if nx < GRID_WIDTH as usize && ny < GRID_HEIGHT as usize && self.grid[ny][nx] == 1 {
                self.grid[y.wrapping_add(dy as usize)][x.wrapping_add(dx as usize)] = 0;
                self.generate_maze(nx, ny);
            }
        }
    }

    fn draw(&self, d: &mut RaylibDrawHandle) {
        for y in 0..GRID_HEIGHT {
            for x in 0..GRID_WIDTH {
                let color = if self.grid[y as usize][x as usize] == 1 { Color::BLACK } else { Color::WHITE };
                d.draw_rectangle(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE, color);
            }
        }
    }

    fn highlight_moves(&self, d: &mut RaylibDrawHandle, x: i32, y: i32) {
        let highlight_color = Color::new(200, 200, 200, 128);
        if x > 0 && self.grid[y as usize][(x - 1) as usize] == 0 {
            d.draw_rectangle((x - 1) * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE, highlight_color);
        }
        if x < GRID_WIDTH - 1 && self.grid[y as usize][(x + 1) as usize] == 0 {
            d.draw_rectangle((x + 1) * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE, highlight_color);
        }
        if y > 0 && self.grid[(y - 1) as usize][x as usize] == 0 {
            d.draw_rectangle(x * GRID_SIZE, (y - 1) * GRID_SIZE, GRID_SIZE, GRID_SIZE, highlight_color);
        }
        if y < GRID_HEIGHT - 1 && self.grid[(y + 1) as usize][x as usize] == 0 {
            d.draw_rectangle(x * GRID_SIZE, (y + 1) * GRID_SIZE, GRID_SIZE, GRID_SIZE, highlight_color);
        }
    }

    fn get_possible_moves(&self, x: i32, y: i32) -> Vec<String> {
        let mut moves = Vec::new();
        if y > 0 && self.grid[(y - 1) as usize][x as usize] == 0 {
            moves.push("Up".to_string()); // 0
        }
        if x > 0 && self.grid[y as usize][(x - 1) as usize] == 0 {
            moves.push("Left".to_string()); // 1
        }
        if y < GRID_HEIGHT - 1 && self.grid[(y + 1) as usize][x as usize] == 0 {
            moves.push("Down".to_string()); // 2
        }
        if x < GRID_WIDTH - 1 && self.grid[y as usize][(x + 1) as usize] == 0 {
            moves.push("Right".to_string()); // 3
        }
        moves
    }

    fn get_possible_moves_numeric(&self, x: i32, y: i32) -> Vec<i32> {
        let mut moves = Vec::new();
        if y > 0 && self.grid[(y - 1) as usize][x as usize] == 0 {
            moves.push(0); // Up
        }
        if x > 0 && self.grid[y as usize][(x - 1) as usize] == 0 {
            moves.push(1); // Left
        }
        if y < GRID_HEIGHT - 1 && self.grid[(y + 1) as usize][x as usize] == 0 {
            moves.push(2); // Down
        }
        if x < GRID_WIDTH - 1 && self.grid[y as usize][(x + 1) as usize] == 0 {
            moves.push(3); // Right
        }
        moves
    }
}

#[derive(Serialize, Deserialize)]
struct MovesData {
    moves: BTreeMap<String, Vec<String>>,  // Store moves as Vec<String>
    completion_status: i32,  // Store completion status as 0 (not completed) or 1 (completed)
}

fn write_to_csv(moves_data: &MovesData) {
    let file_path = "moves_data.csv";
    let file = match File::create(file_path) {
        Ok(file) => file,
        Err(e) => {
            eprintln!("Failed to create file: {:?}", e);
            return;
        }
    };
    let mut writer = csv::Writer::from_writer(file);

    if writer.write_record(&["move", "possible_moves", "completion_status"]).is_err() {
        eprintln!("Failed to write headers to CSV");
        return;
    }

    for (move_key, possible_moves) in &moves_data.moves {
        let numeric_moves: Vec<String> = possible_moves.iter().map(|move_str| {
            match move_str.as_str() {
                "Up" => "0",
                "Left" => "1",
                "Down" => "2",
                "Right" => "3",
                _ => {
                    eprintln!("Invalid move string: {}", move_str);
                    panic!("Invalid move string")
                },
            }.to_string()
        }).collect();

        let numeric_moves_str = numeric_moves.join(",");

        // Prepare each field of the record separately
        let completion_status = moves_data.completion_status.to_string();
        let fields = vec![move_key, &numeric_moves_str, &completion_status];

        if let Err(e) = writer.write_record(&fields) {
            eprintln!("Failed to write record to CSV: {:?}", e);
            return;
        }
    }

    if let Err(e) = writer.flush() {
        eprintln!("Failed to flush CSV writer: {:?}", e);
        return;
    }
}

fn main() {
    let start_time = Instant::now();
    let mut duration = Duration::new(0, 0);

    let (mut rl, thread) = raylib::init()
        .size(WIDTH, HEIGHT)
        .title("Maze Generator")
        .build();
    rl.set_target_fps(60);

    let path = "assets/ref.png";
    if Path::new(path).exists() {
        match Image::load_image(path) {
            Ok(icon) => rl.set_window_icon(&icon),
            Err(e) => eprintln!("Failed to load icon: {:?}", e),
        }
    } else {
        println!("File does not exist.");
    }

    let mut maze = Maze::new();
    maze.generate_maze(0, 0);

    let (mut player_x, mut player_y) = (0, 0);
    let (finish_x, finish_y) = (GRID_WIDTH - 2, GRID_HEIGHT - 2);
    let mut completed = false;
    let mut has_moved = true;
    let mut completion_message_printed = false;

    // Initialize moves_data and clear the file
    let mut moves_data = MovesData {
        moves: BTreeMap::new(),
        completion_status: 0,  // Initially not completed
    };
    File::create("moves_data.csv").unwrap(); // This clears the CSV file at the start

    let mut move_count = 1;

    while !rl.window_should_close() {
        let mut update_player = |dx: i32, dy: i32| {
            let new_x = player_x + dx;
            let new_y = player_y + dy;
            if new_x >= 0
                && new_x < GRID_WIDTH
                && new_y >= 0
                && new_y < GRID_HEIGHT
                && maze.grid[new_y as usize][new_x as usize] == 0
            {
                player_x = new_x;
                player_y = new_y;
                has_moved = true;
            }
        };

        if rl.is_key_pressed(KeyboardKey::KEY_W) {
            update_player(0, -1);
        }
        if rl.is_key_pressed(KeyboardKey::KEY_S) {
            update_player(0, 1);
        }
        if rl.is_key_pressed(KeyboardKey::KEY_A) {
            update_player(-1, 0);
        }
        if rl.is_key_pressed(KeyboardKey::KEY_D) {
            update_player(1, 0);
        }

        if player_x == finish_x && player_y == finish_y && !completed {
            completed = true;
            completion_message_printed = false;
            duration = start_time.elapsed();
        }

        let mut d = rl.begin_drawing(&thread);
        d.clear_background(Color::WHITE);
        maze.draw(&mut d);

        if !completed {
            maze.highlight_moves(&mut d, player_x, player_y);
            if has_moved {
                let numeric_possible_moves = maze.get_possible_moves_numeric(player_x, player_y);
                let string_possible_moves = maze.get_possible_moves(player_x, player_y);
    
                // Debugging: Print moves to verify consistency
                println!("Numeric Moves: {:?}", numeric_possible_moves);
                println!("String Moves: {:?}", string_possible_moves);
    
                // Assuming you want to keep the String representation in MovesData
                let move_key = format!("{:03}", move_count);
                moves_data.moves.insert(move_key.clone(), string_possible_moves);
                move_count += 1;
                has_moved = false;
    
                // Serialize and write to JSON file
                let json = serde_json::to_string_pretty(&moves_data).unwrap();
                let mut file = File::create("moves_data.json").unwrap();
                file.write_all(json.as_bytes()).unwrap();
    
                // Write to CSV using numeric moves
                write_to_csv(&moves_data);
            }
        }

        if completed && !completion_message_printed {
            let duration_secs = duration.as_secs();
            println!("Congratulations! You've completed the maze in {} seconds", duration_secs);
            moves_data.completion_status = 1;  // Set completion status to 1 when finished
            completion_message_printed = true;
        }

        if completed {
            d.draw_text("Congratulations! You've completed the maze!", WIDTH / 12, HEIGHT / 2, 30, Color::RED);
        }

        d.draw_rectangle(player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::RED);
        d.draw_rectangle(finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::GREEN);
    }
}
