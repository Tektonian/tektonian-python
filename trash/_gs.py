import genesis as gs


gs.init(backend=gs.cpu)

scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        res=(1280, 960),
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
        max_FPS=60,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,  # visualize the coordinate frame of `world` at its origin
        world_frame_size=1.0,  # length of the world frame in meter
        show_link_frame=False,  # do not visualize coordinate frames of entity links
        show_cameras=False,  # do not visualize mesh and frustum of the cameras added
        plane_reflection=True,  # turn on plane reflection
        ambient_light=(0.1, 0.1, 0.1),  # ambient light setting
    ),
    renderer=gs.renderers.Rasterizer(),  # using rasterizer for camera rendering
)

cam = scene.add_camera(
    res=(1280, 960), pos=(3.5, 0.0, 2.5), lookat=(0, 0, 0.5), fov=30, GUI=False
)
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(
        file="tt/asset/robosuite/assets/robots/panda/robot.xml", pos=(1, 0, 0)
    ),
)

franka2 = scene.add_entity(
    gs.morphs.MJCF(
        file="tt/asset/robosuite/assets/robots/panda/robot.xml", pos=(-1, 0, 0)
    ),
)

basket = scene.add_entity(
    gs.morphs.MJCF(file="tt/asset/test/Basket/Basket026/model.xml", pos=(-0.5, 0, 0)),
)

scene.build()

while True:
    scene.step()

    cam.render()
