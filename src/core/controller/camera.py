import math

import builtins

from panda3d.core import ClockObject

from src.core.getInputs import keyboard, mouse


class CameraController:
    def __init__(self, focus=(0, 0, 0), distance=30, min_distance=6, max_distance=90,
                 rotate_speed=2.2, pitch_speed=1.4, zoom_step=0.12, drag_speed=3.0):
        self.focus = focus
        self.distance = distance
        self.distance_target = distance
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.rotate_speed = rotate_speed
        self.pitch_speed = pitch_speed
        self.zoom_step = zoom_step
        self.drag_speed = drag_speed
        self.azimuth = math.pi / 4
        self.elevation = 0.9
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

        if keyboard.a_down():
            self.azimuth -= self.rotate_speed * dt
        if keyboard.d_down():
            self.azimuth += self.rotate_speed * dt
        if keyboard.w_down():
            self.elevation = min(self.max_elevation, self.elevation + self.pitch_speed * dt)
        if keyboard.s_down():
            self.elevation = max(self.min_elevation, self.elevation - self.pitch_speed * dt)

        drag_dx, drag_dy = mouse.middle_drag_delta()
        if drag_dx or drag_dy:
            self.azimuth += drag_dx * self.drag_speed
            self.elevation = max(self.min_elevation,
                                 min(self.max_elevation, self.elevation + drag_dy * self.drag_speed))

        notches = mouse.scroll_delta()
        if notches:
            self.distance_target *= (1 - self.zoom_step) ** notches
            self.distance_target = max(self.min_distance, min(self.max_distance, self.distance_target))

        self.distance += (self.distance_target - self.distance) * min(1.0, dt * 8)

        horizontal = self.distance * math.cos(self.elevation)
        base = builtins.base
        base.camera.setPos(
            self.focus[0] + horizontal * math.cos(self.azimuth),
            self.focus[1] + horizontal * math.sin(self.azimuth),
            self.focus[2] + self.distance * math.sin(self.elevation),
        )
        base.camera.lookAt(*self.focus)
        return task.cont
