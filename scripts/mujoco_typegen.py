import pybind11_stubgen


def main():
    pybind11_stubgen.main(["mujoco", "-o", "./.typing"])
