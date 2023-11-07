#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from typing import List, Tuple, Union

from panda3d.core import Vec4
from panda3d.core import TransparencyAttrib
from panda3d.core import NodePath, LineSegs
from panda3d.core import Texture
from direct.showbase.Loader import Loader
from direct.motiontrail.MotionTrail import MotionTrail
from direct.interval.LerpInterval import LerpNodePathInterval, LerpPosInterval, LerpHprInterval, LerpScaleInterval, LerpTexOffsetInterval, LerpColorInterval, LerpColorScaleInterval
from direct.interval.IntervalGlobal import Sequence, Parallel

Objects = List[NodePath]
Anim = Union[LerpNodePathInterval, Sequence]
Anims = List[Anim]

Prefab = Tuple[Objects, Anims]
