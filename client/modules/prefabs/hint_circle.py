#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from direct.task.Task import Task, TaskManager

from modules.assets import *
from modules.shared import LOC_QUERY_TTL
from modules.ui_configs import *
from modules.utils import *

from .utils import *


def hint_circle_show(taskMgr:TaskManager, parent:NodePath, R:float, z:float):
  R                         # 大圆半径
  Z = z * R                 # 小圆纬度
  r = (R**2 - Z**2) ** 0.5  # 小圆半径

  n_div = 180
  tht = pi * 2 / n_div
  X = r * cos(0)
  Y = r * sin(0)

  lines = LineSegs()
  lines.setColor(1.0, 1.0, 0.7)
  lines.moveTo(X, Y, Z)
  for i in range(n_div):
    X = r * cos(i * tht)
    Y = r * sin(i * tht)
    lines.drawTo(X, Y, Z)
  lines.setThickness(4)
  hintNP = NodePath(lines.create())
  hintNP.setTextureOff()
  hintNP.reparentTo(parent)
  LerpColorScaleInterval(hintNP, duration=0.5, colorScale=ALPHA_1, startColorScale=ALPHA_0, blendType=IN_OUT).start()

  def removeNodeTask(task):
    nonlocal hintNP
    hintNP.removeNode()
    return Task.done

  taskMgr.doMethodLater(LOC_QUERY_TTL, removeNodeTask, 'loc_hint')
