import trimesh
from typing import List

def visualize(mesh: trimesh.Trimesh, tx_pos, rx_pos, paths: List):
    scene = trimesh.Scene()
    scene.add_geometry(mesh)
    for geometry in scene.geometry.values():
        if hasattr(geometry.visual, "face_colors"):
            geometry.visual.face_colors[:, 3] = 128  # 50% opacity


    tx = trimesh.creation.uv_sphere(radius=0.5)
    tx.visual.face_colors = [0, 255, 0, 255]; tx.apply_translation(tx_pos)
    scene.add_geometry(tx)

    rx = trimesh.creation.uv_sphere(radius=0.5)
    rx.visual.face_colors = [0, 255, 0, 255]; rx.apply_translation(rx_pos)
    scene.add_geometry(rx)

    for path in paths:
        kind, *points = path
        match kind:
            case 1:  # Direct
                points, color = [tx_pos, rx_pos], [255, 255, 0, 255]
            case 2:  # Diffracted
                points, color = [tx_pos] + points[0] + [rx_pos], [255, 165, 0, 255]
            case 3:  # Reflected
                points, color = [tx_pos, points[0], rx_pos], [255, 0, 0, 255]
            case _: continue

        for i in range(len(points) - 1):  # Line segments
            start, end = points[i], points[i + 1]
            line = trimesh.creation.cylinder(radius=0.1, segment=[start, end])
            line.visual.face_colors = color # type: ignore
            scene.add_geometry(line)

        for point in points[1:-1]:  # Small spheres @ intersections
            sphere = trimesh.creation.uv_sphere(radius=0.25)
            sphere.visual.face_colors = color # type: ignore
            sphere.apply_translation(point)
            scene.add_geometry(sphere)

    scene.show()
