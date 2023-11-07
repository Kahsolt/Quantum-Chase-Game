#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

import sys
from typing import Dict

from panda3d.core import Vec3, Vec4
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from panda3d.core import DirectionalLight, AmbientLight
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText

from modules.scenes import *
from modules.utils import *


class UI(ShowBase):   # aka. SceneManager

  def __init__(self, args):
    super().__init__()

    self.args = args

    # Scenes
    self.cur_scene = None
    self.title_scene = TitleScene(self)
    self.main_scene = MainScene(self)
    self.scenes: Dict[str, Scene] = {
      self.title_scene.name: self.title_scene,
      self.main_scene.name:  self.main_scene,
    }
    self.switch_scene('Title')

    # Light
    self.render.clearLight()
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(1.0, 1.0, 0.8, 0.75))
    alightNP = self.render.attachNewNode(alight)
    self.render.setLight(alightNP)
    dlight = DirectionalLight('directionalLight')
    dlight.setPoint(Vec3(-10, 10, 10))
    dlight.setDirection(Vec3(-1, 1, -1))
    dlight.setColor(Vec4(1.0, 0.75, 0.5, 0.8))
    dlightNP = self.render.attachNewNode(dlight)
    self.render.setLight(dlightNP)

    # Mouse
    self.disableMouse()
    wp = WindowProperties()
    wp.setMouseMode(WindowProperties.M_relative)
    self.win.requestProperties(wp)

    # Input
    self.accept('escape', sys.exit, [0])
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleShowVertices)
    self.accept('f4', self.toggleTexMem)
    self.accept('f5', self.screenshot)
    self.accept('f8', self.enableMouse)

    if not 'help text':
      genLabelText = lambda i, text: OnscreenText(text, parent=self.a2dTopLeft, scale=.05, pos=(0.06, -0.065 * i), fg=(1, 1, 1, 1), align=TextNode.ALeft)
      lines = [
        "ESC: Quit",
        "[F1]: Toggle Wireframe",
        "[F2]: Toggle Texture",
        "[F3]: Toggle Vertices",
        "[F4]: Texture Memory",
        "[F5]: Screenshot",
        "[F8]: Enable Mouse",
        "[1]: switch to TitleScene",
        "[2]: switch to MainScene",
      ]
      for i, line in enumerate(lines, 1):
        genLabelText(i, line)

    # Debug
    self.setFrameRateMeter(True)
    #self.render.place()

  def switch_scene(self, name:str):
    if self.cur_scene is not None:
      self.scenes[self.cur_scene].leave()
    self.cur_scene = name
    self.scenes[self.cur_scene].enter()
