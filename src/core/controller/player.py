import builtins

from direct.actor.Actor import Actor
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.core import ClockObject

SCALE = 0.4
SPAWN_HEIGHT = 6.0


class Player:
    def __init__(self, world):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('Player requires a ShowBase instance to exist first.')

        self.physics = BulletWorld()
        self.physics.setGravity((0, 0, -9.81))

        block_shape = BulletBoxShape((0.5, 0.5, 0.5))
        self._blocks = []
        for x, y, z in world.blocks:
            block = BulletRigidBodyNode('block')
            block.addShape(block_shape)
            block.setStatic(True)
            np = base.render.attachNewNode(block)
            np.setPos(x + 0.5, y + 0.5, z + 0.5)
            self.physics.attach(np.node())
            self._blocks.append(np)

        self.model = Actor('assets/models/ralph')
        self.model.setScale(SCALE)
        self.model.reparentTo(base.render)
        lo, hi = self.model.getTightBounds()
        self.size = hi - lo
        center = (lo + hi) / 2

        self.body = BulletRigidBodyNode('player')
        body_width = min(self.size.x, self.size.y) * 0.6
        self.body.addShape(BulletBoxShape((body_width / 2, body_width / 2, self.size.z / 2)))
        self.body.setMass(1.0)
        self.body.setAngularFactor((0, 0, 0))
        self.node = base.render.attachNewNode(self.body)
        spawn = world.blocks[0]
        self.node.setPos(spawn[0] + 0.5, spawn[1] + 0.5,
                         world.bounds[5] + 1 + SPAWN_HEIGHT + self.size.z / 2)
        self.model.reparentTo(self.node)
        self.model.setPos(-center)
        self.physics.attach(self.body)

        base.taskMgr.add(self.update, 'player_physics')

    def update(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        self.physics.doPhysics(dt, 10, 1.0 / 180.0)
        return task.cont

    def destroy(self):
        builtins.base.taskMgr.remove('player_physics')
        for np in self._blocks:
            np.removeNode()
        self.node.removeNode()
