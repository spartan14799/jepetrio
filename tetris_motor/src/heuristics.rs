pub struct BoardMetrics {
    pub holes: i32,
    pub bumpiness: i32,
    pub aggregate_height: i32,
    pub blocks_in_well: i32,
}

#[inline(always)]
pub fn calculate_metrics(board: &Vec<Vec<i32>>) -> BoardMetrics {
    let rows = 20;
    let cols = 10;

    let mut holes = 0;
    let mut aggregate_height = 0;
    let mut col_heights = vec![0; cols];
    let mut blocks_in_well = 0;

    for c in 0..cols {
        let mut block_found = false;
        for r in 0..rows {
            if board[r][c] == 1 {
                if !block_found {
                    col_heights[c] = (rows - r) as i32;
                    aggregate_height += col_heights[c];
                    block_found = true;
                }
                if c == 9 {
                    blocks_in_well += 1;
                }
            } else if block_found && board[r][c] == 0 {
                holes += 1;
            }
        }
    }
    let mut bumpiness = 0;
    for c in 0..(cols - 1) {
        bumpiness += (col_heights[c] - col_heights[c + 1]).abs();
    }
    BoardMetrics {
        holes,
        bumpiness,
        aggregate_height,
        blocks_in_well,
    }
}
