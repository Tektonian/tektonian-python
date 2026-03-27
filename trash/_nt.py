import warp as wp
import newton

# Build a model
builder = newton.ModelBuilder()
builder.add_ground_plane()

builder.begin_world()
builder.add_urdf(
    "/Users/kangjeuk/Desktop/wiip/tektonian-python/tt/asset/newton-assets-main/franka_emika_panda/urdf/fr3_franka_hand.urdf"
)  # or add_urdf() / add_usd()
# builder.add_mjcf(
#     "tt/asset/robosuite/assets/robots/panda/robot.xml", xform=(-1.0, 0, 0, 0, 0, 0, 1)
# )  # or add_urdf() / add_usd()
builder.add_mjcf(
    "tt/asset/test/Basket/Basket026/model.xml",
    xform=(0.7, 0, 0, 0, 0, 0, 1),
)
builder.end_world()

builder.begin_world()
builder.add_urdf(
    "/Users/kangjeuk/Desktop/wiip/tektonian-python/tt/asset/newton-assets-main/franka_emika_panda/urdf/fr3_franka_hand.urdf"
)  # or add_urdf() / add_usd()
# builder.add_mjcf(
#     "tt/asset/robosuite/assets/robots/panda/robot.xml", xform=(-1.0, 0, 0, 0, 0, 0, 1)
# )  # or add_urdf() / add_usd()
builder.add_mjcf(
    "tt/asset/test/Basket/Basket026/model.xml", xform=(0.7, 0, 0, 0, 0, 0, 1)
)
builder.end_world()

init_q = [
    -3.6802115e-03,
    2.3901723e-02,
    3.6804110e-03,
    -2.3683236e00,
    -1.2918962e-04,
    2.3922248e00,
    7.8549200e-01,
]
builder.joint_q[:9] = [*init_q, 0.05, 0.05]
builder.joint_target_pos[:9] = [*init_q, 1.0, 1.0]

"""
Newton MUST set this value manually for mjcf -> Think MJCF file parser error
"""
builder.joint_target_ke[:9] = [650.0] * 9
builder.joint_target_kd[:9] = [100.0] * 9
builder.joint_effort_limit[:7] = [80.0] * 7
builder.joint_effort_limit[7:9] = [20.0] * 2
builder.joint_armature[:7] = [0.1] * 7
builder.joint_armature[7:9] = [0.5] * 2

builder.joint_q[9:18] = [*init_q, 0.05, 0.05]
builder.joint_target_pos[9:18] = [*init_q, 1.0, 1.0]
builder.joint_target_ke[9:18] = [650.0] * 9
builder.joint_target_kd[9:18] = [100.0] * 9
builder.joint_effort_limit[9:16] = [80.0] * 7
builder.joint_effort_limit[16:18] = [20.0] * 2
builder.joint_armature[9:16] = [0.1] * 7
builder.joint_armature[16:18] = [0.5] * 2

model = builder.finalize()
# viewer = newton.viewer.ViewerFile("output.json")
viewer = newton.viewer.ViewerGL()
viewer.set_model(model)

# Create a solver and allocate state
solver = newton.solvers.SolverMuJoCo(model)
state_0 = model.state()
state_1 = model.state()
control = model.control()
contacts = model.contacts()
viewer.begin_frame(0)
viewer.log_state(state_0)
viewer.end_frame()

view = newton.selection.ArticulationView(model, pattern="*")
newton.eval_fk(model, model.joint_q, model.joint_qd, state_0)

import numpy

breakpoint()
rng = numpy.random.default_rng()
# Step the simulation
print(model.joint_dof_count)

for step in range(100000):
    # model.joint_q = [random.random()] * 7

    # Set arm position
    # view.set_dof_positions(state_0, [[random.random()] * 7] * 2)

    # model.collide(state_0, contacts)

    if step % 100 == 0:
        joint_target = wp.array(
            rng.uniform(-1.0, 1.0, size=model.joint_dof_count),
            dtype=wp.float32,
        )
        print("input", joint_target)
        wp.copy(control.joint_target_pos, joint_target)

    for _ in range(10):
        state_0.clear_forces()
        solver.step(state_0, state_1, control, contacts, 1.0 / 60.0 / 4.0)
        state_0, state_1 = state_1, state_0

    viewer.begin_frame((1.0 / 60.0 / 4.0) * step)
    viewer.log_state(state_0)
    viewer.end_frame()
