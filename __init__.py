import agent
import environment
import keyboard
from numpy import typing, uint8
from time import sleep

agent_started = False
game_started = False
game_finished = False

def start_agent():
    global agent_started
    agent_started = True
    print("Se inició el agente y el ambiente")

if __name__ == "__main__":
    print("Presione 'p' para empezar el juego")
    e = environment.Environment()
    a = agent.Agent()
    keyboard.add_hotkey('p', start_agent)

    while not agent_started:
        sleep(0.1)

    r: typing.NDArray[uint8] | None = None

    while not game_started:
        r: typing.NDArray[uint8] | None = e.response("*")
        if r is not None and e.game_countdown(r):
            game_started = True
    # Cuenta de 3 segundos
    r = e.response("*")
    sleep(3)
    while not game_finished:
        v = a.play(a.percept(r))
        r = e.response(v)
        sleep(0.1)
        # TODO: revisar cuando el juego terminó, devolver puntuación