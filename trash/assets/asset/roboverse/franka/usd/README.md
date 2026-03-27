The `franka_v1.usd` is directly copied from `omniverse://localhost/NVIDIA/Assets/Isaac/4.2/Isaac/Robots/Franka/franka.usd`.

The `franka_v2.usd` is derived from `omniverse://localhost/NVIDIA/Assets/Isaac/2023.1.0/Isaac/Robots/Franka/franka.usd`. The damping and stiffness of both the arm and the gripper are modified.

`franka_v2.usd` is tuned to be more stable, and is expected to have better performance for tasks that is very delicate. It is tested on `square_d0` task from RoboSuite. The `franka_v1.usd` has ~10% success rate, while `franka_v2.usd` has ~25% success rate.
