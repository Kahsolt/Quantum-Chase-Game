#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

import sys
from typing import Dict, Any

from socketio import Client

from panda3d.core import Vec3, Vec4
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from panda3d.core import DirectionalLight, AmbientLight
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText

from modules.scenes import *
from modules.utils import *

Packet = Dict[str, Any]
Data = Dict[str, Any]

def unpack_data(fn):
  def wrapper(app, pack:Packet):
    print(f'>> [{fn.__name__}]: {pack}')
    if not pack['ok']:
      print('>> error: ' + pack['error'])
      return
    return fn(app, pack['data'])
  return wrapper


class GameUI(ShowBase):

  def __init__(self, args):
    super().__init__()

    self.args = args

    # Server
    sio = Client(reconnection=False)
    sio.on('connect',     self.on_connect)
    sio.on('disconnect',  self.on_disconnect)
    sio.on('game:join',   self.on_game_join)
    sio.on('game:start',  self.on_game_start)
    sio.on('game:settle', self.on_game_settle)
    sio.on('mov:start',   self.on_mov_start)
    sio.on('mov:stop',    self.on_mov_stop)
    sio.on('loc:sync',    self.on_loc_sync)
    sio.on('item:spawn',  self.on_item_spawn)
    sio.on('item:pick',   self.on_item_pick)
    self.sio = sio
    self.is_connected = None
    self.is_join = None
    self.game: Game = None
    self.role: str = None     # aka. game.me

    # Scenes
    self.scenes: Dict[str, Scene] = {}
    for scene_cls in SCENE_LIST:
      scene: Scene = scene_cls(self)
      self.scenes[scene.name] = scene
    self.cur_scene = None
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
    self.accept('1', self.switch_scene, ['Title'])
    self.accept('2', self.switch_scene, ['Main'])

    if 'help text':
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

  def connect_server(self):
    self.sio.connect(f'http://{self.args.host}:{self.args.port}', transports=['websocket'])

  def switch_scene(self, name:str):
    if self.cur_scene is not None:
      self.scenes[self.cur_scene].leave()
    self.cur_scene = name
    self.scenes[self.cur_scene].enter()

  ''' handlers '''

  def on_connect(self):
    self.is_connected = True
    print('>> connected')

  def on_disconnect(self):
    self.is_connected = False
    print('>> disconnect')

  @unpack_data
  def on_game_join(self, data:Data):
    print('wait for another player...')

  @unpack_data
  def on_game_start(self, data:Data):
    self.game = Game.from_dict(data)
    self.role = self.game.me
    print(f'You are {self.role}, start chasing~')
    self.switch_scene('Main')

  @unpack_data
  def on_game_settle(self, data:Data):
    winner = data['winner']
    endTs = data['endTs']
    print(f'>> winner: {winner}, endTs: {endTs}')

    self.game = None
    self.role = None
    self.sio.disconnect()
    self.switch_scene('Title')

  @unpack_data
  def on_mov_start(self, data:Data):
    id = data['id']
    player = self.game.players[id]
    player.dir = data['dir']
    if 'spd' in data:
      player.spd = data['spd']

  @unpack_data
  def on_mov_stop(self, data:Data):
    id = data['id']
    player = self.game.players[id]
    player.dir = None
    loc = data['loc']
    player.loc = [(x + y) / 2 for x, y in zip(loc, player.loc)]

  @unpack_data
  def on_loc_sync(self, data:Data):
    for id, loc in data.items():
      self.game.players[id].loc = loc

  @unpack_data
  def on_item_spawn(self, data:Data):
    item = data['item']
    info = f'>> spawn {item["type"]}:{item["id"]} {item["count"]}'
    print(info)

  @unpack_data
  def on_item_pick(self, data:Data):
    item = data['item']
    info = f'>> pick {item["type"]}:{item["id"]} {item["count"]}'
    print(info)

  ''' emitters '''

  def emit_game_join(self, room:str, r:int):
    if self.is_join: return
    if not self.is_connected:
      self.connect_server()

    # 在这里执行开局掷币协议
    print(f'>> room: {room}, r: {r}')
    self.sio.emit('game:join', {
      'rid': room, 
      'r': r,
    })
    self.is_join = True
    print('>> waiting...')

  def emit_item_pick(self):
    self.sio.emit('item:pick', {})
