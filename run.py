import json

from direct.showbase.ShowBase import ShowBase

from src.core.controller.camera import CameraController
from src.core.controller.player import Player
from src.core.world.loader import WorldLoader
from src.ui.buttons import make_round_button
from src.ui.windows import SideMenu, StartWindow

if __name__ == '__main__':
    base = ShowBase()

    with open('assets/worlds/test_map.json') as file:
        blocks = json.load(file)
    world = WorldLoader(blocks)
    world.load()

    base.world = world
    base.camera_controller = CameraController(focus=world.center)

    def start_game():
        base.player = Player(base.world)
        base.start_menu.hide()
        base.side_menu = SideMenu()
        base.hud_buttons = [
            make_round_button(base.a2dLeftCenter, (0.11, 0, 0.78),
                              icon='hamburger', command=base.side_menu.toggle),
            make_round_button(base.a2dLeftCenter, (0.11, 0, 0.56), icon='plus'),
            make_round_button(base.a2dLeftCenter, (0.11, 0, 0.34), icon='grid'),
        ]

    base.start_menu = StartWindow(on_play=start_game)

    base.run()
