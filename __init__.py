import agent
import environment
import keyboard
from time import sleep


if __name__ == "__main__":
    game_started = False
    game_finished = False
    print("Presione 'P' para empezar el juego")
    e = environment.Environment()
    a = agent.Agent()
    while not game_started:
        if keyboard.is_pressed("p"):
            game_started = True
            # r es un array/captura de pantalla
            r = e.response("*")
            print("Empieza el juego")
        sleep(0.1)
    while True:
        print(a.percept(r))
        r = e.response("*")
        sleep(0.1)
    # while r is not False:
    #     # INFO: a.percept(r) es una lista de nuevos bloques (Antes llamada next_blocks)
    #     v = a.play(a.percept(r))
    #     r = e.response(v)
