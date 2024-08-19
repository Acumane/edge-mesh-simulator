import trimesh
from time import time
from attrs import define, Factory as new

from bin import signal
from vis import visualize

SCENE = "scene.glb"

@define
class Timer:
    _start: float = new(time)
    def __str__(self):
        return f"{time() - self._start:.4f}s"

def main():
    scene, meshes = trimesh.load(SCENE), []
    for _, geometry in scene.geometry.items(): # type: ignore
        if isinstance(geometry, trimesh.Trimesh): meshes.append(geometry)
    mesh = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]  # single mesh

    tracer = signal.Tracer(mesh.vertices, mesh.faces) # type: ignore

    a, b = [130, 70, 4], [110, 120, 2]
    # a, b = [120, 65, 4], [110, 120, 2]

    timer = Timer()
    results = tracer.trace(a, b)
    print(f"[{timer}] Tracing complete")
    print("Results:", results)

    freq = 2.4e9  # 2.4 GHz
    p = 5.31  # permittivity of concrete
    losses = [signal.calcLoss(rec, path, freq, p, ref) for rec, path, ref in results]
    print(f"[{timer}] Found losses: {losses}")

    visualize(mesh, a, b, results) # type: ignore

main()
