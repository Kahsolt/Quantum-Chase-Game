#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from time import sleep
from threading import Thread, Event

from socketio import Client

from panda3d.core import Vec2
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib
from panda3d.core import ClockObject
from direct.task import Task
from direct.showbase.InputStateGlobal import inputState
from direct.gui.OnscreenText import OnscreenText

from modules.scenes.scene import Scene, UI
from modules.assets import *
from modules.prefabs import *
from modules.utils import *

Packet = Dict[str, Any]
Data = Dict[str, Any]

'''
{
  type: str
  id: str
  count: int
  loc: [int, int]
  ttl: int        // 生存时长
  ts: int         // 出生时间
}
'''
SpawnItem = Dict[str, Any]

def unpack_data(fn):
  def wrapper(app, pack:Packet):
    print(f'>> [{fn.__name__}]: {pack}')
    if not pack['ok']:
      print('>> error: ' + pack['error'])
      return
    return fn(app, pack['data'])
  return wrapper

DIR_MAPPING = {
  ( 0,  0): None,
  (+1,  0): 0,
  (+1, +1): 1,
  ( 0, +1): 2,
  (-1, +1): 3,
  (-1,  0): 4,
  (-1, -1): 5,
  ( 0, -1): 6,
  (+1, -1): 7,
}

def task_show_state(game:Game, txt_state:OnscreenText):
  loc = v_i2f(game.players[game.me].loc)
  rot = Vec2(*loc)
  txt_state.setText(phi_str(loc_to_phi((rot.x, rot.y))))

def task_update_qubit_loc(game:Game, qubits:Dict[str, NodePath]):
  for role, qubit in qubits.items():
    loc = v_i2f(game.players[role].loc)
    rot = Vec2(*loc)
    pos = rot_to_pos(rot) * qubit.getPos().length()
    qubit.setPos(pos)

def make_sched_task(is_quit:Event, interval:float, func:Callable, func_args:tuple=(), cond:Callable=None) -> Thread:
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      sleep(interval)
      if is_quit.is_set(): break
      if cond is not None and not cond(): continue
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')

  if not isinstance(func_args, tuple): func_args = (func_args,)
  return Thread(target=wrapped_task, daemon=True)


class MainScene(Scene):

  def __init__(self, ui:'UI'):
    super().__init__('Main', ui)

    self.globalClock = ClockObject.getGlobalClock()

    # drag bloch
    self.mouseSpeed = 100
    self.draggable = False
    self.rotateX = 0.0
    self.rotateY = 0.0
    self.lastMouseX = None
    self.lastMouseY = None

    # objects
    (self.blochNP, self.qubit1NP, self.qubit2NP), anims = make_bloch_qubits(self.loader, self.sceneNP)
    self.qubitNPs = {
      ALICE: self.qubit1NP,
      BOB:   self.qubit2NP,
    }
    self.anims.extend(anims)

    # dynamic objects
    self.itemsNP = self.blochNP.attachNewNode('items')
    self.itemNPs: List[Tuple[SpawnItem, NodePath]] = []

    # info
    self.txt_role    = OnscreenText('', parent=self.base.a2dTopLeft,    scale=0.1, pos=(+0.04, -0.15),  fg=(1, 1, 1, 1), align=TextNode.ALeft,   mayChange=True)
    self.txt_state   = OnscreenText('', parent=self.base.a2dTopCenter,  scale=0.1, pos=(0,     -0.15),  fg=(1, 1, 1, 1), align=TextNode.ACenter, mayChange=True)
    self.txt_photons = OnscreenText('', parent=self.base.a2dBottomLeft, scale=0.1, pos=(+0.04, +0.16), fg=(1, 1, 1, 1), align=TextNode.ALeft,   mayChange=True)
    self.txt_gates   = OnscreenText('', parent=self.base.a2dBottomLeft, scale=0.1, pos=(+0.04, +0.06), fg=(1, 1, 1, 1), align=TextNode.ALeft,   mayChange=True)

    # Server
    sio = Client(reconnection=False)
    method_type = type(self.__init__)
    print('>> register events:')
    for attr in dir(self):
      if not attr.startswith('on_'): continue
      obj = getattr(self, attr)
      if type(obj) != method_type: continue
      event = attr[len('on_'):].replace('_', ':')
      print(' ', event)
      sio.on(event, obj)
    self.sio = sio

    self.game: Game = None
    self.thrs: List[Thread] = []
    self.is_quit = Event()
    self.is_connected = None
    self.is_joined = None
    self.is_moving = False
    self.is_entangled = None

    # controls
    # ref: https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support
    inputState.watch('U', 'w', 'w-up', inputSource=inputState.WASD)
    inputState.watch('L', 'a', 'a-up', inputSource=inputState.WASD)
    inputState.watch('D', 's', 's-up', inputSource=inputState.WASD)
    inputState.watch('R', 'd', 'd-up', inputSource=inputState.WASD)
    self.base.accept('space',     self.try_pick_item)
    self.base.accept('shift-p',   self.try_use_photon)
    self.base.accept('shift-x',   self.try_use_gate, ['X'])
    self.base.accept('shift-y',   self.try_use_gate, ['Y'])
    self.base.accept('shift-z',   self.try_use_gate, ['Z'])
    self.base.accept('shift-s',   self.try_use_gate, ['S'])
    self.base.accept('shift-t',   self.try_use_gate, ['T'])
    self.base.accept('shift-m',   self.try_use_gate, ['M'])
    self.base.accept('alt-x',     self.try_use_gate, ['RX'])
    self.base.accept('alt-y',     self.try_use_gate, ['RY'])
    self.base.accept('alt-z',     self.try_use_gate, ['RZ'])
    self.base.accept('control-s', self.try_use_gate, ['SWAP'])
    self.base.accept('control-x', self.try_use_gate, ['CNOT'])

    self.taskMgr.add(self.handleKeyboard, 'handleKeyboard')
    self.taskMgr.add(self.handleMouse,    'handleMouse')

  def enter(self):
    self.base.setBackgroundColor(0.2, 0.2, 0.2, 0.5)
    self.cam.setPos(0, -16, 0)
    self.cam.lookAt(self.blochNP)

    self.base.accept('mouse1',    self.setDrag, [True])
    self.base.accept('mouse1-up', self.setDrag, [False])
    super().enter()

  def leave(self):
    self.txt_state.setText('')

    super().leave()
    self.base.ignore('mouse1')
    self.base.ignore('mouse1-up')

  ''' utils '''

  def setDrag(self, draggable:bool):
    self.draggable = draggable
    self.lastMouseX = None
    self.lastMouseY = None

  def handleMouse(self, task):
    # mouse click down
    if not self.draggable: return Task.cont
    # cursor in window
    mw = self.base.mouseWatcherNode
    if not mw.hasMouse(): return Task.cont

    x, y = mw.getMouseX(), mw.getMouseY()
    dx = (x - self.lastMouseX) if self.lastMouseX is not None else 0
    dy = (y - self.lastMouseY) if self.lastMouseY is not None else 0
    self.lastMouseX = x
    self.lastMouseY = y

    self.rotateX += dx * self.mouseSpeed
    self.rotateY -= dy * self.mouseSpeed / 10
    self.rotateY = clip(self.rotateY, -30, +30)
    self.blochNP.setH(self.rotateX)
    self.blochNP.setP(self.rotateY)

    return Task.cont

  def handleKeyboard(self, task):
    if not self.active: return Task.cont
    if self.is_entangled: return Task.cont

    horz, vert = 0, 0
    if inputState.isSet('R'): horz += 1
    if inputState.isSet('L'): horz -= 1
    if inputState.isSet('U'): vert += 1
    if inputState.isSet('D'): vert -= 1

    new_dir = DIR_MAPPING[(horz, vert)]
    old_dir = self.player.dir
    if new_dir == old_dir: return Task.cont

    if new_dir is None:
      self.emit_mov_stop()
    else:
      self.emit_mov_start(new_dir)

    return Task.cont

  ''' game helpers '''

  def connect_server(self):
    args = self.ui.args
    self.sio.connect(f'http://{args.host}:{args.port}', transports=['websocket'])

  @property
  def role(self) -> str:
    return self.game.me

  @property
  def player(self) -> Player:
    return self.game.players[self.role]

  @property
  def loc(self) -> Loc:
    pos = self.qubitNPs[self.role].getPos()
    rot = pos_to_rot(pos)
    return rot.x, rot.y   # (tht, psi)

  @property
  def phi(self) -> Phi:
    return loc_to_phi(self.loc)

  @property
  def radius(self) -> float:   # 球模型半径
    return self.qubitNPs[self.role].getPos().length()

  def photons_str(self) -> str:
    return f'photons({self.player.photon})'

  def gates_str(self) -> str:
    s = 'gates: '
    for gate, cnt in self.player.gate.items():
      s += f'{gate}({cnt}) '
    return s

  def try_pick_item(self) -> str:
    print('>> try_pick_item')

    min_dist, ts = 1e5, None
    for item, itemNP in self.itemNPs:
      dist = loc_dist(v_i2f(self.player.loc), v_i2f(item['loc']))
      if dist < min_dist:
        min_dist = dist
        ts = item['ts']

    if min_dist < PICK_RADIUS and ts is not None:
      self.emit_item_pick(ts)

  def try_use_photon(self):
    print('>> try_use_photon')

    if self.player.photon < 1: print('>> item not enough') ; return
    cnt = min(self.player.photon, 100)
    self.emit_loc_query(cnt)

  def try_use_gate(self, gate:str):
    print('>> try_use_gate')

    if gate == 'SWAP':
      if self.player.gate.get('SWAP', 0) < 1: print('>> item not enough') ; return
      self.emit_gate_swap()
    elif gate == 'CNOT':
      if self.player.gate.get('CNOT', 0) < 1: print('>> item not enough') ; return
      self.emit_gate_cnot()
    elif gate == 'M':
      if self.player.gate.get('M', 0) < 1: print('>> item not enough') ; return
      self.emit_gate_meas()
    else:
      if self.player.gate.get(gate, 0) < 1: print('>> item not enough') ; return
      self.emit_gate_rot(gate)

  def item_spawn_object(self, item:SpawnItem):
    print('>> item_spawn_object')

    model = self.loader.loadModel(MO_CUBE)
    itemNP = model.copyTo(self.itemsNP)
    itemNP.setTextureOff()
    itemNP.setColor(1, 1, 0.8)
    itemNP.setScale(0.03)
    labelNP = None      # TODO: add a label
    loc = v_i2f(item['loc'])
    rot = Vec2(*loc)
    pos = rot_to_pos(rot) * self.radius
    itemNP.setPos(pos)
    self.itemNPs.append([item, itemNP])

  def item_vanish_object(self, ts:int):
    print('>> item_vanish_object')

    for bundle in self.itemNPs:
      item, itemNP = bundle
      if item['ts'] == ts:
        itemNP.removeNode()
        self.itemNPs.remove(bundle)
        return

  def loc_hint_object(self, z:float):
    R = self.radius           # 大圆半径
    Z = z * R                 # 小圆纬度
    r = (R**2 - Z**2) ** 0.5  # 小圆半径

    lines = LineSegs()
    n_div = 180
    tht = pi * 2 / n_div
    X = r * cos(0)
    Y = r * sin(0)
    lines.moveTo(X, Y, Z)
    for i in range(n_div):
      X = r * cos(i * tht)
      Y = r * sin(i * tht)
      lines.drawTo(X, Y, Z)
    lines.setThickness(4)
    hintNP = NodePath(lines.create())
    hintNP.setTextureOff()
    hintNP.setColor(1.0, 1.0, 0.7)
    hintNP.reparentTo(self.blochNP)

    def removeNodeTask(task):
      nonlocal hintNP
      hintNP.removeNode()
      return Task.done

    self.taskMgr.doMethodLater(LOC_QUERY_TTL, removeNodeTask, 'loc_hint')

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
    self.start_threads()

    self.txt_role.setText(self.role)
    if self.role == ALICE:
      self.txt_role.setFg(Vec4(0.7, 0.7, 1, 1))
    else:
      self.txt_role.setFg(Vec4(1, 0.7, 0.7, 1))
    self.txt_state.setText(phi_str(self.phi))
    self.txt_photons.setText(self.photons_str())
    self.txt_gates.setText(self.gates_str())

    self.ui.switch_scene('Main')

  @unpack_data
  def on_game_settle(self, data:Data):
    self.stop_threads()
  
    winner = data['winner']
    endTs = data['endTs']
    print(f'>> winner: {winner}, endTs: {endTs}')

    self.game = None
    self.sio.disconnect()
    self.switch_scene('Title')

  @unpack_data
  def on_game_sync(self, data:Data):
    self.player[self.role] = data

  @unpack_data
  def on_mov_start(self, data:Data):
    id = data['id']
    player = self.game.players[id]
    player.dir = data['dir']
    if 'spd' in data:
      player.spd = data['spd']
    
    if id == self.role:
      self.is_moving = True

  @unpack_data
  def on_mov_stop(self, data:Data):
    for id, loc in data.items():
      player = self.game.players[id]
      player.dir = None
      player.loc = [(x + y) / 2 for x, y in zip(loc, player.loc)]   # sync fix

      if id == self.role:
        self.is_moving = False

  @unpack_data
  def on_loc_sync(self, data:Data):
    for id, loc in data.items():
      self.game.players[id].loc = loc

  @unpack_data
  def on_loc_query(self, data:Data):
    freq = data['freq']
    print('freq:', freq)
    p0, p1 = [e / sum(freq) for e in freq]
    z = p0 * 2 - 1    # [-1, +1]
    self.loc_hint_object(z)

  @unpack_data
  def on_item_spawn(self, data:Data):
    item = data['item']
    item['loc'] = data['loc']   # make flatten
    item['ttl'] = data['ttl']
    item['ts']  = data['ts']
    self.item_spawn_object(item)

  @unpack_data
  def on_item_vanish(self, data:Data):
    ts = data['ts']
    self.item_vanish_object(ts)

  @unpack_data
  def on_item_pick(self, data:Data):
    player = self.player
    item = data['item']
    if item['type'] == 'photon':
      player.photon += item['count']
      self.txt_photons.setText(self.photons_str())
    else:
      item_id = item['id']
      if item_id in player.gate:
        player.gate[item_id] += item['count']
      else:
        player.gate[item_id] = item['count']
      self.txt_gates.setText(self.gates_str())

  @unpack_data
  def on_gate_rot(self, data:Data):
    if 'state' in data:       # 纠缠态演化
      state = data['state']
      state_str = str(state)
      self.txt_state.setText(state_str)
    else:                     # 旋转自己
      for id, loc in data.items():
        self.game.players[id].loc = loc

  @unpack_data
  def on_gate_swap(self, data:Data):
    for id, loc in data.items():
      self.game.players[id].loc = loc

  @unpack_data
  def on_gate_cnot(self, data:Data):
    state = data['state']

  @unpack_data
  def on_gate_meas(self, data:Data):
    for id, loc in data.items():
      self.game.players[id].loc = loc

  @unpack_data
  def on_entgl_freeze(self, data:Data):
    self.is_entangled = True

  @unpack_data
  def on_entgl_break(self, data:Data):
    self.is_entangled = False

  ''' emitters '''

  def emit_game_join(self, room:str, r:int):
    if self.is_joined: return

    if not self.is_connected:
      self.connect_server()

    # 在这里执行开局掷币协议
    print(f'>> room: {room}, r: {r}')
    self.sio.emit('game:join', {
      'rid': room, 
      'r': r,
      #'debug': True,
    })
    self.is_joined = True
    print('>> waiting...')

  def emit_game_sync(self):
    self.sio.emit('game:sync', {})

  def emit_mov_start(self, dir:int):
    if self.is_entangled: print('>> cannot do this in entangle state') ; return

    self.sio.emit('mov:start', {
      'dir': dir,
    })

  def emit_mov_stop(self):
    if self.is_entangled: print('>> cannot do this in entangle state') ; return

    self.sio.emit('mov:stop', {})

  def emit_loc_query(self, cnt:int):
    if self.is_entangled: print('>> cannot do this in entangle state') ; return

    self.sio.emit('loc:query', {
      'photon': cnt,
      'basis': 'Z',   # only Z supported
    })

  def emit_item_pick(self, ts:int):
    self.sio.emit('item:pick', {'ts': ts})

  def emit_gate_rot(self, gate:str):
    self.sio.emit('gate:rot', {
      'gate': gate,
    })

  def emit_gate_swap(self):
    self.sio.emit('gate:swap', {})

  def emit_gate_cnot(self):
    self.sio.emit('gate:cnot', {})

  def emit_gate_meas(self):
    self.sio.emit('gate:meas', {})

  ''' workers '''

  def start_threads(self):
    self.is_quit.clear()
    self.thrs.extend([
      make_sched_task(self.is_quit, 1/FPS, task_sim_loc,           self.game,                  cond=(lambda: not self.is_entangled)),
      make_sched_task(self.is_quit, 1/FPS, task_update_qubit_loc, (self.game, self.qubitNPs),  cond=(lambda: not self.is_entangled)),
      make_sched_task(self.is_quit, 4/FPS, task_show_state,       (self.game, self.txt_state), cond=(lambda: not self.is_entangled)),
    ])
    for thr in self.thrs:
      thr.start()

  def stop_threads(self):
    self.is_quit.set()
    for thr in self.thrs:
      thr.join()
    self.thrs.clear()
