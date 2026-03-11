mod board_utils;
mod heuristics;
mod pieces;
mod search;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use rayon::prelude::*;
use search::{dfs_search, generate_moves};

#[pyfunction]
fn compute_best_move(
    py: Python,
    board_py: Vec<Vec<i32>>,
    incoming_queue: Vec<String>,
    current_held_piece: String,
    max_depth: usize,
) -> PyResult<Py<PyAny>> {
    if incoming_queue.is_empty() {
        return Ok(py.None());
    }

    let current_piece = incoming_queue[0].as_str();

    let mut possible_moves = generate_moves(&board_py, current_piece, &current_held_piece, false);

    let piece_if_hold: &str;
    let next_held: &str;
    let mut queue_for_children = &incoming_queue[1..];

    if current_held_piece == "" {
        if incoming_queue.len() > 1 {
            piece_if_hold = incoming_queue[1].as_str();
            next_held = current_piece;
            queue_for_children = &incoming_queue[2..];
        } else {
            piece_if_hold = "";
            next_held = "";
        }
    } else {
        piece_if_hold = current_held_piece.as_str();
        next_held = current_piece;
    }

    if piece_if_hold != "" {
        let mut hold_moves = generate_moves(&board_py, piece_if_hold, next_held, true);
        possible_moves.append(&mut hold_moves);
    }

    #[allow(deprecated)]
    let best_move = py.allow_threads(|| {
        possible_moves
            .into_par_iter()
            .map(|mut mov| {
                let queue_to_send = if !mov.actions.is_empty()
                    && mov.actions[0] == "hold"
                    && current_held_piece == ""
                {
                    queue_for_children
                } else {
                    &incoming_queue[1..]
                };

                mov.score = dfs_search(
                    mov.board.clone(),
                    queue_to_send,
                    max_depth.saturating_sub(1),
                    mov.cleared_lines,
                    &mov.held_piece,
                );
                mov
            })
            .max_by(|a, b| a.score.partial_cmp(&b.score).unwrap())
    });

    let dict = PyDict::new(py);
    if let Some(best) = best_move {
        dict.set_item("actions", best.actions)?;
        dict.set_item("score", best.score)?;
        dict.set_item("held_piece", best.held_piece)?;
        return Ok(dict.into());
    }
    Ok(py.None())
}

#[pymodule]
fn tetris_motor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_best_move, m)?)?;
    Ok(())
}
