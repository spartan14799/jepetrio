import time
import random
import numpy as np
from agent import Agent

def simulate_2_minute_blitz(pps=4.0):
    # PPS = Pieces per second. Un blitz de 2 mins con 4 PPS son ~480 piezas.
    total_time = 120 # segundos
    num_pieces = int(total_time * pps)
    
    agent = Agent()
    board = np.zeros((20, 10), dtype=int)
    pieces_pool = ["I", "J", "L", "O", "S", "T", "Z"]
    
    incoming_queue = [random.choice(pieces_pool) for _ in range(5)]
    current_held_piece = ""
    
    total_score = 0
    total_lines = 0
    tetrises = 0
    b2b = False
    
    print(f"Iniciando simulación Tetr.io Blitz (2 minutos a {pps} PPS = {num_pieces} piezas)...")
    start_time = time.time()
    
    piezas_colocadas = 0
    
    for step in range(num_pieces):
        # Clonamos estado preventivamente
        move = agent.get_best_move(
            incoming_queue, 
            board, 
            max_depth=1, 
            current_held_piece=current_held_piece
        )
        
        if not move:
            print(f"¡Game Over (Topping out) en la pieza {piezas_colocadas}!")
            break
            
        board = move.board
        
        # Lógica de consumo de la cola
        if move.actions and move.actions[0] == "c" and current_held_piece == "":
            incoming_queue = incoming_queue[2:]
            incoming_queue.append(random.choice(pieces_pool))
            incoming_queue.append(random.choice(pieces_pool))
        else:
            incoming_queue = incoming_queue[1:]
            incoming_queue.append(random.choice(pieces_pool))
            
        current_held_piece = move.held_piece
        piezas_colocadas += 1
        
        # Puntuación estilo Tetr.io
        lines = move.cleared_lines
        total_lines += lines
        if lines == 1:
            total_score += 100
            b2b = False
        elif lines == 2:
            total_score += 300
            b2b = False
        elif lines == 3:
            total_score += 500
            b2b = False
        elif lines == 4:
            tetrises += 1
            if b2b:
                total_score += 1200 # B2B Tetris
            else:
                total_score += 800
            b2b = True

        # Penalización o Game Over si bloque superan la línea límite superior (altura 20)
        # El juego maneja el desborde (por limitación de board_y_valids), pero si el centro se llena:
        if np.any(board[0, 3:7] == 1):
             print(f"¡Alerta de Game Over por tope en la pieza {piezas_colocadas}!")
             break

    exec_time = time.time() - start_time
    with open("score_result.txt", "w", encoding="utf-8") as f:
        f.write("-" * 40 + "\n")
        f.write(f"RESULTADOS DE LA PRUEBA TECNICA (Score Attack)\n")
        f.write("-" * 40 + "\n")
        f.write(f"Piezas jugadas: {piezas_colocadas} / {num_pieces}\n")
        f.write(f"Lineas limpiadas: {total_lines}\n")
        f.write(f"Tetrises conseguidos: {tetrises}\n")
        f.write(f"PUNTUACION TOTAL ESTIMADA: {total_score:,} pts\n")
        f.write(f"Tiempo real de computo: {exec_time:.2f} segundos\n")
        
        if piezas_colocadas < num_pieces:
            f.write("\n[FAIL] EL AGENTE HA PERDIDO (Se lleno la pantalla antes de los 2 mins).\n")
            f.write("Requiere un ajuste en los pesos de 'wells', 'holes' o 'bumpiness'.\n")
        else:
            f.write("\n[SUCCESS] EL AGENTE COMPLETO LOS 2 MINS SATISFACTORIAMENTE.\n")

if __name__ == "__main__":
    simulate_2_minute_blitz()
