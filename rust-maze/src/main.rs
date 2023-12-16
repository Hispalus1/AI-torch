extern crate raylib;
use raylib::prelude::*;
use rand::seq::SliceRandom;
use rand::thread_rng;

const WIDTH: i32 = 800;
const HEIGHT: i32 = 600;
const GRID_SIZE: i32 = 20;
const GRID_WIDTH: i32 = WIDTH / GRID_SIZE;
const GRID_HEIGHT: i32 = HEIGHT / GRID_SIZE;

struct Maze {
    grid: Vec<Vec<i32>>,
}

impl Maze {
    fn new() -> Self {
        let grid = vec![vec![1; GRID_WIDTH as usize]; GRID_HEIGHT as usize];
        Self { grid }
    }

    fn generate_maze(&mut self, x: usize, y: usize) {
        self.grid[y][x] = 0;
        let mut dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)];
        let mut rng = thread_rng();
        dirs.shuffle(&mut rng);

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
}

fn main() {
    let (mut rl, thread) = raylib::init()
        .size(WIDTH, HEIGHT)
        .title("Maze Generator")
        .build();

    let mut maze = Maze::new();
    maze.generate_maze(0, 0);

    let (mut player_x, mut player_y) = (0, 0);
    let (finish_x, finish_y) = (GRID_WIDTH - 2, GRID_HEIGHT - 2);
    let mut completed = false;

    while !rl.window_should_close() {
        let mut update_player = |dx: i32, dy: i32| {
            let new_x = player_x + dx;
            let new_y = player_y + dy;
            if new_x >= 0 && new_x < GRID_WIDTH && new_y >= 0 && new_y < GRID_HEIGHT && maze.grid[new_y as usize][new_x as usize] == 0 {
                player_x = new_x;
                player_y = new_y;
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

        if player_x == finish_x && player_y == finish_y {
            completed = true;
        }

        let mut d = rl.begin_drawing(&thread);
        d.clear_background(Color::WHITE);

        maze.draw(&mut d);

        d.draw_rectangle(player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::RED);
        d.draw_rectangle(finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE, Color::GREEN);

        if completed {
            let font_size = 20;
            let message = "Congratulations! You've completed the maze!";
            let text_width = measure_text(message, font_size);
            d.draw_text(message, (WIDTH - text_width) / 2, HEIGHT / 2 - font_size / 2, font_size, Color::BLUE);
        }
        
    }
}
