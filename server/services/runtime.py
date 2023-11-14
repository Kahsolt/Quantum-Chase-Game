#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from threading import Event
from dataclasses import dataclass, field

from flask_socketio import SocketIO

from modules.qcircuit import Operation
from services.shared import *
from services.utils import *


@dataclass
class Runtime:
  # backref
  env: 'Env'
  # playerdata (serializable)
  game: Game
  # the stop signal for all thread workers of this Game
  signal: Event = field(default_factory=Event)
  # item spawns: ts => spawn
  spawns: Dict[int, SpawnItem] = field(default_factory=dict)
  # entgl_circuit: each op on the circuit
  circuit: List[Operation] = field(default_factory=list)
  # entgl_ttl
  entgl_ttl: float = None
  # env noise
  noise: float = 0.0

  @property
  def sio(self): return self.env.sio

  @property
  def rid(self): return self.game.rid

  def is_entangled(self): return len(self.circuit) > 0


@dataclass
class Env:
  # ctx
  sio: SocketIO
  # sid => rid|None
  conns: Dict[str, Optional[str]] = field(default_factory=dict)
  # rid => sid => r:int
  waits: Dict[str, Dict[str, int]] = field(default_factory=dict)
  # rid => rt
  games: Dict[str, Runtime] = field(default_factory=dict)
