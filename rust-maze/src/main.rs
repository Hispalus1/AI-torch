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
    
        let mut valid_paths = 0;
        for (dx, dy) in dirs {
            let nx = (x as i32 + dx * 2) as usize;
            let ny = (y as i32 + dy * 2) as usize;
    
            if nx < GRID_WIDTH as usize && ny < GRID_HEIGHT as usize && self.grid[ny][nx] == 1 {
                valid_paths += 1;
                self.grid[y.wrapping_add(dy as usize)][x.wrapping_add(dx as usize)] = 0;
                self.generate_maze(nx, ny);
            }
        }
    
        // Pokud neexistují žádné platné cesty, vrátí se z rekurze
        if valid_paths == 0 {
            return;
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
            moves.push("Up".to_string());
        }
        if x > 0 && self.grid[y as usize][(x - 1) as usize] == 0 {
            moves.push("Left".to_string());
        }
        if y < GRID_HEIGHT - 1 && self.grid[(y + 1) as usize][x as usize] == 0 {
            moves.push("Down".to_string());
        }
        if x < GRID_WIDTH - 1 && self.grid[y as usize][(x + 1) as usize] == 0 {
            moves.push("Right".to_string());
        }
        println!("Possible moves from ({}, {}): {:?}", x, y, moves);
        moves
    }
}

#[derive(Serialize, Deserialize)]
struct MovesData {
    moves: BTreeMap<String, Vec<String>>,
    completion_status: i32,
}

fn write_to_csv(moves_data: &MovesData, is_completed: bool) {
    let file_path = "moves_data.csv";
    let mut file = match File::create(file_path) {
        Ok(file) => file,
        Err(e) => {
            eprintln!("Failed to create file: {:?}", e);
            return;
        }
    };

    // Write the header manually with semicolons as delimiters
    if writeln!(file, "move;possible_moves;completion_message").is_err() {
        eprintln!("Failed to write headers to CSV");
        return;
    }

    let last_move_key = moves_data.moves.keys().last().unwrap();
    for (move_key, possible_moves) in &moves_data.moves {
        let numeric_moves_str = if move_key == last_move_key && is_completed {
            "".to_string()
        } else {
            let numeric_moves: Vec<String> = possible_moves.iter().map(|move_str| {
                match move_str.as_str() {
                    "Up" => "0",
                    "Left" => "1",
                    "Down" => "2",
                    "Right" => "3",
                    _ => panic!("Invalid move string: {}", move_str),
                }.to_string()
            }).collect();
            format!("[{}]", numeric_moves.join(","))
        };

        let completion_message = if is_completed && move_key == last_move_key {
            "1"
        } else {
            "0"
        };

        // Write each record manually with semicolons as delimiters
        if writeln!(file, "{};{};{}", move_key, numeric_moves_str, completion_message).is_err() {
            eprintln!("Failed to write record to CSV");
            return;
        }
    }
    println!("Writing to CSV, completion status: {}", is_completed);
}


fn main() {
    let start_time = Instant::now();
    let mut duration = Duration::new(0, 0);
    let mut completion_time: Option<Instant> = None;

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

    let mut moves_data = MovesData {
        moves: BTreeMap::new(),
        completion_status: 0,
    };
    File::create("moves_data.csv").unwrap(); // Clears the CSV file at the start

    let mut move_count = 1;

    while !rl.window_should_close() {
        let mut update_player = |dx: i32, dy: i32| {
            let new_x = player_x + dx;
            let new_y = player_y + dy;
            println!("Player attempting to move to: ({}, {})", new_x, new_y);
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
            println!("Move Up detected");
        }
        if rl.is_key_pressed(KeyboardKey::KEY_S) {
            update_player(0, 1);
            println!("Move down detected");
        }
        if rl.is_key_pressed(KeyboardKey::KEY_A) {
            update_player(-1, 0);
            println!("Move left detected");
        }
        if rl.is_key_pressed(KeyboardKey::KEY_D) {
            update_player(1, 0);
            println!("Move right detected");
        }

        if player_x == finish_x && player_y == finish_y && !completed {
            println!("Maze completed!");
            completed = true;
            completion_message_printed = false;
            duration = start_time.elapsed();
    
            // Update the last move's completion status to 1 (completed)
            let last_move_key = format!("{:03}", move_count);
            moves_data.completion_status = 1; // Set completion status to 1 when finished
            moves_data.moves.entry(last_move_key).or_insert_with(Vec::new);
    
            // Serialize and write to JSON file
            let json = serde_json::to_string_pretty(&moves_data).unwrap();
            let mut file = File::create("moves_data.json").unwrap();
            file.write_all(json.as_bytes()).unwrap();
    
            // Write final data to CSV
            // When calling write_to_csv inside the main loop
            write_to_csv(&moves_data, completed);

        }

        let mut d = rl.begin_drawing(&thread);
        d.clear_background(Color::WHITE);
        maze.draw(&mut d);

        if !completed {
            maze.highlight_moves(&mut d, player_x, player_y);
            if has_moved {
                let string_possible_moves = maze.get_possible_moves(player_x, player_y);
                let move_key = format!("{:03}", move_count);
                moves_data.moves.insert(move_key, string_possible_moves);
                move_count += 1;
                has_moved = false;

                // Serialize and write to JSON file
                let json = serde_json::to_string_pretty(&moves_data).unwrap();
                let mut file = File::create("moves_data.json").unwrap();
                file.write_all(json.as_bytes()).unwrap();

                // Write to CSV using numeric moves
                // When calling write_to_csv inside the main loop
                write_to_csv(&moves_data, completed);

            }
        }

        if completed && !completion_message_printed {
            let duration_secs = duration.as_secs();
            println!("Congratulations! You've completed the maze in {} seconds", duration_secs);
            completion_time = Some(Instant::now());
            completion_message_printed = true;
        }

        if completed {
            d.draw_text("Congratulations! You've completed the maze!", WIDTH / 12, HEIGHT / 2, 30, Color::RED);
        }
        if completed && completion_time.map_or(false, |ct| ct.elapsed() > Duration::new(5, 0)) {
            maze = Maze::new();
            maze.generate_maze(0, 0);
            player_x = 0;
            player_y = 0;
            completed = false;
            completion_message_printed = false;
            moves_data = MovesData {
                moves: BTreeMap::new(),
                completion_status: 0,
            };
            File::create("moves_data.csv").unwrap();
            move_count = 1;
            completion_time = None;
        }


        d.draw_rectangle(player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::RED);
        d.draw_rectangle(finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::GREEN);
    }
}