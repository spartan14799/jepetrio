// src/search.rs

use crate::board_utils::{check_collision, hard_drop};
use crate::heuristics::calculate_metrics;
use crate::pieces::get_piece_rotations;

#[derive(Clone, Debug)]
pub struct Move {
    pub board: Vec<Vec<i32>>,
    pub cleared_lines: i32,
    pub actions: Vec<String>,
    pub score: f64,
    pub held_piece: String,
}

pub fn evaluate_board(board: &Vec<Vec<i32>>, cleared_lines: i32, held_piece: &str) -> f64 {
    let metrics = calculate_metrics(board);
    let w_holes = -25.0;
    let w_bumpiness = -2.0;
    let w_height = -25.0;

    let mut score = (metrics.holes as f64 * w_holes)
        + (metrics.bumpiness as f64 * w_bumpiness)
        + (metrics.aggregate_height as f64 * w_height);

    if cleared_lines >= 4 {
        score += 1000.0;
    }
    if held_piece == "I" {
        score += 500.0;
    }

    score
}

pub fn generate_moves(
    board: &Vec<Vec<i32>>,
    piece_to_play: &str,
    held_piece_after: &str,
    is_hold: bool,
) -> Vec<Move> {
    let mut moves = Vec::new();
    let rotations = get_piece_rotations(piece_to_play);

    for (rot_idx, piece_shape) in rotations.iter().enumerate() {
        if piece_shape.is_empty() {
            continue;
        }

        let shape_cols = piece_shape[0].len() as i32;

        for c in 0..=(10 - shape_cols) {
            if check_collision(board, piece_shape, 0, c) {
                continue;
            }

            let (new_board, cleared_lines) = hard_drop(board, piece_shape, c);

            let mut actions = Vec::new();
            if is_hold {
                actions.push("hold".to_string());
            }

            match rot_idx {
                1 => actions.push("up".to_string()),
                2 => actions.push("a".to_string()),
                3 => actions.push("z".to_string()),
                _ => {}
            }

            let spawn_c = 3;
            let diff = c - spawn_c;
            if diff < 0 {
                for _ in 0..diff.abs() {
                    actions.push("left".to_string());
                }
            } else if diff > 0 {
                for _ in 0..diff {
                    actions.push("right".to_string());
                }
            }

            actions.push("space".to_string());
            moves.push(Move {
                board: new_board,
                cleared_lines,
                actions,
                score: f64::NEG_INFINITY,
                held_piece: held_piece_after.to_string(),
            });
        }
    }
    moves
}

pub fn dfs_search(
    board: Vec<Vec<i32>>,
    incoming_queue: &[String],
    depth: usize,
    accumulated_lines: i32,
    current_held_piece: &str,
) -> f64 {
    if depth == 0 || incoming_queue.is_empty() {
        return evaluate_board(&board, accumulated_lines, current_held_piece);
    }

    let current_piece = incoming_queue[0].as_str();
    let queue_for_future = &incoming_queue[1..];
    let mut best_score_in_branch = f64::NEG_INFINITY;

    let mut possible_moves = generate_moves(&board, current_piece, current_held_piece, false);

    let piece_to_play_if_hold: &str;
    let next_held_piece: &str;
    let mut advanced_queue_for_hold = queue_for_future;

    if current_held_piece == "" {
        if !queue_for_future.is_empty() {
            piece_to_play_if_hold = queue_for_future[0].as_str();
            next_held_piece = current_piece;
            advanced_queue_for_hold = &queue_for_future[1..];
        } else {
            piece_to_play_if_hold = "";
            next_held_piece = "";
        }
    } else {
        piece_to_play_if_hold = current_held_piece;
        next_held_piece = current_piece;
    }

    if piece_to_play_if_hold != "" {
        let mut hold_moves = generate_moves(&board, piece_to_play_if_hold, next_held_piece, true);
        possible_moves.append(&mut hold_moves);
    }

    for mov in possible_moves {
        let total_lines = accumulated_lines + mov.cleared_lines;

        let queue_to_send =
            if !mov.actions.is_empty() && mov.actions[0] == "hold" && current_held_piece == "" {
                advanced_queue_for_hold
            } else {
                queue_for_future
            };

        let score = dfs_search(
            mov.board,
            queue_to_send,
            depth - 1,
            total_lines,
            &mov.held_piece,
        );

        if score > best_score_in_branch {
            best_score_in_branch = score;
        }
    }

    best_score_in_branch
}
