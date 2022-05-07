"""
This class is for models that are clickable

Hover - grow
Click - shrink
"""
from objects.notifier import Notifier
from direct.actor.Actor import Actor
from panda3d.core import Point3, CollisionNode, CollisionRay, GeomNode, CollisionTraverser, CollisionHandlerEvent
from direct.showbase.DirectObject import DirectObject
from direct.task import Task


class Clickable(Actor, Notifier):
    def __init__(self, level_holder, model_dir, name):
        Actor.__init__(self, model_dir)
        Notifier.__init__(self, "clickable")

        # tags
        self.setTag("clickable", "1")

        # handler
        self.level_holder = level_holder

        # STATES -
        # 0 - NEUTRAL
        # 1 - HOVER
        # 2 - SELECTED
        # 3 - MOUSED DOWN
        self.state = 0

        #task
        self.task_name = f"{name}_task"
        taskMgr.add(self.continuous_task, self.task_name)

        # self.accept('mouseRay-in-rail', self.beam)

        # node
        self.picker_node = CollisionNode('mouse_ray')
        self.picker_node_point = camera.attachNewNode(self.picker_node)
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.traverser = CollisionTraverser('traverser')
        base.cTrav = self.traverser
        self.traverser.addCollider(self.picker_node_point, self.level_holder.collision_handler)

    def continuous_task(self, task):
        # check if hovering is even relevant
        if self.state < 2:
            # First we check that the mouse is not outside the screen.
            if base.mouseWatcherNode.hasMouse():
                # This gives up the screen coordinates of the mouse.
                mpos = base.mouseWatcherNode.getMouse()
                if self.beam(mpos, False):
                    self.state = 1
                else:
                    self.state = 0
        self.set_clickable_state()
        return Task.again

    def set_clickable_state(self):
        match self.state:
            case 0:
                self.setScale(1)
            case 1:
                self.setScale(1.15)
            case 2:
                self.setScale(1.15)
            case 3:
                self.setScale(1.25)

    def beam(self, mpos, click):
        """
        Checks if mouse is over this object
        @return: Was this hit?
        @rtype: boolean
        """
        # This makes the ray's origin the camera and makes the ray point
        # to the screen coordinates of the mouse.
        self.picker_ray.setFromLens(base.camNode, mpos.x, mpos.y)
        self.traverser.traverse(render)
        if self.level_holder.collision_handler.getNumEntries() > 0:
            # This is so we get the closest object.
            self.level_holder.collision_handler.sortEntries()
            picked_object = self.level_holder.collision_handler.getEntry(0).getIntoNodePath()
            picked_object = picked_object.findNetTag('clickable')
            if not picked_object.isEmpty():
                if click:
                    self.clicked(picked_object)
                return True
        return False

    def clicked(self, entry):
        if self.state == 3:
            self.state = 1
        else:
            self.state = 3
