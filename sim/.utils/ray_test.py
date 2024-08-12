import numpy as np
from typing import Tuple, List
import trimesh
from time import time
from attrs import define, Factory as new

@define
class Timer:
    _start: float = new(time)
    def __str__(self):
        return f"{time() - self._start:.2f}s"

# Essentially Moller-Trumbore algorithm for ray-triangle intersection
def intersect(origin: np.ndarray, angles: np.ndarray, vertices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    output = (len(angles), len(vertices))
    inter_rays, t_rays = np.full(output, False), np.zeros(output)

    v1 = vertices[:, 0]; v2 = vertices[:, 1]; v3 = vertices[:, 2]
    edge1 = v2 - v1; edge2 = v3 - v1
    eps = 0.000001

    for i, ray in enumerate(angles):
        P = np.cross(ray, edge2)
        det = np.sum(edge1 * P, axis=1)
        valid = np.abs(det) > eps
        invalid = np.where(valid, 1.0 / det, 0.0)
        T = origin - v1
        u = np.sum(T * P, axis=1) * invalid
        Q = np.cross(T, edge1)
        v = np.sum(ray * Q, axis=1) * invalid
        t = np.sum(edge2 * Q, axis=1) * invalid

        intersected = (
            valid &
            (u >= 0.0) & (u <= 1.0) &
            (v >= 0.0) & (u + v <= 1.0) &
            (t > eps)
        )

        inter_rays[i, intersected] = True
        t_rays[i, intersected] = t[intersected]

    print("Ray-triangle intersection calculation completed.")
    return inter_rays, t_rays

def raycast(A, B, triangles) -> List[np.ndarray]:
    print(f"Finding intersections between points A {A} and B {B}...")
    origin, direction = A, B - A
    length = np.linalg.norm(direction)
    direction = direction / length
    intersected, tVals = intersect(origin, np.array([direction]), triangles)

    inters = []
    if np.any(intersected):
        valid = (tVals >= 0) & (tVals <= length) & intersected
        for t in tVals[valid].flatten(): inters.append(origin + t * direction)

    return inters

def segment(start, end, radius: float, color: List[int]) -> trimesh.Trimesh:
    line = trimesh.creation.cylinder(radius=radius, segment=[start, end]) # thicker lines
    line.visual.face_colors = color # type: ignore
    return line

def visualize(scene: trimesh.Scene, A, B, inters: List[np.ndarray]):
    for geometry in scene.geometry.values():
        if hasattr(geometry.visual, "face_colors"):
            geometry.visual.face_colors[:, 3] = 128  # 50% opacity

    _A = trimesh.creation.uv_sphere(radius=0.2)
    _A.visual.face_colors = [0, 255, 0, 255]  # type: ignore
    _A.apply_translation(A); scene.add_geometry(_A)

    _B = trimesh.creation.uv_sphere(radius=0.2)
    _B.visual.face_colors = [0, 0, 255, 255]  # type: ignore
    _B.apply_translation(B); scene.add_geometry(_B)

    inters = sorted(inters, key=lambda p: np.linalg.norm(p - A))
    segments = [A, *inters, B]
    for i in range(len(segments) - 1):
        start, end = segments[i], segments[i + 1]
        color = [0, 255, 0, 255] if i % 2 == 0 else [255, 0, 0, 255] # alternate green/red
        scene.add_geometry(segment(start, end, radius=0.1, color=color))

    for point in inters:
        sphere = trimesh.creation.uv_sphere(radius=0.5)
        sphere.visual.face_colors = [255, 255, 0, 255] # type: ignore
        sphere.apply_translation(point); scene.add_geometry(sphere)
    scene.show()

timer = Timer()

scene = trimesh.load("scene.glb")
triangles = np.vstack([mesh.triangles for mesh in scene.geometry.values()]) # type: ignore
A, B = np.array([10, 5, 0]), np.array([180, 120, 10])
print(timer)

inters = raycast(A, B, triangles)
print(timer)

if inters:
    print(f"Found {len(inters)} intersection points:")
    for i, point in enumerate(inters, 1): print(f"Intersection {i}: {point}")

visualize(scene, A, B, inters)
