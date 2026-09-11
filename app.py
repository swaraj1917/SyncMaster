# app.py — Flask web server for SyncMaster
# Place this file in the SyncMaster project root, next to main.py and gui.py.
import os
import sys
import threading
import time
from io import StringIO

from flask import Flask, jsonify, request, render_template

from problems import producer_consumer, dining_philosopher, reader_writer
from utils.control import SimulationControl

app = Flask(__name__)

STATE = {
    "producer_consumer": {"thread": None, "output": StringIO(), "running": False},
    "dining_philosopher": {"thread": None, "output": StringIO(), "running": False},
    "reader_writer": {"thread": None, "output": StringIO(), "running": False},
}
LOCK = threading.Lock()
STDOUT_LOCK = threading.Lock()  # only one simulation may hold sys.stdout at a time


def _run(problem, target_fn, args):
    buf = STATE[problem]["output"]
    with STDOUT_LOCK:
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            target_fn(*args)
        finally:
            sys.stdout = old_stdout
    with LOCK:
        STATE[problem]["running"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start/<problem>", methods=["POST"])
def start(problem):
    if problem not in STATE:
        return jsonify(error="unknown problem"), 404

    with LOCK:
        if any(s["running"] for s in STATE.values()):
            return jsonify(error="another simulation is already running"), 409

        data = request.get_json(force=True) or {}
        SimulationControl.init()
        STATE[problem]["output"] = StringIO()
        STATE[problem]["running"] = True

        if problem == "producer_consumer":
            args = (
                int(data.get("buffer_size", 5)),
                int(data.get("num_producers", 2)),
                int(data.get("num_consumers", 2)),
                int(data.get("items_per_producer", 5)),
            )
            fn = producer_consumer.run_simulation
        elif problem == "dining_philosopher":
            n = int(data.get("num_philosophers", 5))
            c = int(data.get("eat_count", 3))
            naive = bool(data.get("naive", False))
            args = (n, c)
            fn = lambda nn, cc: dining_philosopher.run_simulation(nn, cc, naive=naive)
        else:  # reader_writer
            args = (
                int(data.get("num_readers", 3)),
                int(data.get("num_writers", 2)),
                int(data.get("read_times", 3)),
                int(data.get("write_times", 2)),
            )
            fn = reader_writer.run_simulation

        t = threading.Thread(target=_run, args=(problem, fn, args), daemon=True)
        STATE[problem]["thread"] = t
        t.start()

    return jsonify(ok=True)


@app.route("/api/output/<problem>")
def output(problem):
    if problem not in STATE:
        return jsonify(error="unknown problem"), 404
    with LOCK:
        text = STATE[problem]["output"].getvalue()
        running = STATE[problem]["running"]
    return jsonify(output=text, running=running)


@app.route("/api/control/<action>", methods=["POST"])
def control(action):
    if action == "pause":
        SimulationControl.pause()
    elif action == "resume":
        SimulationControl.resume()
    elif action == "stop":
        SimulationControl.stop()
    else:
        return jsonify(error="unknown action"), 400
    return jsonify(ok=True)


@app.route("/api/shutdown", methods=["POST"])
def shutdown():
    def stop():
        time.sleep(0.3)  # give Flask a moment to send the response first
        os._exit(0)
    threading.Thread(target=stop, daemon=True).start()
    return jsonify(ok=True, message="Server shutting down")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)