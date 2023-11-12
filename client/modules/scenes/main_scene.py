#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/03

from time import sleep
from threading import Thread, Event

from socketio import Client

from panda3d.core import Vec2
from panda3d.core import TextNode
from direct.showbase.InputStateGlobal import inputState
from direct.task import Task

# fix import order, avoid name conflict for 'Sequence'
from modules.utils import *
from modules.prefabs import *
from modules.ui_configs import *

from .scene import Scene

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
  def wrapper(scene:'MainScene', pack:Packet):
    print(f'>> [{fn.__name__}]: {pack}')
    scene.update_latency(pack['ts'])
    if not pack['ok']:
      scene.anim_error(pack['error'])
      return
    return fn(scene, pack['data'])
  return wrapper

def show_emit(fn):
  def wrapper(scene:'MainScene', *args, **kwargs):
    print(f'>> emit [{fn.__name__}]')
    return fn(scene, *args, **kwargs)
  return wrapper

def no_entgl(fn):
  def wrapper(scene:'MainScene', *args, **kwargs):
    if scene.is_entangled:
      scene.anim_error('cannot do this in entangle state')
      return
    return fn(scene, *args, **kwargs)
  return wrapper


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

  def __init__(self, ui):
    super().__init__('Main', ui)

    if not 'use clock':
      from panda3d.core import ClockObject
      self.globalClock = ClockObject.getGlobalClock()

    # drag bloch
    self.mouseSpeed = 100
    self.draggable = False
    self.rotateX = 0.0
    self.rotateY = 0.0
    self.lastMouseX = None
    self.lastMouseY = None

    # bloch & qubits
    self._create_bloch_qubits()
    # player controls
    self._create_player_controls()

    # item spawns
    self.itemsNP = self.blochNP.attachNewNode('items')
    self.itemNPs: List[Tuple[SpawnItem, NodePath]] = []

    # server
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

    # game
    self.is_connected = None
    self.join_info: Tuple[Any] = None
    self.game: Game = None
    self.thrs: List[Thread] = []
    self.is_quit = Event()
    self.is_moving: Dict[Role, bool] = {
      ALICE: True,
      BOB:   True,
    }
    self.is_entangled = None
    self.entgl_phi: EntglPhi = None

    # network latency
    self.txtLatentcy = OnscreenText(parent=self.base.a2dTopRight, scale=0.05, pos=(-0.02, -0.1), fg=WHITE, bg=BLACK, align=TextNode.ARight, mayChange=True)
    self.vwin_latency = ValueWindow(15)

    # controls
    # ref: https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support
    inputState.watch('U', 'w', 'w-up', inputSource=inputState.WASD)
    inputState.watch('L', 'a', 'a-up', inputSource=inputState.WASD)
    inputState.watch('D', 's', 's-up', inputSource=inputState.WASD)
    inputState.watch('R', 'd', 'd-up', inputSource=inputState.WASD)
    self.base.accept('space', self.try_pick_item)

    self.taskMgr.add(self.handleKeyboard, 'handleKeyboard')
    self.taskMgr.add(self.handleMouse,    'handleMouse')

  def _create_bloch_qubits(self):
    (self.blochNP, self.qubit1NP, self.qubit2NP), anims = make_bloch_qubits(self.loader, self.sceneNP)
    self.qubitNPs = {
      ALICE: self.qubit1NP,
      BOB:   self.qubit2NP,
    }
    self.animLoops.extend(anims)

  def _create_player_controls(self):
    self.txtError = OnscreenText(text='', mayChange=True, parent=self.base.aspect2d,      scale=0.1, pos=(0, 0),         fg=RED,   align=TextNode.ACenter)
    self.txtRole  = OnscreenText(text='', mayChange=True, parent=self.base.a2dTopLeft,    scale=0.1, pos=(+0.04, -0.15), fg=WHITE, align=TextNode.ALeft)
    self.txtState = OnscreenText(text='', mayChange=True, parent=self.base.a2dTopCenter,  scale=0.1, pos=(0,     -0.15), fg=WHITE, align=TextNode.ACenter)
    self.txtItems: Dict[str, OnscreenText] = {}
    self.btnItems: Dict[str, DirectButton] = {}

    # silder - gate theta
    frm = DirectFrame(self.base.aspect2d)
    self.frm_theta = frm ; frm.hide()
    if True:
      self.v_gate: str = None
      self.v_theta: float = 0.0    # [-pi, pi]

      def showValueTheta():
        nonlocal sldTheta, lblTheta
        n: int = round(sldTheta['value'])   # [-32, 32]
        self.v_theta = n / THETA_QV * pi    # [-pi, pi]
        sign = 1 if n >= 0 else -1 
        a, b = frac_norm(abs(n), THETA_QV)
        if a == 0:
          theta_str = '0'
        elif a == b == 1:
          theta_str = 'pi'
        else:
          theta_str = f'{a*sign}/{b} pi'
        lblTheta.setText(f'theta = {theta_str}')

      def onCancelTheta():
        self.frm_theta.hide()

      def onConfirmTheta():
        self.frm_theta.hide()
        self.use_param_rot_gate()

      sldTheta = DirectSlider(frm, scale=0.5, pos=(0, 0, 0.15), range=(-THETA_QV, THETA_QV), value=0, pageSize=1, command=showValueTheta, frameColor=WHITE)
      lblTheta = DirectLabel(frm, text='theta = 0', scale=0.075, pos=(0, 0, 0), text_style=BlackOnWhite, textMayChange=True)
      DirectButton(frm, text='Cancel', text_bg=RED,   scale=0.1, pos=(-0.15, 0, -0.2), textMayChange=False, command=onCancelTheta)
      DirectButton(frm, text='OK',     text_bg=GREEN, scale=0.1, pos=(+0.15, 0, -0.2), textMayChange=False, command=onConfirmTheta)

    # silder - photons
    frm = DirectFrame(self.base.aspect2d)
    self.frm_photon = frm ; frm.hide()
    if True:
      self.v_photon: int = 100

      def showValuePhoton():
        nonlocal sldPhoton, lblPhoton
        n: int = round(sldPhoton['value'])   # [-32, 32]
        self.v_photon = n
        lblPhoton.setText(f'measure {n} photons')

      def onCancelPhoton():
        self.frm_photon.hide()

      def onConfirmPhoton():
        self.frm_photon.hide()
        self.try_use_photon()

      sldPhoton = DirectSlider(frm, scale=0.5, pos=(0, 0, 0.15), range=(1, 9999), value=100, pageSize=10, command=showValuePhoton, frameColor=WHITE)
      lblPhoton = DirectLabel(frm, text='', scale=0.075, pos=(0, 0, 0), text_style=BlackOnWhite, textMayChange=True)
      self.sldPhoton = sldPhoton
      DirectButton(frm, text='Cancel', text_bg=RED,   scale=0.1, pos=(-0.15, 0, -0.2), textMayChange=False, command=onCancelPhoton)
      DirectButton(frm, text='OK',     text_bg=GREEN, scale=0.1, pos=(+0.15, 0, -0.2), textMayChange=False, command=onConfirmPhoton)

    # buttons - gate
    frm = DirectFrame(self.base.a2dBottomLeft)
    self.guiNPs.append(frm) ; frm.hide()
    if True:
      label_size = 0.08
      label_offset = 0.1

      for i, name in enumerate(GATE_NAMES):
        offset = GATE_SCALE * (2 * i + 1) + GATE_PAD * i
        btn = DirectButton(frm, image=IMG_GATE(name), textMayChange=False, scale=GATE_SCALE, pos=(offset, 0, GATE_SCALE), command=self.try_use_gate, extraArgs=[name])
        self.btnItems[name] = btn
        txt = OnscreenText(text='', mayChange=True, parent=frm, scale=label_size, pos=(offset, GATE_SCALE+label_offset), fg=RED, align=TextNode.ACenter)
        self.txtItems[name] = txt
      offset += GATE_SPLIT_PAD

      offset += 2 * GATE_SCALE + GATE_PAD
      if 'theta':
        name = 'theta'
        btn = DirectButton(frm, image=IMG_AUX(name), textMayChange=False, scale=GATE_SCALE, pos=(offset, 0, GATE_SCALE), command=self.anim_error, extraArgs=['try use R* gate'])
        self.btnItems[name] = btn
        txt = OnscreenText(text='', mayChange=True, parent=frm, scale=label_size, pos=(offset, GATE_SCALE+label_offset), fg=RED, align=TextNode.ACenter)
        self.txtItems[name] = txt
      offset += 2 * GATE_SCALE + GATE_PAD
      if 'photon':
        def tryShowPhtonFrame():
          if self.player.photons <= 0:
            self.anim_error('photon not enough')
            return
          self.frm_photon.show()

        name = 'photon'
        btn = DirectButton(frm, image=IMG_AUX(name), textMayChange=False, scale=GATE_SCALE, pos=(offset, 0, GATE_SCALE), command=tryShowPhtonFrame)
        self.btnItems[name] = btn
        txt = OnscreenText(text='', mayChange=True, parent=frm, scale=label_size, pos=(offset, GATE_SCALE+label_offset), fg=RED, align=TextNode.ACenter)
        self.txtItems[name] = txt

  def enter(self):
    self.base.setBackgroundColor(0.2, 0.2, 0.2, 0.5)
    self.cam.setPos(0, -16, 0)
    self.cam.lookAt(self.blochNP)

    self.base.accept('mouse1',    self.setDrag, [True])
    self.base.accept('mouse1-up', self.setDrag, [False])
    super().enter()

  def leave(self):
    self.txtState.setText('')

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
    if not self.has_game: return Task.cont
    if not self.isCurrentScene: return Task.cont
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
  def has_game(self) -> bool:
    return self.game is not None

  @property
  def me(self) -> str:
    return self.game.me

  @property
  def player(self) -> Player:
    return self.game.players[self.me]

  @property
  def loc(self) -> Loc:
    return v_i2f(self.player.loc)

  @property
  def phi(self) -> Phi:
    return loc_to_phi(self.loc)

  @property
  def radius(self) -> float:   # 球模型半径
    return self.qubitNPs[self.me].getPos().length()

  def try_pick_item(self) -> str:
    max_fid, ts = 0, None
    phi1 = self.phi
    for item, itemNP in self.itemNPs:
      phi2 = loc_to_phi(v_i2f(item['loc']))
      fid = phi_fidelity(phi1, phi2)
      if fid > max_fid:
        max_fid = fid
        ts = item['ts']   # use as uid

    print('max_fid:', max_fid)
    if max_fid > PICK_FID and ts is not None:
      self.emit_item_pick(ts)

  def try_use_photon(self):
    assert self.v_photon > 0

    if self.player.photons < 1:
      self.anim_error('item not enough')
      return

    self.anim_item('photon')
    self.emit_loc_query(min(self.player.photons, self.v_photon))

  def try_use_gate(self, gate:str):
    gate = GATE_NAME_MAPPING.get(gate, gate)
    if self.player.gates.get(gate, 0) < 1:
      self.anim_error('item not enough')
      return
    if gate in P_ROT_GATES:
      if self.player.thetas < 1:
        self.anim_error('has no theta')
        return

    self.anim_item(gate)
    if   gate == 'SWAP': self.emit_gate_swap()
    elif gate == 'CNOT': self.emit_gate_cnot()
    elif gate == 'M':    self.emit_gate_meas()
    else:
      if gate in P_ROT_GATES:
        self.v_gate = gate
        self.frm_theta.show()
      else:
        self.emit_gate_rot(gate)

  def use_param_rot_gate(self):
    assert self.v_gate is not None
    assert self.v_theta is not None
    self.emit_gate_rot(self.v_gate, self.v_theta)

  def item_spawn_object(self, item:SpawnItem):
    model = self.loader.loadModel(MO_CUBE)
    itemNP = model.copyTo(self.itemsNP)
    itemNP.setTextureOff()
    itemNP.setColor(1, 1, 0.8)
    itemNP.setScale(0.03)
    loc = v_i2f(item['loc'])
    rot = Vec2(*loc)
    pos = rot_to_pos(rot) * self.radius
    itemNP.setPos(pos)
    self.itemNPs.append([item, itemNP])

  def item_vanish_object(self, ts:int):
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

  def update_latency(self, server_ts:int):
    self.last_server_ts = server_ts
    self.vwin_latency.add(now_ts() - server_ts)

  def reset_photon_slider_range(self, lim:int):
    self.sldPhoton['range'] = (1, lim)
  
  def reset_item_button_count(self, name:str, cnt:int):
    self.txtItems[name].setText(str(cnt))

  def anim_error(self, err:str):
    self.txtError.setText(err)
    Sequence(
      LerpColorScaleInterval(self.txtError, duration=0.2, colorScale=ALPHA_1),
      LerpColorScaleInterval(self.txtError, duration=1.7, colorScale=ALPHA_1),
      LerpColorScaleInterval(self.txtError, duration=0.2, colorScale=ALPHA_0),
    ).start()

  def anim_item(self, name:str):
    name = GATE_NAME_MAPPING_INV.get(name, name)
    btn = self.btnItems[name]
    anim_button(btn).start()

  ''' handlers '''

  def on_connect(self):
    self.is_connected = True
    print('>> connected')

  def on_disconnect(self):
    self.is_connected = False
    print('>> disconnect')

  @unpack_data
  def on_game_join(self, data:Data):
    from modules.scenes.title_scene import TitleScene
    title_scene: TitleScene = self.ui.get_scene('Title')
    title_scene.txtInfo.setText('wait for another player...')

  @unpack_data
  def on_game_start(self, data:Data):
    self._game_sync(data)
    self.start_threads()

    self.txtRole.setText(self.me)
    if self.me == ALICE:
      self.txtRole.setFg(Vec4(0.7, 0.7, 1, 1))
    else:
      self.txtRole.setFg(Vec4(1, 0.7, 0.7, 1))
    self.txtState.setText(phi_str(self.phi))

    player = self.player
    for name, txt in self.txtItems.items():
      if name == 'photon':
        self.reset_item_button_count(name, player.photons)
        self.reset_photon_slider_range(player.photons)
      elif name == 'theta':
        self.reset_item_button_count(name, player.thetas)
      else:
        server_name = GATE_NAME_MAPPING.get(name, name)
        self.reset_item_button_count(name, player.gates.get(server_name, 0))

    self.ui.switch_scene('Main')

  @unpack_data
  def on_game_settle(self, data:Data):
    winner = data['winner']
    endTs = data['endTs']
    self.anim_error(f'winner: {winner}')
    
    self.stop_threads()

    self.game = None
    self.sio.disconnect()
    #self.ui.switch_scene('Title')

  @unpack_data
  def on_game_sync(self, data:Data):
    self._game_sync(data)

  @unpack_data
  def on_game_ping(self, data:Data):
    pass

  @unpack_data
  def on_mov_start(self, data:Data):
    id = data['id']
    player = self.game.players[id]
    player.dir = data['dir']
    if 'spd' in data:
      player.spd = data['spd']
    self.is_moving[id] = True

  @unpack_data
  def on_mov_stop(self, data:Data):
    for id, loc in data.items():
      player = self.game.players[id]
      player.dir = None
      player.loc = [(x + y) / 2 for x, y in zip(loc, player.loc)]   # sync fix
      self.is_moving[id] = False

  @unpack_data
  def on_loc_sync(self, data:Data):
    self._loc_sync(data)

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
    'nothing, see item:gain'

  @unpack_data
  def on_item_gain(self, item:Data):
    player = self.player
    item_type = ItemType(item['type'])
    item_id = item['id']
    server_name = GATE_NAME_MAPPING_INV.get(item_id, item_id)
    self.anim_item(server_name)
    if item_type == ItemType.PHOTON:
      player.photons += item['count']
      self.reset_item_button_count(server_name, player.photons)
      self.reset_photon_slider_range(player.photons)
    elif item_type == ItemType.THETA:
      player.thetas += item['count']
      self.reset_item_button_count(server_name, player.thetas)
    else:
      if item_id in player.gates:
        player.gates[item_id] += item['count']
      else:
        player.gates[item_id] = item['count']
      self.reset_item_button_count(server_name, player.gates[item_id])

  @unpack_data
  def on_item_cost(self, item:Data):
    player = self.player
    item_type = ItemType(item['type'])
    item_id = item['id']
    server_name = GATE_NAME_MAPPING_INV.get(item_id, item_id)
    if item_type == ItemType.PHOTON:
      player.photons -= item['count']
      self.reset_item_button_count(server_name, player.photons)
      self.reset_photon_slider_range(player.photons)
    elif item_type == ItemType.THETA:
      player.thetas -= item['count']
      self.reset_item_button_count(server_name, player.thetas)
    else:
      player.gates[item_id] -= item['count']
      self.reset_item_button_count(server_name, player.gates.get(item_id, 0))

  @unpack_data
  def on_gate_rot(self, data:Data):
    if 'state' in data:
      self._state_sync(data['state'])
    else:
      self._loc_sync(data)

  @unpack_data
  def on_gate_swap(self, data:Data):
    if 'state' in data:
      self._state_sync(data['state'])
    else:
      self._loc_sync(data)

  @unpack_data
  def on_gate_cnot(self, data:Data):
    if 'state' in data:
      self._state_sync(data['state'])
    else:
      self._loc_sync(data)

  @unpack_data
  def on_gate_meas(self, data:Data):
    self._loc_sync(data)

  @unpack_data
  def on_entgl_enter(self, data:Data):
    self.is_entangled = True
    for player in self.game.players.values():
      player.dir = None
    for qubitNP in self.qubitNPs.values():
      qubitNP.hide()

  @unpack_data
  def on_entgl_break(self, data:Data):
    self.is_entangled = False
    self.emit_loc_sync()
    for qubitNP in self.qubitNPs.values():
      qubitNP.show()

  def _game_sync(self, data:Data):
    self.game = Game.from_dict(data)

  def _loc_sync(self, data:Data):
    for id, loc in data.items():
      self.game.players[id].loc = loc

  def _state_sync(self, data:Data):
    state = v_i2f(data)
    entgl_state = [complex(state[2*i], state[2*i+1]) for i in range(len(state)//2)]
    self.entgl_phi = entgl_state

  ''' emitters '''

  @show_emit
  def emit_game_join(self, room:str, r:int):
    if self.join_info == (room, r): return
    print(f'>> room: {room}, r: {r}')
    self.join_info = (room, r)

    if not self.is_connected:
      self.connect_server()
    self.sio.emit('game:join', {
      'rid': room, 
      'r': r,
    })

  @show_emit
  def emit_game_sync(self):
    self.sio.emit('game:sync', {})

  @show_emit
  def emit_game_ping(self):
    self.sio.emit('game:ping', {})

  @no_entgl
  @show_emit
  def emit_item_pick(self, ts:int):
    self.sio.emit('item:pick', {
      'ts': ts,
    })

  @no_entgl
  @show_emit
  def emit_mov_start(self, dir:int):
    self.sio.emit('mov:start', {
      'dir': dir,
    })

  @no_entgl
  @show_emit
  def emit_mov_stop(self):
    self.sio.emit('mov:stop', {})

  @no_entgl
  @show_emit
  def emit_loc_query(self, cnt:int):
    self.sio.emit('loc:query', {
      'photons': cnt,
      'basis': 'Z',   # only Z supported
    })

  @no_entgl
  @show_emit
  def emit_loc_sync(self):
    self.sio.emit('loc:sync', {})

  @show_emit
  def emit_gate_rot(self, gate:str, theta:float=None):
    self.sio.emit('gate:rot', {
      'gate': gate,
      'theta': theta,
    })

  @show_emit
  def emit_gate_swap(self):
    self.sio.emit('gate:swap', {})

  @show_emit
  def emit_gate_cnot(self):
    self.sio.emit('gate:cnot', {})

  @show_emit
  def emit_gate_meas(self):
    self.sio.emit('gate:meas', {})

  ''' workers '''

  def start_threads(self):
    self.is_quit.clear()
    self.thrs.extend([
      make_sched_task(self.is_quit, HEART_BEAT, self.task_heartbeat, cond=self.task_heartbeat_cond),
      make_sched_task(self.is_quit, 3, self.task_update_latency_meter),
      make_sched_task(self.is_quit, 1/FPS, self.task_update_qubit_loc, cond=self.task_update_qubit_loc_cond),
      make_sched_task(self.is_quit, 2/FPS, self.task_update_state),
    ])
    for thr in self.thrs:
      thr.start()

  def stop_threads(self):
    self.is_quit.set()
    for thr in self.thrs:
      thr.join()
    self.thrs.clear()

  def task_heartbeat(self):
    self.emit_game_ping()

  def task_heartbeat_cond(self) -> bool:
    return now_ts() - self.last_server_ts > HEART_BEAT

  def task_update_latency_meter(self):
    latentcy: float = self.vwin_latency.mean
    self.txtLatentcy.setText(f'{latentcy:.1f} ms')

    # ref: https://zhidao.baidu.com/question/372038117473759972.html
    if latentcy <= 30:
      self.txtLatentcy['fg'] = GREEN
    elif latentcy <= 50:
      self.txtLatentcy['fg'] = LIME
    elif latentcy <= 100:
      self.txtLatentcy['fg'] = YELLOW
    elif latentcy <= 200:
      self.txtLatentcy['fg'] = ORANGE
    else:
      self.txtLatentcy['fg'] = RED

  def task_update_state(self):
    if self.is_entangled:
      state_str = entgl_phi_str(self.entgl_phi)
    else:
      state_str = phi_str(self.phi)
    self.txtState.setText(state_str)

  def task_update_qubit_loc(self):
    # update data
    game = self.game
    task_sim_loc(game)
    # update draw
    for role, qubit in self.qubitNPs.items():
      loc = v_i2f(game.players[role].loc)
      rot = Vec2(*loc)
      pos = rot_to_pos(rot) * self.radius
      qubit.setPos(pos)
    # dist
    alice = loc_to_phi(v_i2f(game.players[ALICE].loc))
    bob   = loc_to_phi(v_i2f(game.players[BOB]  .loc))
    fid = phi_fidelity(alice, bob)
    qubitRival = self.qubitNPs[get_rival(game.me)]
    if fid >= VISIBLE_FID:
      qubitRival.setAlphaScale((fid - VISIBLE_FID) / (1 - VISIBLE_FID))
    else:
      qubitRival.setAlphaScale(0)

  def task_update_qubit_loc_cond(self) -> bool:
    return not self.is_entangled
