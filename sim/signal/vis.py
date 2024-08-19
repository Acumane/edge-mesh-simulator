import trimesh

def visualize(mesh: trimesh.Trimesh, a, b, result):
    scene = trimesh.Scene()
    scene.add_geometry(mesh)
    for geometry in scene.geometry.values():
        if hasattr(geometry.visual, "face_colors"):
            geometry.visual.face_colors[:, 3] = 128  # 50% opacity

    tx = trimesh.creation.uv_sphere(radius=0.5)
    tx.visual.face_colors = [0, 255, 0, 255]; tx.apply_translation(a)
    scene.add_geometry(tx)

    rx = trimesh.creation.uv_sphere(radius=0.5)
    rx.visual.face_colors = [0, 255, 0, 255]; rx.apply_translation(b)
    scene.add_geometry(rx)

    for path in result:
        kind, points, _ = path
        color = [255, 255, 0, 255] if kind == 1 else [255, 0, 0, 255]
        
        for i in range(len(points) - 1):
            start, end = points[i], points[i + 1]
            line = trimesh.creation.cylinder(radius=0.1, segment=[start, end])
            line.visual.face_colors = color
            scene.add_geometry(line)

        for point in points[1:-1]: # Small spheres @ intersections
            sphere = trimesh.creation.uv_sphere(radius=0.25)
            sphere.visual.face_colors = color
            sphere.apply_translation(point)
            scene.add_geometry(sphere)

    scene.show()