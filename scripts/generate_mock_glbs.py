import os
import trimesh

os.makedirs("frontend/public/mock_room", exist_ok=True)

def save_normalized_box(filename: str, w: float, h: float, d: float, rgba: list[int]):
    mesh = trimesh.creation.box(extents=[w, h, d])
    # Shift bottom-center to (0, 0, 0)
    mesh.apply_translation([0, h / 2.0, 0])
    mesh.visual.vertex_colors = rgba
    mesh.export(f"frontend/public/mock_room/{filename}")

save_normalized_box("bed.glb", 1.45, 0.55, 2.00, [110, 140, 190, 255])
save_normalized_box("desk.glb", 1.40, 0.75, 0.70, [185, 145, 105, 255])
save_normalized_box("wardrobe.glb", 1.00, 2.00, 0.60, [130, 110, 95, 255])
print("Exported normalized mock .glb files to frontend/public/mock_room/")