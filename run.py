import json

from panda3d.core import loadPrcFileData

from configs.engine import settings as engine_settings
from direct.showbase.ShowBase import ShowBase

from src.core.controller.camera import CameraController
from src.core.controller.menu import Menu
from src.core.world.loader import WorldLoader

if __name__ == '__main__':
    if engine_settings.FULLSCREEN:
        loadPrcFileData('', 'fullscreen true')
        size = engine_settings.screen_size()
        if size:
            loadPrcFileData('', f'win-size {size[0]} {size[1]}')
    base = ShowBase()

    with open('assets/worlds/test_map.json') as file:
        blocks = json.load(file)
    world = WorldLoader(blocks)
    world.load()

    base.world = world
    base.camera_controller = CameraController(focus=world.center)
    base.menu = Menu()

    base.run()
