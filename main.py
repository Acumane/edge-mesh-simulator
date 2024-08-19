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
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from rich import print
from sys import stderr
from threading import Thread
from uvicorn import run
import toml

config = toml.load("config.toml")

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

progress = {
    "signal": {"value": 0.0, "step": "Waiting for nodes"},
    "build":  {"value": 0.0, "step": "Initializing"},
    "lifetime": {"tick": 0, "end": config.get("ticks", 50)}
}
timer = Timer()

def updateProgress(task, value, step=None, log=True):
    global progress
    progress[task]["value"] = value
    if step:
        progress[task]["step"] = step
        if log: print(f"[bright_yellow][{timer}][/]  {step}")

def main(args):
    global W, D
    W, D = args.get("width", 150), args.get("depth", 200)
    rep.TYPE = args.get("comm", "BLE")
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
            futures = executor.submit(runBuild), executor.submit(runSigStren)
            for future in as_completed(futures):
                try: future.result()
                except Exception: raise

        # lifetime()

    except Exception as e:
        print(f"[bright_red][{timer}]  ERROR:[/] {e}", file=stderr)
    finally:
        plot.close()

def lifetime():
    global progress
    end = progress["lifetime"]["end"]

    for tick in range(end + 1):
        progress["lifetime"]["tick"] = tick

        callback = lambda v, s=None, log=False: updateProgress("signal", 1, s, False)
        sigStren(rep.cloud, rep.STATE.instances, callback)
        rep.STATE.tick()

        print(f"Tick: {tick}/{end}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(target=main, args=[config]).start()
    app.STATE = rep.STATE  # type: ignore
    yield

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

@app.get("/progress")
async def getProgress():
    global progress; return progress

@app.get("/")
def getRoot():
    return {"message": "Alive"}

@app.get("/controllers")
async def controllers():
    return app.STATE.getStates(app.STATE.cur)  # type: ignore

if __name__ == "__main__":
    run("__main__:app", host="localhost", port=8001, reload=False, log_level="critical")
