#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/24

from modules.xvqe import *
from services.packets import *


''' handlers & emitters '''

def handle_vqe_ham(payload:Payload, g:Game) -> HandlerRet:
  # TODO: what
  return resp_ok(payload), Recp.ROOM


def handle_vqe_solve(payload:Payload, g:Game) -> HandlerRet:
  # TODO: what
  return resp_ok(payload), Recp.ROOM


def emit_vqe_phase():
  # TODO: what
  pass
