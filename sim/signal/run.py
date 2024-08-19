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

    tracer = Tracer(mesh.vertices, mesh.faces) # type: ignore

    # a, b = [130, 100, 4], [110, 120, 2]
    a, b = [120, 65, 4], [110, 120, 2]



    timer = Timer()
    raw, result = tracer.trace(a, b)
    print(f"[{timer}] Tracing complete")
    print("Trace result:", raw)
    print("Processed result:", result)


    freq = 2.4e9  # 2.4 GHz
    permittivity = 5.3  # Concrete
    losses = tracer.getLoss(a, b, result, freq, permittivity)
    print(f"[{timer}] Found losses: {losses}")

    visualize(mesh, a, b, result) # type: ignore

main()