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
    keyboard.add_hotkey("p", start_agent)

    while not agent_started:
        sleep(0.1)

    r: typing.NDArray[uint8] | None = None

    while not game_started:
        r: typing.NDArray[uint8] | None = e.response("*")
        if r is not None and e.game_countdown(r):
            game_started = True
    # Cuenta de 3 segundos
    sleep(1)
    r = e.response("*")
    first_queue = a.percept(r)
    sleep(2)
    v = a.play(first_queue)

    while not game_finished:
        r = e.response("*")
        incoming_queue = a.percept(r)
        if incoming_queue:
            v = a.play(incoming_queue)
            if v == "^":
                game_finished = True

        sleep(0.1)
