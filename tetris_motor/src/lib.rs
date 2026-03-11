use pyo3::prelude::*;
use pyo3::types::PyDict;
use rayon::prelude::*;
mod heuristics;
use heuristics::calculate_metrics;

#[derive(Clone, Debug)]
struct Move {
    board: Vec<Vec<i32>>,
    cleared_lines: i32,
    actions: Vec<String>,
    score: f64,
    held_piece: String,
}

fn evaluate_board(board: &Vec<Vec<i32>>, cleared_lines: i32, held_piece: &str) -> f64 {
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

#[pyfunction]
fn compute_best_move(
    py: Python,
    board_py: Vec<Vec<i32>>,
    incoming_queue: Vec<String>,
    current_held_piece: String,
    max_depth: usize,
) -> PyResult<Py<PyAny>> {
    // TODO: generar los movimientos base.
    let possible_moves = vec![
        Move {
            board: board_py.clone(),
            cleared_lines: 0,
            actions: vec!["right".to_string(), "space".to_string()],
            score: f64::NEG_INFINITY,
            held_piece: current_held_piece.clone(),
        },
        Move {
            board: board_py.clone(),
            cleared_lines: 1,
            actions: vec!["hold".to_string(), "left".to_string(), "space".to_string()],
            score: f64::NEG_INFINITY,
            held_piece: "T".to_string(),
        },
    ];
    #[allow(deprecated)]
    let best_move = py.allow_threads(|| {
        possible_moves
            .into_par_iter()
            .map(|mut mov| {
                // TODO: Crear DFS.
                mov.score = evaluate_board(&mov.board, mov.cleared_lines, &mov.held_piece);
                mov
            })
            .max_by(|a, b| a.score.partial_cmp(&b.score).unwrap())
    });

    let dict = PyDict::new(py);
    if let Some(best) = best_move {
        dict.set_item("action", best.actions)?;
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
