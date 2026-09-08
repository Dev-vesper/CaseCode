import json

from direct.showbase.ShowBase import ShowBase

from src.core.controller.camera import CameraController
from src.core.controller.player import Player
from src.core.world.loader import WorldLoader
from src.ui.windows import StartWindow

if __name__ == '__main__':
    base = ShowBase()

    with open('assets/worlds/test_map.json') as file:
        blocks = json.load(file)
    world = WorldLoader(blocks)
    world.load()

    base.world = world
    base.camera_controller = CameraController(focus=world.center)
    base.player = Player(world)
    base.start_menu = StartWindow()

    base.run()
