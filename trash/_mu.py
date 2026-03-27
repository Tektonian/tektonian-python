import random
import time

from enum import IntEnum
import mujoco
import mujoco.viewer


# region https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general
class DynTypeEnum(IntEnum):
    NONE = 0
    INTEGRATOR = 1
    FILTER = 2
    FILTEREXACT = 3
    MUSCLE = 4
    USER = 5


class GainTypeEnum(IntEnum):
    FIXED = 0
    AFFINE = 1
    MUSCLE = 2
    USER = 3


class BiasTypeEnum(IntEnum):
    NONE = 0
    AFFINE = 1
    MUSCLE = 2
    USER = 3


# end-region


# https://github.com/lvjonok/mujoco-actuators-types/blob/master/demo.ipynb


class ActuatorMotor:
    # https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor
    def __init__(self) -> None:
        self.dyn = [1, 0, 0]
        self.gain = [1, 0, 0]
        self.bias = [0, 0, 0]

        self.dyn_type = [DynTypeEnum.NONE.value]
        self.gain_type = [GainTypeEnum.FIXED.value]
        self.bias_type = [BiasTypeEnum.NONE.value]

    def __repr__(self) -> str:
        return f"ActuatorMotor(dyn={self.dyn}, gain={self.gain}, bias={self.bias})"


class ActuatorPosition(ActuatorMotor):
    # https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position
    def __init__(self, kp=1, kd=0) -> None:
        super().__init__()
        self.kp = kp
        self.kd = kd
        self.gain[0] = self.kp
        self.bias[1] = -self.kp
        self.bias[2] = -self.kd

        self.dyn_type = [DynTypeEnum.NONE.value]
        self.gain_type = [GainTypeEnum.FIXED.value]
        self.bias_type = [BiasTypeEnum.AFFINE.value]


class ActuatorVelocity(ActuatorMotor):
    # https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity
    def __init__(self, kv=1) -> None:
        super().__init__()
        self.kv = kv
        self.gain[0] = self.kv
        self.bias[2] = -self.kv

        self.dyn_type = [DynTypeEnum.NONE.value]
        self.gain_type = [GainTypeEnum.FIXED.value]
        self.bias_type = [BiasTypeEnum.AFFINE.value]


def update_actuator(model: mujoco.MjModel, actuator_id, actuator: ActuatorMotor):
    """
    Update actuator in model
    model - mujoco.MjModel
    actuator_id - int or str (name) (for reference see, named access to model elements)
    actuator - ActuatorMotor, ActuatorPosition, ActuatorVelocity
    """
    model.actuator(actuator_id).dynprm[:3] = actuator.dyn
    model.actuator(actuator_id).gainprm[:3] = actuator.gain
    model.actuator(actuator_id).biasprm[:3] = actuator.bias

    model.actuator(actuator_id).dyntype = actuator.dyn_type
    model.actuator(actuator_id).gaintype = actuator.gain_type
    model.actuator(actuator_id).biastype = actuator.bias_type


scene_xml = """
<mujoco model="panda scene">
  <statistic center="0.3 0 0.4" extent="1"/>

  <option timestep="0.005" iterations="5" ls_iterations="8" integrator="implicitfast">
    <flag eulerdamp="disable"/>
  </option>

  <custom>
    <numeric data="12" name="max_contact_points"/>
  </custom>

  <visual>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
    <rgba haze="0.15 0.25 0.35 1"/>
    <global azimuth="120" elevation="-20"/>
    <scale contactwidth="0.075" contactheight="0.025" forcewidth="0.05" com="0.05" framewidth="0.01" framelength="0.2"/>
  </visual>

  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
    <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
      markrgb="0.8 0.8 0.8" width="300" height="300"/>
    <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
  </asset>

  <worldbody>
    <light pos="0 0 1.5" dir="0 0 -1" directional="true"/>
    <geom name="floor" size="0 0 0.05" type="plane" material="groundplane" contype="1"/>
  </worldbody>
</mujoco>
"""
# # Create the parent spec.
# parent = mujoco.MjSpec.from_string(scene_xml)


# # Create the child spec.
# child = mujoco.MjSpec.from_file("tt/asset/roboverse/franka/mjcf/panda.xml")

# Create the parent spec.
parent = mujoco.MjSpec.from_string(scene_xml)
body = parent.worldbody.add_body()
frame = parent.worldbody.add_frame()
# site = parent.worldbody.add_site()

# Create the child spec.
child = mujoco.MjSpec.from_file("tt/asset/roboverse/franka/mjcf/panda.xml")
child2 = mujoco.MjSpec.from_file("tt/asset/roboverse/franka/mjcf/panda.xml")
child_body = child.worldbody.add_body()
child_frame = child.worldbody.add_frame()

basket = mujoco.MjSpec.from_file("tt/asset/test/Basket/Basket026/model.xml")
print(basket.pair)


# # Attach the child to the parent in different ways.
# body_in_frame = frame.attach_body(child_body, "child-", "")
# frame_in_body = body.attach_frame(child_frame, "child-", "")
# worldframe_in_site = parent.attach(child, site=site, prefix="child-")
# worldframe_in_frame = parent.attach(child, frame=frame, prefix="child-")
basket.bodies[1].pos = [1, 0, 0]
child.bodies[1].pos = [0.5, 0, 0]
child2.bodies[1].pos = [-0.5, 0, 0]
print(child.bodies)
bodies: list[mujoco.MjsBody] = child.bodies
for body in bodies:
    print(body, body.parent, body.parent == child.worldbody)
parent.attach(child, frame=frame)
parent.attach(child2, frame=frame, prefix="arm2")
parent.attach(basket, frame=frame)

print(parent.to_xml())
m: mujoco.MjModel = parent.compile()
d = mujoco.MjData(m)

# update actuators
# torque_motor = ActuatorPosition(kp=200, kd=100)
# vel_motor = ActuatorVelocity(kv=200)

# for actuator_id in range(m.nu):
#     update_actuator(m, actuator_id, vel_motor)

d.ctrl = [random.random() * ((-1) ** i) for i in range(m.nq)]


s = 0
with mujoco.viewer.launch_passive(m, d) as viewer:
    # Close the viewer automatically after 30 wall-seconds.
    start = time.time()
    while viewer.is_running() and time.time() - start < 10000:
        step_start = time.time()

        # mj_step can be replaced with code that also evaluates
        # a policy and applies a control signal before stepping the physics.
        # if s % 200 == 0:
        #     d.ctrl = [random.random() * ((-1) ** i) for i in range(m.nq)]

        s += 1
        mujoco.mj_step(m, d)
        # Example modification of a viewer option: toggle contact points every two seconds.
        with viewer.lock():
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

        # Pick up changes to the physics state, apply perturbations, update options from GUI.
        viewer.sync()

        # Rudimentary time keeping, will drift relative to wall clock.
        time_until_next_step = m.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
