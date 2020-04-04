class Level:
    def __init__(self, name, sprite_dest, father):
        self.name = name
        self.father = father
        self.actors = []
        self.lights = []
        self.sprites = loader.loadModel(sprite_dest)
        self.buttons = []
        self.images = []
        self.text_nodepaths = []

    def create(self):
        # create actors
        # create models
        # create uis
        print("Created {}".format(self.name))
        return

    def destroy(self):
        # delete actors
        # delete models
        # delete uis
        print("Destroy {}".format(self.name))

        for a in self.actors:
            self.destroy_actor(a)
        for l in self.lights:
            self.destroy_light(l)
        for b in self.buttons:
            self.destroy_button(b)
        for i in self.images:
            self.destroy_image(i)
        for t in self.text_nodepaths:
            self.destroy_text_nodepaths(t)

        return

    def destroy_actor(self, a):
        a.cleanup()

    def destroy_light(self, l):
        l.removeNode()

    def destroy_button(self, b):
        b.destroy()

    def destroy_image(self, i):
        i.destroy()

    def destroy_text_nodepaths(self, t):
        t.removeNode()

    def update(self):
        return