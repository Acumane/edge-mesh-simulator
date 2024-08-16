import trimesh
from time import time
from attrs import define, Factory as new

from tracer import Tracer
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

    vertices, faces = mesh.vertices, mesh.faces # type: ignore

    tracer = Tracer()
    tracer.load(vertices, faces)

    a, b = [100, 60, 5], [0, 10, 20]

    timer = Timer()
    result = tracer.trace(a, b)
    print(f"[{timer}] Tracing complete")
    print("Trace result:", result)

    freq = 2.4e9  # 2.4 GHz
    permittivity = 5.3  # Concrete
    losses = tracer.getLoss(a, b, result, freq, permittivity)
    print(f"[{timer}] Found losses: {losses}")

    visualize(mesh, a, b, result) # type: ignore

main()