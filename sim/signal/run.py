import trimesh
from time import time
from attrs import define, Factory as new
from math import exp, log10

from bin import signal
from vis import visualize

SCENE = "scene.glb"

@define
class Timer:
    ms: bool = False
    _start: float = new(time)

    def __str__(self):
        elapsed = time() - self._start
        if self.ms: return f"{elapsed * 1000:.2f}ms"
        return f"{elapsed:.4f}s"

def multipathSignal(recv, delays): # omni
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

def main():
    timer = Timer()
    scene, meshes = trimesh.load(SCENE), []
    print(f"[{timer}] Loaded scene")
    for _, geometry in scene.geometry.items(): # type: ignore
        if isinstance(geometry, trimesh.Trimesh): meshes.append(geometry)
    mesh = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]  # single mesh
    print(f"[{timer}] Processed scene")

    tracer = signal.Tracer(mesh.vertices, mesh.faces) # type: ignore
    print(f"[{timer}] Initialized tracer")

    # a, b = [130, 120, 2], [110, 120, 2]
    a, b = [130, 70, 4], [110, 120, 2]
    # a, b = [130, 95, 4], [110, 120, 2]
    # a, b = [115, 35, 4], [110, 120, 2]

    traceTime = Timer(ms=True)
    res_ = tracer.trace(a, b)

    print(f"[{timer}] Tracing complete in {traceTime}")
    # [(<type: int>, <path: [(pos), ... ]>, <refIndex: int>), ...]

    freq = 2.4e9  # 2.4 GHz
    p = 5.31  # permittivity of concrete
    power = 4 # dBm
    bfGain = 6 # dB
    minRecv = -90 # dBm
    losses_, delays_ = list(zip(*(signal.calcLoss(*r, freq, p) for r in res_)))

    paired = list(zip(res_, losses_, delays_))
    best = sorted(paired, key=lambda x: x[1])[:5]
    res, losses, delays = zip(*best)

    # [(<loss (factor)>, <delay: ns>), ... ]
    print(f"[{timer}] Losses (dB): {losses}")
    print(f"\t  Light delay (ns): {delays}")

    recv = [power - loss for loss in losses]
    print(f"\t  Received power (dBm): {recv}\n")

    print(f"\t  As multipath (dBm): {multipathSignal(recv, delays)}")
    print(f"\t     beamformed: {power + bfGain - losses[0]}")

    # visualize(mesh, a, b, res) # type: ignore

main()
