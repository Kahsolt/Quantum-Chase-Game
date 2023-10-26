#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from flask_socketio import emit
from flask_socketio import join_room, leave_room

from modules.qbloch import rand_loc
from modules.xcoin import toss_coin
from modules.xrand import random_bit
from services.movloc import task_sim_loc
from services.utils import *


def handle_game_join(payload:Payload, env:Env) -> HandlerRet:
  try:
    check_payload(payload, [('rid', str), ('r', int)])
    assert payload['r'] in [0, 1], '`r` must in [0, 1]'
  except Exception as e: return resp_error(e.args[0])

  _rid: str = payload['rid']
  _r:   int = payload['r']

  if payload['rid'] in env.games:   # room in use
    return resp_error('room is occupied in gaming')

  sid = request.sid
  rid = env.conns.get(sid)
  if rid in env.games:        # in gaming
    return resp_error('player already in gaming')

  # leave the room for changing: waiting => standby
  if rid in env.waits and rid != _rid: #   in waiting
    del env.waits[rid]
    env.conns[sid] = None

  # standby => waiting
  env.conns[sid] = _rid
  if _rid not in env.waits:
    env.waits[_rid] = {}
  env.waits[_rid][sid] = _r     # init stuff

  # two players meet, let's start the game
  if len(env.waits[_rid]) == 2:
    emit_game_start(env, _rid)

  # this is delayed, but no bother
  return resp_ok(), Recp.ONE


def handle_game_sync(payload:Payload, g:Game) -> HandlerRet:
  id, player = get_me(g)

  return resp_ok(player), Recp.ONE


def emit_game_start(env:Env, rid:str):
  if rid not in env.waits: return
  if rid in env.games: return

  # run Q-coin to decide final Alice & Bob role
  id_a, id_b = ALICE, BOB             # init role
  init_stuff = env.waits[rid]
  sid_a, sid_b = list(init_stuff.keys())
  bit_a, bit_b = init_stuff[sid_a], init_stuff[sid_b]
  bas = random_bit()                  # assume the basis is chosen by Charlie
  r = toss_coin((bit_a, bas), bit_b)
  if r == 1: id_a, id_b = id_b, id_a  # swap role

  # init global game status
  g = Game(
    me={
      sid_a: id_a,
      sid_b: id_b,
    },
    players={
      ALICE: Player(spd=v_f2i(MOVE_SPEED), loc=[v_f2i(e) for e in rand_loc()]),
      BOB:   Player(spd=v_f2i(MOVE_SPEED), loc=[v_f2i(e) for e in rand_loc()]),
    },
    status=Status(
      startTs=now_ts(),
      stage=1,
    ),
    const=Const(
      cost=GATE_COST,
      noise=ENV_NOISE,
    ),
  )
  is_stop = Event()
  env.signals[rid] = is_stop
  run_sched_task(is_stop, 1/FPS, task_sim_loc, g)

  # distribute partial data
  emit('game:start', resp_ok(make_pstate(g, me=id_a).to_dict()), to=sid_a)
  emit('game:start', resp_ok(make_pstate(g, me=id_b).to_dict()), to=sid_b)

  # move waiting => playing, track game state
  for sid in env.waits[rid]:
    join_room(rid, sid)
  del env.waits[rid]
  env.games[rid] = g


def emit_game_settle(env:Env, rid:str, winner:str):
  if rid not in env.games: return

  # stop sim
  env.signals[rid].set()
  del env.signals[rid]

  endTs = now_ts()
  g = env.games[rid]
  g.status.winner = winner
  g.status.endTs = endTs
  data = {
    'winner': winner,
    'endTs': endTs,
  }
  emit('game:settle', resp_ok(data), to=rid)

  # move playing => standby
  for sid in env.games[rid]:
    leave_room(rid, sid)
    env.conns[sid] = None


''' utils '''

def make_pstate(g:Game, me:str):
  ret = deepcopy(g)
  ret.me = me
  for id, player in g.players.items():
    if id != me:
      player.bag = None
  return ret
