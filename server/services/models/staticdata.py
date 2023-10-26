#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/20

from numpy import pi

# 角色名
ALICE = 'Alice'
BOB = 'Bob'

# 角色移动角速度: 假设 60s 转一圈
MOVE_SPEED = 2 * pi / 60

# 角色拾取范围
PICK_RADIUS = MOVE_SPEED * 2

# 物品生成速度
SPAWN_INTERVAL = 15

# 物品生成数量上限
SPAWN_LIMIT = 30

# 物品生成的份数期望
SPAWN_COUNT = 2.25

# 物品存活时间期望中心
SPAWN_TTL = 90

# 使用量子门所消耗代币
GATE_COST = {
  'H': 10,
  'X': 10,
  'Y': 10,
  'Z': 10,
  'RX': 20,
  'RY': 20,
  'RZ': 20,
  'CNOT': 50,
  'SWAP': 150,
}

# 门操作计算噪声
ENV_NOISE = 0.0
