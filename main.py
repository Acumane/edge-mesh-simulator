import uuid
from gen.proc import *
from gen.place import *
from sim.signal import *
from sim import rep
from gen.build import build
from typing import *  # type: ignore
from attrs import define, Factory as new
import matplotlib.pyplot as plot
from os import getcwd as cwd, path, mkdir
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from time import time
from rich import print
from sys import stderr
from threading import Thread
from uvicorn import run
from config import WIDTH, DEPTH, TICKS, COMM, MQ_URI, MQ_LOGS
from amqpstorm import Connection, Channel
from amqpstorm import AMQPMessageError
import json

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

progress = {
    "signal": {
    "value": 0.0,
    "step": "Waiting for nodes"
    },
    "build": {
    "value": 0.0,
    "step": "Initializing"
    },
    "lifetime": {
    "tick": 0,
    "end": TICKS
    }
}
mq_key = ""
timer = Timer()
connection: Connection
channel: Channel

def updateProgress(task, value, step=None, log=True):
    global progress
    progress[task]["value"] = value
    if step:
        progress[task]["step"] = step
        if (value <= 1): _sendMessage("*.loading", json.dumps(progress), MQ_LOGS)
        if log: print(f"[bright_yellow][{timer}][/]  {step}")

def main():
    global W, D
    W, D = WIDTH, DEPTH
    rep.TYPE = COMM
    plot.rcParams["toolbar"] = "None"

    updateProgress("build", 0.0, "Generating layout")
    regions = genRegions(W, D, show=False)  # generate warehouse layout

    try:
        updateProgress("build", 0.05, "Placing features")
        kinds: Grid = features(W, D, regions, FREQ)  # place features

        updateProgress("build", 0.1, "Scattering nodes")
        nodes: Grid = rep.genPoints(W, D)  # scatter nodes
        plot.close()

        updateProgress("build", 0.15, "Creating internal representation")
        rep.init(kinds, nodes, show=False)  # create scene rep in global rep.SCENE
        plot.pause(0.1)

        def runBuild():
            out = path.join(cwd(), "vis", "assets")
            if not path.exists(out): mkdir(out)
            build(rep.cloud, out, lambda v, s=None: updateProgress("build", 0.2 + v*0.8, s))

        def runSigStren():
            callback = lambda v, s=None, log=True: updateProgress("signal", v, s, log)
            sigStren(rep.cloud, rep.STATE.instances, callback)

        with ThreadPoolExecutor() as executor:
            executor.submit(runBuild)
            executor.submit(runSigStren)

        lifetime()

    except Exception as e:
        print(f"[bright_red][{timer}]  ERROR: {e}[/]", file=stderr)
    finally:
        plot.close()

def lifetime():
    global progress
    end = progress["lifetime"]["end"]

    for tick in range(end + 1):
        progress["lifetime"]["tick"] = tick

        callback = lambda v, s=None, log=False: updateProgress("signal", 1.1, s, False)
        sigStren(rep.cloud, rep.STATE.instances, callback)
        rep.STATE.tick()
        _sendMessage("*.data", json.dumps(rep.STATE.getStates(rep.STATE.cur)), MQ_LOGS)

        print(f"Tick: {tick}/{end}")

def on_message(message):
    global progress
    try:
        body = json.loads(message.body)
        if (body["type"] == "reload"):
            _sendMessage("*.loading", json.dumps(progress), MQ_LOGS)
            if (progress["build"]["value"] >= 1 and progress["signal"]["value"] >= 1):
                _sendMessage("*.data", json.dumps(rep.STATE.getStates(rep.STATE.cur)), MQ_LOGS)

    except Exception as e:
        print(f"Error processing message: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection
    global channel
    connection = Connection(hostname=MQ_URI, username="guest", password="guest")
    channel = connection.channel()
    channel.exchange.declare(exchange="edge-mesh", exchange_type="topic")
    channel.queue.declare("reload", durable=True)
    channel.queue.bind(exchange="edge-mesh", queue="reload", routing_key="reload")
    channel.basic.consume(on_message, "reload", no_ack=True)
    consumer_thread = Thread(target=channel.start_consuming)
    consumer_thread.start()
    Thread(target=main).start()
    app.STATE = rep.STATE  # type: ignore
    yield
    connection.close()

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:8000",  # frontend
    "http://localhost:8001",  # FastAPI
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# app.STATE.getStates(app.STATE.cur)
def _sendMessage(key, msg, log=False):
    try:
        channel.basic.publish(exchange="edge-mesh", routing_key=key, body=msg)
        if log:
            print(f"{key} sent: {msg}")
    except AMQPMessageError as e:
        print(f"AMQPError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

@app.get("/")
def getRoot():
    return {"message": "Alive"}

if __name__ == "__main__":
    run("__main__:app", host="localhost", port=8001, reload=False, log_level="critical")
