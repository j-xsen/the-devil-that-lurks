from panda3d.core import TextNode

class Chat:
    def  __init__(self, pos, phrase):
        chat_node = TextNode("Chat: {}".format(phrase))
        chat_node.setText(phrase)
        chat_node.setAlign(TextNode.ACenter)
        chat_node.setTextColor(0.682, 0.125, 0.121, 1)
        self.nodepath = render.attachNewNode(chat_node)
        self.nodepath.setHpr(0, 0, 0)
        self.nodepath.setScale(0.5)
        self.nodepath.setPos(pos.x, pos.y + 1.5, pos.z + 3)
        self.nodepath.setBin('fixed', 0)
