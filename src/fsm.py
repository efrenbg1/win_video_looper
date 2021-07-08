import threading
import time
import queue

_state = "pause"
_lstate = threading.Lock()

_states = ["play", "pause", "casting"]

_q = queue.Queue(maxsize=1)


def set(state, timeout=0):
    global _states, _q
    if state not in _states:
        raise ValueError("Invalid state. State argument must be one of the following: ", _states)
    with _q.mutex:
        _q.queue.clear()
    try:
        _q.put([state, timeout], block=False)
    except Exception as e:
        print(e)
        pass


def get():
    global _state, _lstate
    with _lstate:
        return _state


def run():
    global _state, _lstate, _q
    while True:
        state = _q.get()
        if not isinstance(state, list):
            continue
        if len(state) != 2:
            continue
        if state[0] not in _states:
            continue
        if not isinstance(state[1], int):
            continue
        time.sleep(state[1])
        if not _q.empty():
            continue
        with _lstate:
            _state = state[0]


def start():
    daemon = threading.Thread(target=run, daemon=True)
    daemon.setDaemon(True)
    daemon.start()
