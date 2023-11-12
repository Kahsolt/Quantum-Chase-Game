#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from panda3d.core import TextNode

from modules.assets import *
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
    frm = DirectFrame(self.base.aspect2d)
    self.guiNPs.append(frm) ; frm.hide()
    if True:
      OnscreenText(parent=frm, text='~ Quantum Chase ~',   mayChange=False, scale=0.1, pos=(0, 0.4), fg=WHITE, align=TextNode.ACenter)
      OnscreenText(parent=frm, text='where your universe', mayChange=False, scale=0.058, pos=(0, 0.22), fg=RED, align=TextNode.ACenter)
      DirectEntry(frm, initialText='test', scale=0.075, pos=(0, 0, 0.1), text_align=TextNode.ACenter, command=self.set_room, numLines=1, focus=True, textMayChange=True)
      OnscreenText(parent=frm, text='choose your bit decision', mayChange=False, scale=0.058, pos=(0, 0.00), fg=RED, align=TextNode.ACenter)
      radBits: List[DirectRadioButton] = [
        DirectRadioButton(frm, image=IMG_QUBIT(0), value=[0], variable=self.v_bit, scale=0.05, pos=(-0.1, 0, -0.12), textMayChange=False),
        DirectRadioButton(frm, image=IMG_QUBIT(1), value=[1], variable=self.v_bit, scale=0.05, pos=(+0.1, 0, -0.12), textMayChange=False),
      ]
      for rad in radBits: rad.setOthers(radBits)
      self.txtInfo = OnscreenText(parent=frm, text='', scale=0.06, pos=(0, -0.28), fg=(1.0, 1.0, 0.2, 1.0), align=TextNode.ACenter)
      self.btnStart = DirectButton(frm, text='Start!', textMayChange=False, scale=0.1, pos=(0, 0, -0.44), pad=(0.02, 0.03), command=self.try_join_game)

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
    anim_button(self.btnStart).start()

    room = self.v_room[0]
    r    = self.v_bit[0]

    try:
      from modules.scenes.main_scene import MainScene
      main_scene: MainScene = self.ui.get_scene('Main')
      main_scene.emit_game_join(room, r)
    except Exception as e:
      self.txtInfo.setText(str(e))
      print_exc()
