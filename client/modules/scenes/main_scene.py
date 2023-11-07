#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from time import sleep
from threading import Thread, Event

from panda3d.core import Vec2
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib
from panda3d.core import ClockObject
from direct.task import Task
from direct.showbase.InputStateGlobal import inputState
from direct.gui.OnscreenText import OnscreenText

from modules.scenes.scene import Scene, GameUI
from modules.assets import *
from modules.prefabs import *
from modules.utils import *


def task_update_ui():
  if geo_fmt is Phi:
    def draw(ch:str, role:str, lineno:int):
      loc = v_i2f(game.players[role].loc)
      phi = loc_to_phi(loc)
      sfx = f' {rand_char()}' if role in moving else ''
      ui_show_info(f'{ch}: {phi_str(phi)}{sfx}', lineno)
  elif geo_fmt is Loc:
    def draw(ch:str, role:str, lineno:int):
      loc = v_i2f(game.players[role].loc)
      sfx = f' {rand_char()}' if role in moving else ''
      ui_show_info(f'{ch}: {loc_str(loc)}{sfx}', lineno)
  else: raise ValueError

  draw('a', ALICE, 3)
  draw('b', BOB,   4)


def run_sched_task(is_quit:Event, interval:float, func:Callable, func_args:tuple=()):
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      sleep(interval)
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')
    quit()

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()



class MainScene(Scene):

  def __init__(self, gameUI:'GameUI'):
    super().__init__('Main', gameUI)

    self.globalClock = ClockObject.getGlobalClock()

    self.moveSpeed = 0.0024
    self.mouseSpeed = 100

    self.rotate = 0.0
    self.draggable = False
    self.lastMouseX = None

    # objects
    (self.blochNP, self.qubit1NP, self.qubit2NP), anims = make_bloch_qubits(self.loader, self.sceneNP)
    self.qubitNPs = {
      'Alice': self.qubit1NP,
      'Bob':   self.qubit2NP,
    }
    self.anims.extend(anims)

    # info
    self.txt_state = OnscreenText('', parent=self.base.a2dTopCenter, scale=0.1, pos=(0, -0.15), fg=(1, 1, 1, 1), align=TextNode.ACenter, mayChange=True)

    # controls
    inputState.watchWithModifiers('U', 'w', inputSource=inputState.WASD)
    inputState.watchWithModifiers('L', 'a', inputSource=inputState.WASD)
    inputState.watchWithModifiers('D', 's', inputSource=inputState.WASD)
    inputState.watchWithModifiers('R', 'd', inputSource=inputState.WASD)
    if 'debug':
      inputState.watchWithModifiers('_U', 'arrow_up',    inputSource=inputState.ArrowKeys)
      inputState.watchWithModifiers('_L', 'arrow_left',  inputSource=inputState.ArrowKeys)
      inputState.watchWithModifiers('_D', 'arrow_down',  inputSource=inputState.ArrowKeys)
      inputState.watchWithModifiers('_R', 'arrow_right', inputSource=inputState.ArrowKeys)

    self.taskMgr.add(self.handleKeyboard, 'handleKeyboard')
    self.taskMgr.add(self.handleMouse,    'handleMouse')

  def enter(self):
    self.base.setBackgroundColor(0.2, 0.2, 0.2, 0.5)
    self.cam.setPos(0, -16, 0)
    self.cam.lookAt(self.blochNP)

    self.base.accept('mouse1',    self.setDrag, [True])
    self.base.accept('mouse1-up', self.setDrag, [False])
    super().enter()

    pos = self.qubitNPs[self.gameUI.role].getPos()
    rot = pos_to_rot(pos)
    self.txt_state.setText(phi_str(loc_to_phi((rot.x, rot.y))))

  def leave(self):
    self.txt_state.setText('')

    super().leave()
    self.base.ignore('mouse1')
    self.base.ignore('mouse1-up')

  ''' utils '''

  def setDrag(self, draggable:bool):
    self.draggable = draggable
    self.lastMouseX = None

  def handleMouse(self, task):
    # mouse click down
    if not self.draggable: return Task.cont
    # cursor in window
    mw = self.base.mouseWatcherNode
    if not mw.hasMouse(): return Task.cont

    x = mw.getMouseX()
    dx = (x - self.lastMouseX) if self.lastMouseX is not None else 0
    self.lastMouseX = x

    self.rotate += dx * self.mouseSpeed
    self.blochNP.setH(self.rotate)

    return Task.cont

  def handleKeyboard(self, task):
    # dt = self.globalClock.getDt()

    wheel = Vec2(0, 0)
    if inputState.isSet('U'): wheel.setX(-1.0)
    if inputState.isSet('D'): wheel.setX(+1.0)
    if inputState.isSet('L'): wheel.setY(-1.0)
    if inputState.isSet('R'): wheel.setY(+1.0)
    if wheel == NO_MOVE: return Task.cont

    qubitNP = self.qubitNPs[self.gameUI.role]
    pos = qubitNP.getPos()
    rot = pos_to_rot(pos)
    rot += wheel * self.moveSpeed
    pos_new = rot_to_pos(rot) * pos.length()
    qubitNP.setPos(pos_new)
    self.txt_state.setText(phi_str(loc_to_phi((rot.x, rot.y))))
    
    return Task.cont

  def mov_sim(self):
    is_quit = Event()
    run_sched_task(is_quit, 1/FPS, task_update_ui, (self.gameUI.game, self.qubitNPs))
