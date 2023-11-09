#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from direct.showbase.ShowBase import ShowBase

from modules.prefabs.utils import Objects, Anims
from modules.prefabs.scene_fade import make_scene_fade_anims


class ShowBaseWrapper:

  def __init__(self, base:ShowBase):
    self.base = base

  @property
  def loader(self): return self.base.loader
  @property
  def render(self): return self.base.render
  @property
  def cam(self): return self.base.cam
  @property
  def taskMgr(self): return self.base.taskMgr


class Scene(ShowBaseWrapper):

  def __init__(self, name:str, ui):
    super().__init__(ui)

    from modules.ui import UI

    self.name = name
    self.ui: UI = ui    # backref
    self.isCurrentScene: bool = None
    self.animLoops: Anims = []
    self.guiNPs: Objects = []  # 2D objects root

    # create root NodePath for 3D objects
    self.sceneNP = self.render.attachNewNode(name)
    self.sceneNP.hide()
    # create scene fading in/out
    self.animIn, self.animOut = make_scene_fade_anims(self.sceneNP)

  def enter(self):
    print(f'>> enter scene: {self.name}')
    self.isCurrentScene = True
  
    for obj in self.guiNPs: obj.show()
    for anim in self.animLoops: anim.loop()
    self.sceneNP.show()
    self.animIn.start()

  def leave(self):
    print(f'>> leave scene: {self.name}')
    self.isCurrentScene = False

    self.animOut.start()
    self.sceneNP.hide()
    for anim in self.animLoops: anim.pause()
    for obj in self.guiNPs: obj.hide()

  def destory(self):
    print(f'>> destroy scene: {self.name}')

    self.sceneNP.removeNode()
    for anim in self.animLoops: anim.finish()
    self.animLoops.clear()
    for obj in self.guiNPs: obj.removeNode()
    self.guiNPs.clear()
