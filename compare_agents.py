import time
import random
import numpy as np

from Originalagent import Agent as OriginalAgent
from agent import Agent as OptimizedAgent

def compare_agents(num_pieces=15):
    result_str = "====================================\n"
    result_str += "COMPARACION: ORIGINAL VS OPTIMIZADO\n"
    result_str += "====================================\n\n"

    pieces_pool = ["I", "J", "L", "O", "S", "T", "Z"]

    agents = [
        ("Agente Original (ProcessPool / depth=2 / sin penalizar altura)", OriginalAgent(), True),
        ("Agente Optimizado (SingleThread / depth=1 / pesos Dellacherie)", OptimizedAgent(), False)
    ]

    for name, agent_instance, is_original in agents:
        board = np.zeros((20, 10), dtype=int)
        incoming_queue = [random.choice(pieces_pool) for _ in range(5)]
        current_held_piece = ""
        
        result_str += f"-> Evaluando: {name} (Prueba de {num_pieces} piezas)\n"
        print(f"Calculando {name}...")
        start_time = time.time()
        
        piezas_jugadas = 0
        total_score = 0
        for step in range(num_pieces):
            if is_original:
                move = agent_instance.compute(
                    incoming_queue, 
                    board, 
                    max_depth=2, 
                    current_held_piece=current_held_piece
                )
            else:
                move = agent_instance.get_best_move(
                    incoming_queue, 
                    board, 
                    max_depth=1, 
                    current_held_piece=current_held_piece
                )
            
            if not move:
                result_str += "   [!] GAME OVER (Top Out)\n"
                break
                
            board = move.board
            if move.actions and move.actions[0] == "c" and current_held_piece == "":
                incoming_queue = incoming_queue[2:]
            else:
                incoming_queue = incoming_queue[1:]
                
            incoming_queue.append(random.choice(pieces_pool))
            current_held_piece = move.held_piece
            piezas_jugadas += 1
            total_score += move.cleared_lines
            
        exec_time = time.time() - start_time
        pps = piezas_jugadas / exec_time if exec_time > 0 else 0
        
        result_str += f"   > Tiempo de proceso : {exec_time:.2f} segundos\n"
        result_str += f"   > Velocidad         : {pps:.2f} PPS (Piezas por segundo)\n"
        result_str += f"   > Lineas resueltas  : {total_score}\n\n"

    print(result_str)
    with open("compare_result.txt", "w", encoding="utf-8") as f:
        f.write(result_str)

if __name__ == "__main__":
    compare_agents()
