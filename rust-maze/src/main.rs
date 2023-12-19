extern crate raylib;
use raylib::prelude::*;
use rand::seq::SliceRandom; // Import for SliceRandom


const WIDTH: i32 = 800;
const HEIGHT: i32 = 600;
const GRID_SIZE: i32 = 20;
const GRID_WIDTH: i32 = WIDTH / GRID_SIZE;
const GRID_HEIGHT: i32 = HEIGHT / GRID_SIZE;

struct Maze {
    grid: Vec<Vec<i32>>,
    rng: rand::rngs::ThreadRng, // Add RNG to the Maze struct
}

impl Maze {
    fn new() -> Self {
        let grid = vec![vec![1; GRID_WIDTH as usize]; GRID_HEIGHT as usize];
        let rng = rand::thread_rng(); // Initialize RNG
        Self { grid, rng }
    }

    fn generate_maze(&mut self, x: usize, y: usize) {
        self.grid[y][x] = 0;
        let mut dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)];
        
        dirs.shuffle(&mut self.rng); // Use the RNG in Maze struct

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
        let highlight_color = Color::new(200, 200, 200, 128); // Semi-transparent gray

        // Check each direction and highlight if the cell is open
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

        if x > 0 && self.grid[y as usize][(x - 1) as usize] == 0 {
            moves.push("Left".to_string());
        }
        if x < GRID_WIDTH - 1 && self.grid[y as usize][(x + 1) as usize] == 0 {
            moves.push("Right".to_string());
        }
        if y > 0 && self.grid[(y - 1) as usize][x as usize] == 0 {
            moves.push("Up".to_string());
        }
        if y < GRID_HEIGHT - 1 && self.grid[(y + 1) as usize][x as usize] == 0 {
            moves.push("Down".to_string());
        }

        moves
    }
}

fn main() {
    let (mut rl, thread) = raylib::init()
        .size(WIDTH, HEIGHT)
        .title("Maze Generator")
        .build();
    rl.set_target_fps(60);
    match Image::load_image("assets/icon.png") {
        Ok(icon) => {
            rl.set_window_icon(&icon);
        },
        Err(e) => {
            eprintln!("Failed to load icon: {:?}", e);
        }
    }

    let mut maze = Maze::new();
    maze.generate_maze(0, 0);

    let (mut player_x, mut player_y) = (0, 0);
    let (finish_x, finish_y) = (GRID_WIDTH - 2, GRID_HEIGHT - 2);
    let mut completed = false;
    let mut has_moved = true; // Flag to track if the player has moved
    let mut completion_message_printed = false; // Flag for completion message
    

    while !rl.window_should_close() {
        
        let mut update_player = |dx: i32, dy: i32| {
            let new_x = player_x + dx;
            let new_y = player_y + dy;
            if new_x >= 0 && new_x < GRID_WIDTH && new_y >= 0 && new_y < GRID_HEIGHT && maze.grid[new_y as usize][new_x as usize] == 0 {
                player_x = new_x;
                player_y = new_y;
                has_moved = true; // Set the flag to true when the player moves
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
            completion_message_printed = false; // Reset this flag when the player reaches the end
        }
    
        let mut d = rl.begin_drawing(&thread);
        d.clear_background(Color::WHITE);
    
        maze.draw(&mut d);

        if !completed {
            maze.highlight_moves(&mut d, player_x, player_y);
            if has_moved {
                let possible_moves = maze.get_possible_moves(player_x, player_y);
                println!("Possible Moves: {:?}", possible_moves);
                has_moved = false; // Reset the flag after printing the moves
            }
        } 
        if completed && !completion_message_printed {
            println!("Congratulations! You've completed the maze!");
            completion_message_printed = true; // Set the flag after printing the message
        }
        if completed {
            d.draw_text("Congratulations! You've completed the maze!", WIDTH/12, HEIGHT/2, 30, Color::RED);
        }
        
        

        d.draw_rectangle(player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::RED);
        d.draw_rectangle(finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::GREEN);
    }
    
}
