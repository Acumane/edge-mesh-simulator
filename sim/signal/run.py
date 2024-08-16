import trimesh
from time import time
from attrs import define, Factory as new

from tracer import Tracer
from vis import visualize

SCENE_FILE = "poznan.obj"

@define
class Timer:
    _start: float = new(time)
    def __str__(self):
        return f"{time() - self._start:.4f}s"

def main():
    mesh = trimesh.load_mesh(SCENE_FILE)
    vertices, faces = mesh.vertices, mesh.faces # type: ignore

    tracer = Tracer()
    tracer.load_scene(vertices, faces)

    tx_pos, rx_pos = [0, 15, 0], [-30, 1.5, 45]

    timer = Timer()
    result = tracer.trace(tx_pos, rx_pos)
    print(f"[{timer}] Tracing complete")
    print("Trace result:", result)

    tx_freq = 2.4e9  # 2.4 GHz
    permittivity = 5.3  # Concrete
    losses = tracer.get_total_loss(tx_pos, rx_pos, result, tx_freq, permittivity)
    print(f"[{timer}] Found losses: {losses}")

    visualize(mesh, tx_pos, rx_pos, result) # type: ignore

main()
