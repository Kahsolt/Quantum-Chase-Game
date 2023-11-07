#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from direct.showbase.ShowBase import ShowBase

from modules.prefabs.utils import Anims
from modules.prefabs.scene_fade import make_scene_fade_anims

# avoid cyclic import :(
try: from modules.ui import UI
except ImportError: UI = object()


class ShowBaseWrapper:

  def __init__(self, base:ShowBase):
    self.base = base
    self.loader = base.loader
    self.render = base.render
    self.cam = base.cam
    self.taskMgr = base.taskMgr


class Scene(ShowBaseWrapper):

  def __init__(self, name:str, ui:'UI'):
    super().__init__(ui)

    self.name = name
    self.ui = ui
    self.anims: Anims = []  # all loop anims
    self.active: bool = None

    # create root NodePath
    self.sceneNP = self.render.attachNewNode(name)
    self.sceneNP.hide()
    # create scene fading
    self.anim_in, self.anim_out = make_scene_fade_anims(self.sceneNP)

  def enter(self):
    print(f'>> enter {self.name}')
    self.active = True
  
    for anim in self.anims: anim.loop()
    self.sceneNP.show()
    #self.anim_in.start()

  def leave(self):
    print(f'>> leave {self.name}')
    self.active = False

    #self.anim_out.start()
    self.sceneNP.hide()
    for anim in self.anims: anim.pause()

  def destory(self):
    print(f'>> destroy {self.name}')

    self.sceneNP.removeNode()
    for anim in self.anims: anim.finish()
    self.anims.clear()
