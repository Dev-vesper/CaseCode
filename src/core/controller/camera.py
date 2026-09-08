import math

import builtins

from panda3d.core import ClockObject

from configs.game import settings as game_settings
from src.core.getInputs import keyboard, mouse


class CameraController:
    def __init__(self, focus=(0, 0, 0), distance=30, min_distance=6, max_distance=90,
                 rotate_speed=2.2, pitch_speed=1.4, zoom_step=0.12, drag_speed=120.0):
        self.focus = focus
        self.distance = distance
        self.distance_target = distance
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.rotate_speed = rotate_speed
        self.pitch_speed = pitch_speed
        self.zoom_step = zoom_step
        self.drag_speed = drag_speed
        self.look_yaw = 0.0
        self.look_pitch = 0.0
        self.azimuth = math.pi / 4
        self.azimuth_target = math.pi / 4
        self.elevation = 0.9
        self.elevation_target = 0.9
        self.min_elevation = 0.25
        self.max_elevation = 1.5

        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('CameraController requires a ShowBase instance to exist first.')
        base.disableMouse()
        mouse.init()
        base.taskMgr.add(self.update, 'camera_update')

    def update(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        speed = game_settings.get('camera_speed') / 5.0

        if keyboard.a_down():
            self.azimuth_target -= self.rotate_speed * speed * dt
        if keyboard.d_down():
            self.azimuth_target += self.rotate_speed * speed * dt
        if keyboard.w_down():
            self.elevation_target = min(self.max_elevation, self.elevation_target + self.pitch_speed * speed * dt)
        if keyboard.s_down():
            self.elevation_target = max(self.min_elevation, self.elevation_target - self.pitch_speed * speed * dt)

        drag_dx, drag_dy = mouse.middle_drag_delta()
        if drag_dx or drag_dy:
            if game_settings.get('invert_drag_y'):
                drag_dy = -drag_dy
            self.look_yaw -= drag_dx * self.drag_speed
            self.look_pitch = max(-89.0, min(89.0, self.look_pitch + drag_dy * self.drag_speed))

        notches = mouse.scroll_delta()
        if notches:
            zoom_step = self.zoom_step * (game_settings.get('zoom_speed') / 5.0)
            self.distance_target *= (1 - zoom_step) ** notches
            self.distance_target = max(self.min_distance, min(self.max_distance, self.distance_target))

        self.azimuth += (self.azimuth_target - self.azimuth) * min(1.0, dt * 8)
        self.elevation += (self.elevation_target - self.elevation) * min(1.0, dt * 8)
        self.distance += (self.distance_target - self.distance) * min(1.0, dt * 8)

        horizontal = self.distance * math.cos(self.elevation)
        base = builtins.base
        base.camera.setPos(
            self.focus[0] + horizontal * math.cos(self.azimuth),
            self.focus[1] + horizontal * math.sin(self.azimuth),
            self.focus[2] + self.distance * math.sin(self.elevation),
        )
        base.camera.lookAt(*self.focus)
        hpr = base.camera.getHpr()
        base.camera.setHpr(hpr.x + self.look_yaw,
                           max(-89.0, min(89.0, hpr.y + self.look_pitch)), 0)
        return task.cont
