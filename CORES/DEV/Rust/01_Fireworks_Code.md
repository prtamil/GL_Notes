```rs
PS C:\Users\trangasami\Programming\Rust\fireworks> cat .\Cargo.toml
[package]
name = "fireworks"
version = "0.1.0"
edition = "2021"

[dependencies]
crossterm = "0.29.0"
rand = "0.9.1"
PS C:\Users\trangasami\Programming\Rust\fireworks> cat .\src\main.rs
use crossterm::{
    cursor,
    event::{self, Event, KeyCode},
    execute,
    style::{Color, Print, ResetColor, SetForegroundColor},
    terminal::{self, ClearType},
};
use rand::{prelude::*, rng};
use std::{
    io::{stdout, Write, Result},
    sync::{Arc, Mutex},
    thread,
    time::{Duration, Instant},
};

const FRAME_RATE: u64 = 30;
const MAX_PARTICLE_AGE: u8 = 30;

#[derive(Clone)]
struct Particle {
    x: f32,
    y: f32,
    dx: f32,
    dy: f32,
    age: u8,
    symbol: char,
    color: Color,
}

impl Particle {
    fn update(&mut self) {
        self.x += self.dx;
        self.y += self.dy;
        self.dy += 0.05; // gravity
        self.age = self.age.saturating_sub(1);
    }

    fn draw(&self, frame: &mut Frame, color_frame: &mut ColorFrame) {
        let xi = self.x.round() as usize;
        let yi = self.y.round() as usize;
        if yi < frame.len() && xi < frame[0].len() {
            let intensity = match self.age {
                25..=30 => self.symbol,
                15..=24 => '+',
                5..=14 => '.',
                _ => ' ',
            };
            frame[yi].replace_range(xi..=xi, &intensity.to_string());
            color_frame[yi][xi] = Some(self.color);
        }
    }

    fn is_alive(&self) -> bool {
        self.age > 0
    }
}

type Frame = Vec<String>;
type ColorFrame = Vec<Vec<Option<Color>>>;

fn blank_frame(width: u16, height: u16) -> Frame {
    vec![" ".repeat(width as usize); height as usize]
}

fn blank_color_frame(width: u16, height: u16) -> ColorFrame {
    vec![vec![None; width as usize]; height as usize]
}

fn diff_and_draw(
    old: &Frame,
    old_colors: &ColorFrame,
    new: &Frame,
    new_colors: &ColorFrame,
    stdout: &mut std::io::Stdout,
) -> Result<()> {
    for y in 0..new.len() {
        let new_row = &new[y];
        let old_row = &old[y];
        for x in 0..new_row.len() {
            let nc = new_row.chars().nth(x).unwrap();
            let oc = old_row.chars().nth(x).unwrap();
            let nc_color = new_colors[y][x];
            let oc_color = old_colors[y][x];
            if nc != oc || nc_color != oc_color {
                execute!(
                    stdout,
                    cursor::MoveTo(x as u16, y as u16),
                    SetForegroundColor(nc_color.unwrap_or(Color::White)),
                    Print(nc)
                )?;
            }
        }
    }
    execute!(stdout, ResetColor)?;
    stdout.flush()
}

fn spawn_firework(width: u16, height: u16) -> Vec<Particle> {
    let mut rng = rng();
    let x = rng.random_range(10.0..(width - 10) as f32);
    let y = rng.random_range(5.0..(height / 2) as f32);
    let colors = [Color::Red, Color::Yellow, Color::Blue, Color::Magenta, Color::Cyan, Color::Green];
    let color = *colors.choose(&mut rng).unwrap();

    (0..30)
        .map(|_| {
            let angle = rng.random_range(0.0..std::f32::consts::TAU);
            let speed = rng.random_range(0.5..2.0);
            Particle {
                x,
                y,
                dx: angle.cos() * speed,
                dy: angle.sin() * speed,
                age: MAX_PARTICLE_AGE,
                symbol: '*',
                color,
            }
        })
        .collect()
}

fn main() -> Result<()> {
    let (width, height) = terminal::size()?;
    let mut stdout = stdout();

    execute!(
        stdout,
        terminal::EnterAlternateScreen,
        terminal::Clear(ClearType::All),
        cursor::Hide
    )?;

    terminal::enable_raw_mode()?;

    let particles = Arc::new(Mutex::new(Vec::<Particle>::new()));
    let particles_clone = Arc::clone(&particles);

    // Firework generator thread
    thread::spawn(move || loop {
        {
            let mut p = particles_clone.lock().unwrap();
            p.extend(spawn_firework(width, height));
        }
        thread::sleep(Duration::from_millis(1000));
    });

    let mut frame1 = blank_frame(width, height);
    let mut frame2 = blank_frame(width, height);
    let mut color1 = blank_color_frame(width, height);
    let mut color2 = blank_color_frame(width, height);
    let mut current = true;
    let mut last_frame = Instant::now();

    loop {
        // FPS logic
        let now = Instant::now();
        let delta = now.duration_since(last_frame);
        let fps = if delta.as_secs_f32() > 0.0 {
            1.0 / delta.as_secs_f32()
        } else {
            0.0
        };
        last_frame = now;

        // Quit on key press
        if event::poll(Duration::from_millis(0))? {
            if let Event::Key(k) = event::read()? {
                if k.code == KeyCode::Char('q') || k.code == KeyCode::Esc {
                    break;
                }
            }
        }

        // Prepare current and old frames
        let (frame, old_frame) = if current {
            (&mut frame1, &mut frame2)
        } else {
            (&mut frame2, &mut frame1)
        };

        let (color_frame, old_color_frame) = if current {
            (&mut color1, &mut color2)
        } else {
            (&mut color2, &mut color1)
        };

        *frame = blank_frame(width, height);
        *color_frame = blank_color_frame(width, height);

        // Draw particles
        {
            let mut p = particles.lock().unwrap();
            for particle in p.iter_mut() {
                particle.update();
                particle.draw(frame, color_frame);
            }
            p.retain(|p| p.is_alive());
        }

        // Draw FPS counter
        let fps_display = format!("FPS: {:.1}", fps);
        frame[0].replace_range(0..fps_display.len(), &fps_display);
        for (i, _c) in fps_display.chars().enumerate() {
            color_frame[0][i] = Some(Color::DarkGrey);
        }

        diff_and_draw(old_frame, old_color_frame, frame, color_frame, &mut stdout)?;

        current = !current;
        thread::sleep(Duration::from_millis(1000 / FRAME_RATE));
    }

    execute!(
        stdout,
        terminal::LeaveAlternateScreen,
        cursor::Show,
        ResetColor
    )?;
    terminal::disable_raw_mode()?;
    Ok(())
}
```