import time
import numpy as np
import concurrent.futures
from agent import Agent

def compute_threads(self, incoming_queue, current_board, max_depth=3, current_held_piece=""):
    best_score = float("-inf")
    best_move = None

    if not incoming_queue:
        return None

    current_piece = incoming_queue[0]

    possible_moves = self._generate_moves_with_hold(
        current_board, current_piece, incoming_queue[1:], current_held_piece
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for move in possible_moves:
            future = executor.submit(
                self._evaluate_single_branch,
                move, incoming_queue, max_depth, current_held_piece
            )
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            evaluated_move = future.result()

            if evaluated_move.score > best_score:
                best_score = evaluated_move.score
                best_move = evaluated_move

    return best_move

def test_multithread_blitz():
    agent = Agent()
    agent.queue_perceptions = None
    agent.queue_actions = None
    
    current_board = np.zeros((20, 10), dtype=int)
    incoming_queue = ["T", "J", "O", "I", "S"]
    current_held_piece = ""

    print("=== RENDIMIENTO BLITZ (max_depth=1) ===")
    
    # 1. Single Thread
    start_time_single = time.time()
    best_move_single = agent.get_best_move(incoming_queue, current_board, 1, current_held_piece)
    end_time_single = time.time()
    print(f"[1] Un Solo Hilo (Single Thread): {end_time_single - start_time_single:.4f} segundos")

    # 2. ThreadPoolExecutor
    agent.compute_threads = compute_threads.__get__(agent, Agent)
    start_time_th = time.time()
    best_move_th = agent.compute_threads(incoming_queue, current_board, 1, current_held_piece)
    end_time_th = time.time()
    print(f"[2] Multithread (ThreadPoolExecutor): {end_time_th - start_time_th:.4f} segundos")

    print("\n=== RENDIMIENTO PROFUNDO (max_depth=2) ===")
    
    # 3. Single Thread
    start_time_single_2 = time.time()
    best_move_single_2 = agent.get_best_move(incoming_queue, current_board, 2, current_held_piece)
    end_time_single_2 = time.time()
    print(f"[1] Un Solo Hilo (Single Thread): {end_time_single_2 - start_time_single_2:.4f} segundos")

    # 4. ThreadPoolExecutor
    start_time_th_2 = time.time()
    best_move_th_2 = agent.compute_threads(incoming_queue, current_board, 2, current_held_piece)
    end_time_th_2 = time.time()
    print(f"[2] Multithread (ThreadPoolExecutor): {end_time_th_2 - start_time_th_2:.4f} segundos")

if __name__ == "__main__":
    test_multithread_blitz()
