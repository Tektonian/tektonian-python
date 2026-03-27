import trimesh
import os
import shutil

def convert_stl_to_obj(stl_path, obj_path):
    mesh = trimesh.load_mesh(stl_path)
    mesh.export(obj_path)

if __name__ == "__main__":
    dir = "/home/fs/yizhuo/RoboVerse/roboverse_data/robots/franka_shadow_hand/mjcf/meshes"

    for obj_file in os.listdir(dir):
        if obj_file.endswith(".stl"):
            stl_path = os.path.join(dir, obj_file)
            obj_path = os.path.join(dir, obj_file.replace(".stl", ".obj"))
            if os.path.exists(obj_path):
                continue
            convert_stl_to_obj(stl_path, obj_path)
