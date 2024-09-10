import trimesh
from math import exp, log10
import numpy as num

from sim.signal.bin import signal
from sim.rep import Signal

SCENE = "vis/assets/scene.glb"

def omniSignal(recv, delays): # multipath
    total = 0
    # Heuristic: (mostly) stop caring if late by 1 symbol
    # BLE: ~1 symbol / 1000ns
    # e^(-a * 1000) = 0.1, so:
    a = 0.0023
    t_first = min(delays)
    for recv, delay in zip(recv, delays):
        mW = 10 ** (recv / 10)
        tardiness = exp(-a * (delay - t_first))
        total += (mW * tardiness)
    return 10*log10(total)

def recvStren(dBm):
    k = 0.2
    # see %.png (~-30 to -90 dBm)
    return 100/(1 + num.exp(-k*(dBm + 70)))

def calcSignal(cA, cB):

    scene, meshes = trimesh.load(SCENE), []
    for _, geometry in scene.geometry.items(): # type: ignore
        if isinstance(geometry, trimesh.Trimesh): meshes.append(geometry)
    mesh = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]  # single mesh

    tracer = signal.Tracer(mesh.vertices, mesh.faces) # type: ignore

    res_ = tracer.trace(cA.pos.asList(), cB.pos.asList())
    # [(<type: int>, <path: [(pos), ... ]>, <refIndex: int>), ...]

    freq = 2.4e9  # 2.4 GHz
    p = 5.31  # permittivity of concrete
    power = 4 # dBm
    bfGain = 6 # dB
    losses_, delays_ = list(zip(*(signal.calcLoss(*r, freq, p) for r in res_)))

    paired = list(zip(res_, losses_, delays_))
    best = sorted(paired, key=lambda x: x[1])[:5]
    res, losses, delays = zip(*best)



    # [(<loss (factor)>, <delay: ns>), ... ]
    recv = [power - loss for loss in losses]
    omni_dBm = omniSignal(recv, delays)
    bf_dBm = power + bfGain - losses[0]

    return (
        cA.name, cB.name, 
        # TODO: when cA.bf != cB.bf
        Signal(perc=recvStren(bf_dBm if cA.bf else omni_dBm), dBm=bf_dBm if cA.bf else omni_dBm)
    )

def sigStren(mesh, callback):
    callback(0.0, "Determining signal strength")
    controllers = list(mesh.values())

    n_edges = len(controllers) * (len(controllers) - 1) // 2
    edge = 0

    connections = []
    for i, cA in enumerate(controllers):
        for cB in controllers[i + 1:]:
            conn = calcSignal(cA, cB)
            if conn: connections.append(conn)
            edge += 1
        progress = edge / n_edges
        callback(progress, "Determining signal strength", log=False)

    for cA_name, cB_name, sig in connections:
        mesh[cA_name].hears[cB_name] = mesh[cB_name].hears[cA_name] = sig

    callback(1.0, "Connections made", log=False)
