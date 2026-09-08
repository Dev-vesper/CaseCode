import builtins

from panda3d.core import AmbientLight, DirectionalLight


class WorldLoader:
    def __init__(self, blocks):
        self.blocks = [tuple(block) for block in blocks]
        self.root = None
        self.bounds = None
        self.center = (0, 0, 0)

    def load(self):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('WorldLoader requires a ShowBase instance to exist first.')

        self.root = base.render.attachNewNode('world')
        xs = [block[0] for block in self.blocks]
        ys = [block[1] for block in self.blocks]
        zs = [block[2] for block in self.blocks]
        self.bounds = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
        self.center = ((self.bounds[0] + self.bounds[1]) / 2,
                       (self.bounds[2] + self.bounds[3]) / 2,
                       (self.bounds[4] + self.bounds[5]) / 2)
        height_span = max(1, self.bounds[5] - self.bounds[4])

        cube = base.loader.loadModel('models/box')
        for x, y, z in self.blocks:
            block = cube.copyTo(self.root)
            block.setPos(x, y, z)
            t = (z - self.bounds[4]) / height_span
            block.setColor(0.25 + 0.45 * t, 0.40 + 0.25 * t, 0.55 - 0.25 * t, 1)
        self.root.flattenStrong()

        ambient = self.root.attachNewNode(AmbientLight('ambient'))
        ambient.node().setColor((0.35, 0.35, 0.40, 1))
        base.render.setLight(ambient)

        sun = self.root.attachNewNode(DirectionalLight('sun'))
        sun.node().setColor((0.80, 0.75, 0.70, 1))
        sun.setHpr(-45, -50, 0)
        base.render.setLight(sun)

        return self.root
