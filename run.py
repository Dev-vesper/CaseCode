import json

from direct.showbase.ShowBase import ShowBase

from src.core.controller.camera import CameraController
from src.core.controller.menu import SideMenu, StartWindow
from src.core.controller.player import Player
from src.core.world.loader import WorldLoader
from src.ui.buttons import make_round_button

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
        margin = 0.07
        spacing = 0.125
        row_y = -(margin + 0.045)
        base.hud_buttons = [
            make_round_button(base.a2dTopRight, (-(margin + 0.045), 0, row_y),
                              icon='hamburger', command=base.side_menu.toggle),
            make_round_button(base.a2dTopRight, (-(margin + 0.045) - spacing, 0, row_y),
                              icon='plus'),
            make_round_button(base.a2dTopRight, (-(margin + 0.045) - 2 * spacing, 0, row_y),
                              icon='grid'),
        ]

    base.start_menu = StartWindow(on_play=start_game)

    base.run()
