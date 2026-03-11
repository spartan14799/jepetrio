pub fn get_piece_rotations(piece: &str) -> Vec<Vec<Vec<i32>>> {
    match piece {
        "I" => vec![
            vec![vec![0, 0, 0, 0], vec![1, 1, 1, 1], vec![0, 0, 0, 0], vec![0, 0, 0, 0]],
            vec![vec![0, 0, 1, 0], vec![0, 0, 1, 0], vec![0, 0, 1, 0], vec![0, 0, 1, 0]],
        ],
        "J" => vec![
            vec![vec![1, 0, 0], vec![1, 1, 1], vec![0, 0, 0]],
            vec![vec![0, 1, 1], vec![0, 1, 0], vec![0, 1, 0]],
            vec![vec![0, 0, 0], vec![1, 1, 1], vec![0, 0, 1]],
            vec![vec![0, 1, 0], vec![0, 1, 0], vec![1, 1, 0]],
        ],
        "L" => vec![
            vec![vec![0, 0, 1], vec![1, 1, 1], vec![0, 0, 0]],
            vec![vec![0, 1, 0], vec![0, 1, 0], vec![0, 1, 1]],
            vec![vec![0, 0, 0], vec![1, 1, 1], vec![1, 0, 0]],
            vec![vec![1, 1, 0], vec![0, 1, 0], vec![0, 1, 0]],
        ],
        "O" => vec![
            vec![vec![0, 0, 0], vec![0, 1, 1], vec![0, 1, 1]],
        ],
        "S" => vec![
            vec![vec![0, 1, 1], vec![1, 1, 0], vec![0, 0, 0]],
            vec![vec![0, 1, 0], vec![0, 1, 1], vec![0, 0, 1]],
        ],
        "T" => vec![
            vec![vec![0, 1, 0], vec![1, 1, 1], vec![0, 0, 0]],
            vec![vec![0, 1, 0], vec![0, 1, 1], vec![0, 1, 0]],
            vec![vec![0, 0, 0], vec![1, 1, 1], vec![0, 1, 0]],
            vec![vec![0, 1, 0], vec![1, 1, 0], vec![0, 1, 0]],
        ],
        "Z" => vec![
            vec![vec![1, 1, 0], vec![0, 1, 1], vec![0, 0, 0]],
            vec![vec![0, 0, 1], vec![0, 1, 1], vec![0, 1, 0]],
        ],
        _ => vec![],
    }
}
