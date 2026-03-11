pub fn check_collision(
    board: &Vec<Vec<i32>>,
    piece_shape: &Vec<Vec<i32>>,
    offset_r: i32,
    offset_c: i32,
) -> bool {
    let shape_rows = piece_shape.len() as i32;
    let shape_cols = piece_shape[0].len() as i32;

    for r in 0..shape_rows {
        for c in 0..shape_cols {
            if piece_shape[r as usize][c as usize] != 0 {
                let board_r = offset_r + r;
                let board_c = offset_c + c;

                if board_r >= 20 || board_c < 0 || board_c >= 10 {
                    return true;
                }
                if board_r >= 0 {
                    if board[board_r as usize][board_c as usize] != 0 {
                        return true;
                    }
                }
            }
        }
    }
    false
}

pub fn hard_drop(
    board: &Vec<Vec<i32>>,
    piece_shape: &Vec<Vec<i32>>,
    start_c: i32,
) -> (Vec<Vec<i32>>, i32) {
    let mut current_r = 0;

    while !check_collision(board, piece_shape, current_r + 1, start_c) {
        current_r += 1;
    }

    let mut new_board = board.clone();

    for r in 0..piece_shape.len() {
        for c in 0..piece_shape[0].len() {
            if piece_shape[r][c] != 0 {
                let br = (current_r + r as i32) as usize;
                let bc = (start_c + c as i32) as usize;
                if br < 20 && bc < 10 {
                    new_board[br][bc] = 1;
                }
            }
        }
    }

    let cleared_lines = clear_lines(&mut new_board);

    (new_board, cleared_lines)
}

pub fn clear_lines(board: &mut Vec<Vec<i32>>) -> i32 {
    let mut lines_cleared = 0;
    let mut r = 19;
    
    while r > 0 {
        if !board[r].contains(&0) {
            lines_cleared += 1;
            for drop_r in (1..=r).rev() {
                board[drop_r] = board[drop_r - 1].clone();
            }
            board[0] = vec![0; 10];
        } else {
            r -= 1;
        }
    }
    lines_cleared
}
