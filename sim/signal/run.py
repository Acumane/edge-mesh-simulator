import trimesh
from time import time
from attrs import define, Factory as new

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

    a, b = [130, 70, 4], [110, 120, 2]
    # a, b = [120, 65, 4], [110, 120, 2]

    traceTime = Timer(ms=True)
    results = tracer.trace(a, b)

    print(f"[{timer}] Tracing complete in {traceTime}")
    # [(<type: int>, <path: [(pos), ... ]>, <refIndex: int>), ...]
    # print("Results:", results)

    freq = 2.4e9  # 2.4 GHz
    p = 5.31  # permittivity of concrete
    power = 4 # dBm
    minRecv = -90 # dBm
    losses, delays = zip(*(signal.calcLoss(*r, freq, p) for r in results))

    # [(<loss (factor)>, <delay: ns>), ... ]
    print(f"[{timer}] Losses (dB): {losses}")
    print(f"\t  Light delay (ns): {delays}")

    recv = [power - loss for loss in losses]
    print(f"\t  Received power (dBm): {recv}")
    ratios = [10**(db/10) for db in recv]

    floor, ceil = 10**(minRecv/10), max(ratios)
    scores = [(r - floor) / (ceil - floor) * 100 for r in ratios]
    print(f"\t  Signal scores [0-100]: {scores}")

    visualize(mesh, a, b, results) # type: ignore

main()
