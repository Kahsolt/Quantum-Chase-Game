#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from typing import List, Tuple, Union

from panda3d.core import Vec4
from panda3d.core import TransparencyAttrib
from panda3d.core import NodePath
from panda3d.core import Texture
from panda3d.core import LineSegs
from direct.showbase.Loader import Loader
from direct.motiontrail.MotionTrail import MotionTrail
from direct.interval.LerpInterval import LerpNodePathInterval
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval, LerpScaleInterval, LerpTexOffsetInterval
from direct.interval.LerpInterval import LerpColorInterval, LerpColorScaleInterval
from direct.interval.IntervalGlobal import Sequence, Parallel

Objects = List[NodePath]
Anim = Union[LerpNodePathInterval, Sequence, Parallel]
Anims = List[Anim]

Prefab = Tuple[Objects, Anims]

BLACK   = Vec4(0, 0, 0, 1)
WHITE   = Vec4(1, 1, 1, 1)
RED     = Vec4(1, 0, 0, 1)
GREEN   = Vec4(0, 1, 0, 1)
BLUE    = Vec4(0, 0, 1, 1)
LIME    = Vec4(0.75, 1, 0, 1)
YELLOW  = Vec4(1, 1, 0, 1)
ORANGE  = Vec4(1, 0.5, 0, 1)

ALPHA_0 = Vec4(1, 1, 1, 0)
ALPHA_1 = Vec4(1, 1, 1, 1)
