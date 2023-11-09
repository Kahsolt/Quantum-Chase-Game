#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from panda3d.core import TextNode

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton

from modules.prefabs import *
from modules.utils import *

from .scene import Scene


class TitleScene(Scene):

  def __init__(self, ui):
    super().__init__('Title', ui)

    # form vars
    self.v_room = [ui.args.room]
    self.v_bit  = [rand_bit()]

    # form widgets
    self._create_form_widgets()

    # flying cores (background anim)
    self._create_flying_core('warm', colors_warm, +30)
    self._create_flying_core('cold', colors_cold, -30)

  def _create_form_widgets(self):
    txtTitle = OnscreenText(text='~ Quantum Chase ~', scale=0.1, pos=(0, 0.4), fg=WHITE, align=TextNode.ACenter)
    lblRoom = OnscreenText(text='where your universe', scale=0.058, pos=(0, 0.22), fg=RED, align=TextNode.ACenter)
    entRoom = DirectEntry(initialText='test', scale=0.075, pos=(0, 0, 0.1), text_align=TextNode.ACenter, command=self.set_room, numLines=1, focus=True, textMayChange=True)
    txtBit = OnscreenText(text='choose your bit decision', scale=0.058, pos=(0, 0.00), fg=RED, align=TextNode.ACenter)
    radsBit = [
      DirectRadioButton(text='0', variable=self.v_bit, value=[0], scale=0.085, pos=(-0.08, 0, -0.12), boxImageColor=BLACK, textMayChange=False),
      DirectRadioButton(text='1', variable=self.v_bit, value=[1], scale=0.085, pos=(+0.08, 0, -0.12), boxImageColor=BLACK, textMayChange=False),
    ]
    for rad in radsBit: rad.setOthers(radsBit)
    self.txtInfo = OnscreenText(text='', scale=0.075, pos=(0, -0.28), fg=(1.0, 0.2, 0.2, 1.0), align=TextNode.ACenter)
    btnStart = DirectButton(text='Start!', scale=0.1, pos=(0, 0, -0.44), pad=(0.02, 0.03), command=self.try_join_game, textMayChange=False)

    self.guiNPs.extend([
      txtTitle,
      lblRoom, entRoom,
      txtBit, *radsBit,
      self.txtInfo, btnStart,
    ])

  def _create_flying_core(self, name:str, flame_colors:Colors, offsetX:int=30):
    objs, anims = make_solar(self.loader, self.sceneNP, name, flame_colors[0], offsetX)
    self.animLoops.extend(anims)
    satellite = objs[-1]
    _, anims = make_trail(self.loader, self.sceneNP, satellite, flame_colors)
    self.animLoops.extend(anims)

  def enter(self):
    self.base.setBackgroundColor(0.1, 0.1, 0.1, 0.75)
    self.cam.setPos(0, 0, 128)
    self.cam.lookAt(0, 0, 0)

    super().enter()

  def leave(self):
    super().leave()

  ''' utils '''

  def set_room(self, v):
    self.v_room[0] = v

  def try_join_game(self):
    room = self.v_room[0]
    r    = self.v_bit[0]

    try:
      from modules.scenes.main_scene import MainScene
      main_scene: MainScene = self.ui.get_scene('Main')
      main_scene.emit_game_join(room, r)
    except Exception as e:
      self.txtInfo.setText(str(e))
      print_exc()
