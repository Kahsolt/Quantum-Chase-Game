#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from copy import deepcopy

from flask_socketio import join_room, leave_room

from modules.qbloch import rand_loc, loc2phi, phi_fidelity
from modules.xcoin import toss_coin
from modules.xrand import random_bit
from services.handler import *
from services.tasks import run_sched_task, run_randu_sched_task
from services.domains.mov import task_mov_sim
from services.domains.item import task_item_spawn


''' handlers & emitters '''

def handle_game_join(payload:Payload, env:Env) -> HandlerRet:
  try:
    check_payload(payload, [('rid', str), ('r', int)])
    assert payload['r'] in [0, 1], '`r` must in [0, 1]'
  except Exception as e: return resp_error(e.args[0])

  _rid: str = payload['rid']
  _r:   int = payload['r']

  if _rid in env.games: return resp_error('room is occupied in gaming')
  sid = request.sid
  rid = env.conns.get(sid)
  if rid in env.games: return resp_error('player already in gaming')

  # leave the room for changing if already in waiting: waiting => standby
  if rid in env.waits and rid != _rid:
    del env.waits[rid]
    env.conns[sid] = None

  # standby => waiting
  env.conns[sid] = _rid
  if _rid not in env.waits:
    env.waits[_rid] = {}
  # stash init stuff
  env.waits[_rid][sid] = _r

  # when two players meet, start the game!
  if len(env.waits[_rid]) == 2:
    emit_game_start(env, _rid)

  # NOTE: this might be later than emit `game:start`
  return resp_ok()


def handle_game_sync(payload:Payload, rt:Runtime) -> HandlerRet:
  id, player, g = x_rt(rt)
  pstate = make_pstate(g, id)
  return resp_ok(pstate)


def handle_game_ping(payload:Payload, rt:Runtime) -> HandlerRet:
  return resp_ok()


def emit_game_start(env:Env, rid:str):
  if rid not in env.waits: return
  if rid in env.games: return

  # run Q-coin-flip to decide Alice & Bob role
  (sid_a, id_a), (sid_b, id_b) = decide_role(env.waits[rid])

  # init global game state
  init_photon = 1000
  init_theta = 99
  init_gate = { g: 99 for g in ROT_GATES + P_ROT_GATES }
  init_gate.update({
    'H':    99,
    'M':    99,
    'CNOT': 99,
    'SWAP': 99,
  })
  g = Game(
    rid=rid,
    me={
      sid_a: id_a,
      sid_b: id_b,
    },
    players={
      ALICE: Player(spd=v_f2i(MOVE_SPEED), loc=[v_f2i(e) for e in rand_loc()], photons=init_photon, thetas=init_theta, gates=deepcopy(init_gate)),
      BOB:   Player(spd=v_f2i(MOVE_SPEED), loc=[v_f2i(e) for e in rand_loc()], photons=init_photon, thetas=init_theta, gates=deepcopy(init_gate)),
    },
    startTs=now_ts(),
  )
  rt = Runtime(env, g)
  env.games[rid] = rt
  run_sched_task(rt.signal, 1/FPS, task_mov_sim, rt, cond=(lambda: not rt.is_entangled()))
  run_sched_task(rt.signal, 1/FPS, task_game_over, rt)
  run_randu_sched_task(rt.signal, [SPAWN_INTERVAL/2, SPAWN_INTERVAL*2], task_item_spawn, rt)

  # distribute partial data
  env.sio.emit('game:start', resp_ok(make_pstate(g, me=id_a).to_dict()), to=sid_a)
  env.sio.emit('game:start', resp_ok(make_pstate(g, me=id_b).to_dict()), to=sid_b)

  # move waiting => playing
  for sid in env.waits[rid]:
    join_room(rid, sid)
  del env.waits[rid]


def emit_game_settle(rt:Runtime, winner:str):
  # stop all thread workers
  rt.signal.set()

  endTs = now_ts()
  g = rt.game
  g.winner = winner
  g.endTs = endTs
  data = {
    'winner': winner,
    'endTs': endTs,
  }
  rt.sio.emit('game:settle', resp_ok(data), to=rt.rid)

  # move playing => standby
  for sid in g.me:
    try:
      leave_room(rt.rid, sid)
      rt.env.conns[sid] = None
    except:
      pass


''' utils '''

def decide_role(init_stuff:Dict[str, int]):
  # players' bit
  sid_a, sid_b = list(init_stuff.keys())
  bit_a, bit_b = init_stuff[sid_a], init_stuff[sid_b]
  # assume the basis is chosen by Charlie
  bas = random_bit()
  # the fair-coin
  r = toss_coin((bit_a, bas), bit_b)
  # whether swap role
  id_a, id_b = ALICE, BOB
  if r == 1: id_a, id_b = id_b, id_a
  return (sid_a, id_a), (sid_b, id_b)


def make_pstate(g:Game, me:str) -> Game:
  ret = deepcopy(g)
  ret.me = me
  return ret


''' task '''

def task_game_over(rt:Runtime):
  if now_ts() - rt.game.startTs > TIME_LIMIT * 10**3:
    emit_game_settle(rt, ALICE)

  players = rt.game.players
  fid = phi_fidelity(
    loc2phi(v_i2f(players[ALICE].loc)),
    loc2phi(v_i2f(players[BOB]  .loc)),
  )
  if fid >= CATCH_FID:
    emit_game_settle(rt, BOB)
