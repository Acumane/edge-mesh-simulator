from cascade import cascade
from dataclasses import asdict
from .signal import MAX_STREN
import random
import json

GRAPH: cascade.Cascade = cascade.Cascade()

def makeGraph(mesh, tick):
    if tick == 0: buildGraph(mesh)
    else: updateGraph(mesh)

def buildGraph(mesh):
    for controller in mesh:
        GRAPH.graph.addVert(controller["name"])
        for target, weight in controller["hears"].items():
            GRAPH.graph.addEdge(controller["name"], target, MAX_STREN + 1 - weight)
    root = random.choice(mesh)["name"]
    GRAPH.dijkstra(root)
    # GRAPH.plot()

def updateGraph(updates):
    # have function that converts mesh into update operations
    # and then executes them and then calls cascade
    return

def infoGraph():
    return {"pred": json.dumps({k: asdict(v) for k, v in GRAPH.pred.items()}), "cache": json.dumps(GRAPH.cache)}
