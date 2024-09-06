import numpy as num
import trimesh

KINDS = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}

COL = {"shelf": (0.8039, 0.5216, 0.24706), "pile": (0.62745, 0.32157, 0.17647), "wall": (0.6, 0.6, 0.6)}

vertices, faces, normals, colors = [], [], [], []
def march(cloud, callback):
    faceMap = [
        ([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [-1, 0, 0]), # left
        ([1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]),  # right
        ([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, -1, 0]), # bottom
        ([0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]),  # top
        ([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, -1]), # back
        ([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1])   # front
    ]

    count, total = 0, num.prod(cloud.shape)

    for (x, y, z), pos in num.ndenumerate(cloud):
        if pos:
            for face in faceMap:
                neighbor = x + face[4][0], y + face[4][1], z + face[4][2]  # face[4]: normal to face
                if all(0 <= n < dim for n, dim in zip(neighbor, cloud.shape)) and cloud[neighbor]:
                    continue  # interior face

                v = len(vertices)
                vertices.extend([(x + dx, y + dy, z + dz) for (dx, dy, dz) in face[:4]])
                faces.extend([[v, v + 1, v + 2], [v, v + 2, v + 3]])
                normals.extend([face[4]]*4)
                colors.extend([COL.get(KINDS[pos], (0, 0, 0))]*4)

        count += 1
        if count % 100 == 0:
            progress = count/total
            callback(progress)

    return vertices, faces, normals, colors

def boundingBox(dim):
    X, Y, Z = dim
    vertices = [
        (0, 0, 0), (X, 0, 0), (X, Y, 0), (0, Y, 0),
        (0, 0, Z), (X, 0, Z), (X, Y, Z), (0, Y, Z)
    ]
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 4, 7, 3],
        [1, 5, 6, 2], [0, 1, 5, 4], [3, 2, 6, 7]
    ]
    return trimesh.Trimesh(vertices, faces)

def build(cloud, out, callback):
    callback(0.0, "Marching cubes")
    march(cloud, lambda p: callback(p*0.7))

    callback(0.7, "Creating mesh")
    meshes = {
        "main": trimesh.Trimesh(vertices, faces, vertex_normals=normals, vertex_colors=colors),
        "bounds": boundingBox(cloud.shape)
    }

    scene = trimesh.Scene(meshes) # type: ignore

    scene.export(f"{out}/scene.glb")

    callback(1.0, "Scene exported")
