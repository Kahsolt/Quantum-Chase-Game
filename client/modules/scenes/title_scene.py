#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from typing import List

from panda3d.core import Vec4
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.DirectRadioButton import DirectRadioButton

from modules.scenes.scene import Scene, UI
from modules.scenes.main_scene import MainScene
from modules.prefabs import *
from modules.assets import *
from modules.utils import *


class TitleScene(Scene):

  def __init__(self, ui:'UI'):
    super().__init__('Title', ui)

    # vars
    self.v_room = [ui.args.room]
    self.v_bit  = [rand_bit()]

    # flying cores
    self._create_flying_core('warm', colors_warm, +30)
    self._create_flying_core('cold', colors_cold, -30)

    # form
    #self._create_form()

    # controls
    self.base.accept('enter', self.try_join_game)

  def _create_flying_core(self, name:str, flame_colors:List[Vec4], offsetX:int=30):
    # A floating ball.
    objs, anims = make_solar(self.loader, self.sceneNP, name, flame_colors[0], offsetX)
    self.anims.extend(anims)

    # It leaves a trail of flames.
    satellite = objs[-1]
    objs, anims = make_trail(self.loader, self.sceneNP, satellite, flame_colors)
    self.anims.extend(anims)

  def _create_form(self):
    DirectEntry(pos=(1, 1, 0), scale=0.1, command=self.set_room, initialText='test', numLines=1, focus=True, textMayChange=True)
    buttons = [
      DirectRadioButton(text='0', variable=self.v_bit, value=[0], scale=0.15, pos=(0, +10, 0)),
      DirectRadioButton(text='1', variable=self.v_bit, value=[1], scale=0.15, pos=(0, -10, 0)),
    ]
    for button in buttons: button.setOthers(buttons)
    
    #self.wbar = DirectWaitBar()
    self.txt_error = DirectLabel(scale=0.1)
    DirectButton(text='Start!', scale=0.1, command=self.try_join_game)

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
    # 从 ui 控件收取信息
    room = self.v_room[0]
    r = self.v_bit[0]

    try:
      main_scene: MainScene = self.ui.main_scene
      main_scene.emit_game_join(room, r)
    except:
      #self.txt_error.setText('>> error!')
      print_exc()
