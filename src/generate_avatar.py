import trimesh
import numpy as np

print("Generating 3D AI Avatar...")
head = trimesh.creation.box(extents=[1.2, 1.2, 1.2])
head.visual.face_colors = [56, 189, 248, 255]

body = trimesh.creation.box(extents=[1.5, 0.8, 1.8])
body.apply_translation([0, 0, -1.5])
body.visual.face_colors = [30, 41, 59, 255]

avatar = trimesh.util.concatenate([head, body])
avatar.export('avatar.glb')
print("Success! avatar.glb created.")