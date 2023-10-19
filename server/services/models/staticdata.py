#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/20

from math import pi

# 角色名
ALICE = 'Alice'
BOB = 'Bob'

# 角色移动角速度: 假设 60s 转一圈
MOVE_SPEED = 2 * pi / 60

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
