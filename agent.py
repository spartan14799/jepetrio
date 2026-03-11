from typing import Sequence, List
from dataclasses import dataclass, field
import pyautogui
from time import sleep
import numpy as np
import concurrent.futures
import queue
import threading


# INFO: Estructura usada para la comunicacion entre los niveles del arbol
# Usamos  slots=True para hacerla mas rapida que un diccionario
@dataclass(slots=True)
class Move:
    board: np.ndarray
    cleared_lines: int
    actions: List[str] = field(default_factory=list)
    score: float = float("-inf")
    held_piece: str = ""

    def __lt__(self, other):
        return self.score < other.score


class Agent:
    COORDINATES = np.array(
        [
            [
                (208, 1317),
                (208, 1318),
                (208, 1319),
                (208, 1320),
                (208, 1321),
                (208, 1322),
            ],
            [
                (335, 1317),
                (335, 1318),
                (335, 1319),
                (335, 1320),
                (335, 1321),
                (335, 1322),
            ],
            [
                (472, 1317),
                (472, 1318),
                (472, 1319),
                (472, 1320),
                (472, 1321),
                (472, 1322),
            ],
            [
                (609, 1317),
                (609, 1318),
                (609, 1319),
                (609, 1320),
                (609, 1321),
                (609, 1322),
            ],
            [
                (752, 1317),
                (752, 1318),
                (752, 1319),
                (752, 1320),
                (752, 1321),
                (752, 1322),
            ],
        ]
    )

    COLOR_RANGES = {
        "T": ((128, 218), (63, 106), (128, 215)),
        "Z": ((144, 240), (52, 97), (59, 111)),
        "S": ((110, 180), (130, 230), (52, 100)),
        "L": ((141, 245), (89, 150), (51, 104)),
        "J": ((77, 121), (63, 103), (136, 226)),
        "I": ((49, 98), (144, 229), (111, 178)),
        "O": ((160, 200), (140, 170), (51, 70)),
    }

    def __init__(self, weights=None):
        self.current_board = np.zeros((20, 10), dtype=int)
        self.hold = ""
        self.current_playing_piece = None
        # Cambio: Pesos modificados para priorizar Tetris y evitar huecos en early game
        self.weights = (
            weights
            if weights
            else {
                "holes": -40.0,           
                "bumpiness": -3.0,        
                "aggregate_height": -15.0, 
                "block_in_well": -0.1,    
                "incomplete_clear": -20, 
                "tetris": 100.0,          
                "well_depth": 15.0,       # Nuevo: Bonus por profundidad del well
                "flat_top": 20.0,         # Nuevo: Bonus por top plano en 9 columnas
            }
        )

        self.well_column = 9
        self.rows = 20
        self.cols = 10

        # Representación matricial (Bounding boxes de 4x4, 3x3 y 2x2)
        self.maping_pieces = {
            "I": [
                np.array([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]]),
                np.array([[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]]),
            ],
            "J": [
                np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]]),
                np.array([[0, 1, 1], [0, 1, 0], [0, 1, 0]]),
                np.array([[0, 0, 0], [1, 1, 1], [0, 0, 1]]),
                np.array([[0, 1, 0], [0, 1, 0], [1, 1, 0]]),
            ],
            "L": [
                np.array([[0, 0, 1], [1, 1, 1], [0, 0, 0]]),
                np.array([[0, 1, 0], [0, 1, 0], [0, 1, 1]]),
                np.array([[0, 0, 0], [1, 1, 1], [1, 0, 0]]),
                np.array([[1, 1, 0], [0, 1, 0], [0, 1, 0]]),
            ],
            "O": [np.array([[0,0,0], [0, 1, 1], [0, 1, 1]])],
            # "O": [np.array([[1, 1], [1, 1]])],
            "S": [
                np.array([[0, 1, 1], [1, 1, 0], [0, 0, 0]]),
                np.array([[0, 1, 0], [0, 1, 1], [0, 0, 1]]),
            ],
            "T": [
                np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]]),
                np.array([[0, 1, 0], [0, 1, 1], [0, 1, 0]]),
                np.array([[0, 0, 0], [1, 1, 1], [0, 1, 0]]),
                np.array([[0, 1, 0], [1, 1, 0], [0, 1, 0]]),
            ],
            "Z": [
                np.array([[1, 1, 0], [0, 1, 1], [0, 0, 0]]),
                np.array([[0, 0, 1], [0, 1, 1], [0, 1, 0]]),
            ],
        }

        self.queue_outputs = queue.Queue()
        self.thread_action = threading.Thread(
            target=self.action, args=(self.queue_outputs,), daemon=True
        )
        self.thread_action.start()

    # Execute actions
    def action(self, queue_outputs):
        keys = {
            "left": "left",
            "right": "right",
            "soft_drop": "down",
            "hard_drop": "space",
            "rotate_countercw": "z",
            "rotate_cw": "x",
            "hold": "c",
            "rotate_180": "a",
        }

        while True:
            comand = queue_outputs.get()

            if comand == "^":
                break

            if comand in keys:
                key = keys[comand]
                pyautogui.press(key)
                # pyautogui.keyDown(key)
                # sleep(0.1)
                # pyautogui.keyUp(key)
                # sleep(0.2)

            else:
                print(f"Movimiento no reconocido: {comand}")

    def percept(self, screenshot: np.typing.NDArray[np.uint8] | None) -> list | None:
        if screenshot is None:
            return None
        return [
            self.most_frequent(self.possible_colors(screenshot, i)) for i in range(0, 5)
        ]

    def possible_colors(
        self, screenshot: np.typing.NDArray[np.uint8], index: int
    ) -> list:
        return [self.color(screenshot[r, c]) for r, c in self.COORDINATES[index]]

    def color(self, rgb: np.typing.NDArray[np.uint8] | Sequence[int]) -> str | None:
        r, g, b = rgb
        for name, (
            (r_min, r_max),
            (g_min, g_max),
            (b_min, b_max),
        ) in self.COLOR_RANGES.items():
            if r_min <= r <= r_max and g_min <= g <= g_max and b_min <= b <= b_max:
                return name
        return None

    def most_frequent(self, lista: list) -> str:
        return max(set(lista), key=lista.count)

    # Cambio: Firma modificada para recibir incoming_queue
    def evaluate_move(self, board, cleared_lines, held_piece, incoming_queue=None):
        holes = self._count_holes(board)

        # Nuevo: Penalización masiva por huecos en líneas 1-3 en early game
        early_game_penalty = 0.0
        if self._is_early_game(board):
            bottom_holes = self._count_bottom_holes(board, 3)  # Huecos en últimas 3 filas
            if bottom_holes > 0:
                early_game_penalty = 5000 * bottom_holes  # Penalización extrema


        bumpiness = self._calculate_bumpiness(board)
        aggregate_height = self._calculate_aggregate_height(board)
        blocks_in_well = self._count_blocks_in_well(board)

        # Nuevo: Métricas de well-building
        well_depth = self._calculate_well_depth(board)
        flatness = self._calculate_flatness(board)
        has_i_ready = self._has_i_piece_ready(held_piece, incoming_queue)
        covered_well = self._count_covered_in_well(board)

        is_tetris = 1 if cleared_lines >= 4 else 0
        incomplete_clear = cleared_lines if 0 < cleared_lines < 4 else 0

        score = (
            (self.weights["holes"] * holes)
            + (self.weights["bumpiness"] * bumpiness)
            + (self.weights["aggregate_height"] * aggregate_height)
            + (self.weights["block_in_well"] * blocks_in_well)
            + (self.weights["incomplete_clear"] * incomplete_clear)
            + (self.weights["tetris"] * is_tetris)
            + (self.weights["well_depth"] * well_depth)      # Nuevo
            + (self.weights["flat_top"] * flatness)          # Nuevo
            - early_game_penalty  # Nuevo: Restar penalización directamente
        )
        
        # Cambio: Bonus masivo por Tetris
        if is_tetris == 1:
            score += 10000.0  # Cambio: Era 1000.0
        
        # Nuevo: Bonus por tener I lista con well profundo
        if has_i_ready and well_depth >= 3:
            score += 8000.0 * well_depth  
        elif has_i_ready:
            score += 1000.0
        
        # Nuevo: Penalizar si cubrimos el well
        score += self.weights["holes"] * covered_well * 3
        
        # Nuevo: Penalización extrema por limpiar pocas líneas
        bottom_holes_count = self._count_bottom_holes(board, 3) if self._is_early_game(board) else 0
        
        if 0 < cleared_lines < 4:
            if bottom_holes_count > 0 and cleared_lines >= 1:
                score += 1000.0 * cleared_lines
            else:
                score -= 500.0 * (4 - cleared_lines)
                if well_depth >= 2:
                    score -= 1000.0
        
        # Nuevo: Penalizar quedarse bajo sin hacer Tetris
        if aggregate_height < 10 and is_tetris == 0:
            score -= 1000.0

        # Nuevo: Penalizar huecos en la parte baja del tablero (especialmente early game)
        low_holes = self._count_low_holes(board)
        score += self.weights["holes"] * low_holes * 5
        
        # Nuevo: Penalizar específicamente huecos en primera línea en early game
        if self._is_early_game(board) and cleared_lines == 0:
            first_row_holes = self._count_first_row_holes(board)
            if first_row_holes > 0:
                score -= 2000.0 * first_row_holes

        return score

    # INFO: Funciones para calcular la combinacion lineal:

    def _count_holes(self, board):
        # Cambio: Penalización ponderada por altura del hueco
        accumulated_blocks = np.maximum.accumulate(board, axis=0)
        holes = (board == 0) & (accumulated_blocks == 1)
        
        # Nuevo: Peso extra para huecos en filas bajas (líneas 0-5 desde abajo)
        row_weights = np.ones(self.rows)
        for i in range(self.rows):
            # Filas más bajas (índices altos) tienen mayor peso
            if i >= self.rows - 5:  # Últimas 5 filas
                row_weights[i] = 5.0  # Peso 10x para huecos en base
            elif i >= self.rows - 10:  # Filas 6-10 desde abajo
                row_weights[i] = 5.0   # Peso 5x para huecos medios-bajos
            else:
                row_weights[i] = 2.0   # Peso normal para huecos altos
        
        weighted_holes = holes * row_weights.reshape(-1, 1)
        return int(np.sum(weighted_holes))

    def _count_bottom_holes(self, board, num_rows=3):
        """Cuenta huecos específicamente en las últimas N filas."""
        holes = 0
        start_row = self.rows - num_rows  # Desde qué fila empezar
        
        for row in range(start_row, self.rows):
            for col in range(self.cols - 1):  # Excluir well
                if board[row, col] == 0:
                    # Verificar si hay bloques arriba (es un hueco)
                    if np.any(board[:row, col] == 1):
                        holes += 1
        return holes

    def _calculate_bumpiness(self, board):
        col_has_blocks = board.any(axis=0)
        heights = np.zeros(self.cols, dtype=int)
        heights[col_has_blocks] = self.rows - board.argmax(axis=0)[col_has_blocks]
        bumpiness = np.sum(np.abs(np.diff(heights)))
        return bumpiness
    
    def _calculate_aggregate_height(self, board):
        col_has_blocks = board.any(axis=0)
        heights = np.zeros(self.cols, dtype=int)
        heights[col_has_blocks] = self.rows - board.argmax(axis=0)[col_has_blocks]
        return np.sum(heights)

    def _count_blocks_in_well(self, board):
        return np.sum(board[:, self.well_column])

    # Nuevo: Métodos para well-building y early game
    def _calculate_well_depth(self, board):
        """Calcula profundidad del well en columna 9."""
        well_col = self.well_column
        depth = 0
        for row in range(self.rows - 1, -1, -1):
            if board[row, well_col] == 0:
                depth += 1
            else:
                break
        return depth

    def _calculate_flatness(self, board):
        """Calcula qué planas están las 9 columnas (excluyendo well)."""
        heights = np.zeros(self.cols, dtype=int)
        for col in range(self.cols):
            for row in range(self.rows):
                if board[row, col] == 1:
                    heights[col] = self.rows - row
                    break
        
        other_heights = np.delete(heights, self.well_column)
        if len(other_heights) == 0:
            return 0.0
        
        mean_h = np.mean(other_heights)
        variance = np.mean((other_heights - mean_h) ** 2)
        
        if variance < 1.0:
            return 1.0
        elif variance < 4.0:
            return 0.5
        return 0.0

    def _has_i_piece_ready(self, held_piece, incoming_queue):
        """Verifica si tenemos pieza I disponible pronto."""
        if held_piece == "I":
            return True
        if incoming_queue and incoming_queue[0] == "I":
            return True
        return False

    def _count_covered_in_well(self, board):
        """Cuenta celdas bloqueadas sobre el well."""
        well_col = self.well_column
        covered = 0
        found_block = False
        for row in range(self.rows):
            if board[row, well_col] == 1:
                found_block = True
            elif found_block:
                covered += 1
        return covered

    def _is_early_game(self, board):
        """Detecta si estamos en early game (< 20 bloques)."""
        return np.sum(board) < 20

    def _get_column_heights(self, board):
        """Altura de cada columna."""
        heights = np.zeros(self.cols, dtype=int)
        for col in range(self.cols):
            for row in range(self.rows):
                if board[row, col] == 1:
                    heights[col] = self.rows - row
                    break
        return heights

    def _count_low_holes(self, board):
        """Cuenta huecos en las primeras 5 filas desde abajo."""
        holes = 0
        for row in range(self.rows - 1, self.rows - 6, -1):
            for col in range(self.cols - 1):
                if board[row, col] == 0:
                    if np.any(board[:row, col] == 1):
                        holes += 1
        return holes

    def _count_first_row_holes(self, board):
        """Cuenta huecos en la fila más baja (primera línea de juego)."""
        holes = 0
        bottom_row = self.rows - 1
        for col in range(self.cols - 1):
            if board[bottom_row, col] == 0 and np.any(board[:bottom_row, col] == 1):
                holes += 1
        return holes

    # INFO: Metodos para alcanzar el mejor movimiento sin el hold.

    def get_best_move(
        self, incoming_queue, current_board, max_depth=3, current_held_piece=""
    ):
        best_score = float("-inf")
        best_move = None

        if not incoming_queue:
            return None

        current_piece = incoming_queue[0]

        possible_moves = self._generate_moves_with_hold(
            current_board, current_piece, incoming_queue[1:], current_held_piece
        )

        for move in possible_moves:
            queue_for_future = incoming_queue[1:]
            if move.actions and move.actions[0] == "hold" and current_held_piece == "":
                queue_for_future = incoming_queue[2:] if len(incoming_queue) > 1 else []

            # Cambio: Pasar incoming_queue a _dfs_search
            score = self._dfs_search(
                board=move.board,
                incoming_queue=queue_for_future,
                depth=max_depth - 1,
                accumulated_lines=move.cleared_lines,
                current_held_piece=move.held_piece,
                original_queue=incoming_queue,  # Nuevo
            )

            if score > best_score:
                best_score = score
                move.score = score
                best_move = move

        return best_move

    # Cambio: Firma modificada para recibir original_queue
    def _dfs_search(
        self, board, incoming_queue, depth, accumulated_lines, current_held_piece, original_queue=None
    ) -> float:
        if depth == 0 or not incoming_queue:
            # Cambio: Pasar cola para evaluar I piece
            return self.evaluate_move(board, accumulated_lines, current_held_piece, original_queue)

        current_piece = incoming_queue[0]

        possible_moves = self._generate_moves_with_hold(
            board, current_piece, incoming_queue[1:], current_held_piece
        )

        if not possible_moves:
            return float("-inf")

        best_score_in_branch = float("-inf")

        for move in possible_moves:
            total_lines = accumulated_lines + move.cleared_lines

            queue_for_future = incoming_queue[1:]
            if move.actions and move.actions[0] == "hold" and current_held_piece == "":
                queue_for_future = incoming_queue[2:] if len(incoming_queue) > 1 else []

            # Cambio: Pasar original_queue recursivamente
            score = self._dfs_search(
                board=move.board,
                incoming_queue=queue_for_future,
                depth=depth - 1,
                accumulated_lines=total_lines,
                current_held_piece=move.held_piece,
                original_queue=original_queue,
            )

            if score > best_score_in_branch:
                best_score_in_branch = score

        return best_score_in_branch

    def _generate_all_moves(self, board, piece_name) -> list[Move]:
        possible_moves = []

        rotations = self.maping_pieces[piece_name]

        for rot_idx, piece_matrix in enumerate(rotations):
            _, blocks_x = np.where(piece_matrix == 1)

            for x in range(-3, self.cols + 1):
                board_x = blocks_x + x

                if np.any(board_x < 0) or np.any(board_x >= self.cols):
                    continue

                drop_y = self._get_drop_position(board, piece_matrix, x)

                new_board = self._place_piece(board, piece_matrix, x, drop_y)

                final_board, cleared_lines = self._clear_lines(new_board)

                # Revisar bien
                spawn_col = 3
                actions = []
                for _ in range(rot_idx):
                    actions.append("rotate_cw")

                if x < spawn_col:
                    actions.extend(["left"] * (spawn_col - x))

                elif x > spawn_col:
                    actions.extend(["right"] * (x - spawn_col))

                actions.append("hard_drop")
                move = Move(
                    board=final_board, cleared_lines=cleared_lines, actions=actions
                )

                possible_moves.append(move)

        return possible_moves

    def _check_collision(self, board, piece_matrix, offset_x, offset_y):
        block_y, block_x = np.where(piece_matrix == 1)

        board_y = block_y + offset_y
        board_x = block_x + offset_x

        if (
            np.any(board_x < 0)
            or np.any(board_x >= self.cols)
            or np.any(board_y >= self.rows)
        ):
            return True

        valids = board_y >= 0
        board_y_valids = board_y[valids]
        board_x_valids = board_x[valids]

        if np.any(board[board_y_valids, board_x_valids] == 1):
            return True

        return False

    def _get_drop_position(self, board, piece_matrix, offset_x):
        curret_y = -2
        while not self._check_collision(board, piece_matrix, offset_x, curret_y):
            curret_y += 1

        return curret_y - 1

    def _place_piece(self, board, piece_matrix, offset_x, offset_y):
        new_board = (
            board.copy()
        )  # INFO: para evitar que se sobreescriba sobre el tablero
        block_y, block_x = np.where(piece_matrix == 1)

        board_y = block_y + offset_y
        board_x = block_x + offset_x

        valids = board_y >= 0
        board_y_valids = board_y[valids]
        board_x_valids = board_x[valids]

        new_board[board_y_valids, board_x_valids] = 1
        return new_board

    def _clear_lines(self, board):
        filled_rows = np.all(board == 1, axis=1)
        num_row_cleared = np.sum(filled_rows)

        if num_row_cleared == 0:
            return board, 0

        remaining_rows = board[~filled_rows]
        cleared_rows = np.zeros((num_row_cleared, self.cols), dtype=int)
        new_board = np.vstack((cleared_rows, remaining_rows))

        return new_board, num_row_cleared

    # INFO: Funciones para paralelizar

    def __getstate__(self):
        estado = self.__dict__.copy()
        estado["queue_outputs"] = None
        estado["thread_action"] = None
        return estado

    def __setstate__(self, estado):
        self.__dict__.update(estado)

    # Cambio: Firma modificada para recibir original_queue
    def _evaluate_single_branch(
        self, move, incoming_queue, max_depth, initial_held_piece, original_queue=None
    ):
        queue_for_future = incoming_queue[1:]

        if move.actions and move.actions[0] == "hold" and initial_held_piece == "":
            queue_for_future = incoming_queue[2:] if len(incoming_queue) > 1 else []

        # Fix: Asegurar que score siempre se asigne
        try:
            score = self._dfs_search(
                board=move.board,
                incoming_queue=queue_for_future,
                depth=max_depth - 1,
                accumulated_lines=move.cleared_lines,
                current_held_piece=move.held_piece,
                original_queue=original_queue,  # Nuevo
            )
        except Exception:
            score = float("-inf")  # Fix: Si falla, peor score posible
        
        move.score = score
        return move

    def compute(self, incoming_queue, max_depth=3, current_held_piece=""):
        best_score = float("-inf")
        best_move = Move(self.current_board, 0)

        if not incoming_queue:
            return None

        current_piece = incoming_queue[0]

        possible_moves = self._generate_moves_with_hold(
            self.current_board, current_piece, incoming_queue[1:], current_held_piece
        )

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for move in possible_moves:
                # Cambio: Pasar incoming_queue como original_queue
                future = executor.submit(
                    self._evaluate_single_branch,
                    move,
                    incoming_queue,
                    max_depth,
                    current_held_piece,
                    incoming_queue,  # Nuevo
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                evaluated_move = future.result()

                if evaluated_move.score > best_score:
                    best_score = evaluated_move.score
                    best_move = evaluated_move

        self.current_board = best_move.board
        print(best_move.actions)
        return best_move

    # INFO: Metodos para encontrar movimientos usando el hold
    #
    def _generate_moves_with_hold(
        self, current_board, current_piece, incoming_queue, current_held_piece
    ):
        """Genera movimientos normales Y movimientos usando el Hold."""
        all_moves = []

        # Nuevo: Solo generar normales si no tenemos I en hold con well listo
        well_depth = self._calculate_well_depth(current_board)
        if not (current_held_piece == "I" and well_depth >= 3):
            normal_moves = self._generate_all_moves(current_board, current_piece)
            for move in normal_moves:
                move.held_piece = current_held_piece
                all_moves.append(move)

        if current_held_piece == "":
            if not incoming_queue:
                return all_moves
            piece_to_play = incoming_queue[0]
            new_held = current_piece
        else:
            piece_to_play = current_held_piece
            new_held = current_piece

        moves_con_hold = self._generate_all_moves(current_board, piece_to_play)
        for move in moves_con_hold:
            move.actions = ["hold"] + move.actions
            move.held_piece = new_held
            all_moves.append(move)

        return all_moves

    def play(self, incoming_queue) -> str:
        if self.current_playing_piece is not None:
            incoming_queue.insert(0, self.current_playing_piece)
            self.current_playing_piece = None  # Nuevo: Resetear después de insertar
        best_move = self.compute(
            incoming_queue,
            max_depth=1,
            current_held_piece=self.hold,
        )

        if not best_move:
            self.queue_outputs.put("^")
            return "^"

        for key in best_move.actions:
            self.queue_outputs.put(key)

        
        if self.hold == "" and "hold" in best_move.actions:
            self.current_playing_piece = incoming_queue[2] if len(incoming_queue) > 2 else None
        else:
            self.current_playing_piece = incoming_queue[1] if len(incoming_queue) > 1 else None

        self.current_board = best_move.board
        self.hold = best_move.held_piece

        while not self.queue_outputs.empty():
            sleep(0.2)

        sleep(0.1)

        return "*"
