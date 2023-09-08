#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

import isq
from isq import LocalDevice, optv

isq_str = '''
  qbit q[2];
  RX(theta[0], q[0]);
  RY(theta[1], q[1]);
  M(q[0]);
'''

ld = LocalDevice()

def loss(params):
  # 使用probs函数进行带参编译和模拟，其中需要优化的参数通过optv封装后传入
  c = ld.probs(isq_str, theta=optv(params))
  return c[0] - c[1]

# 定义optimizer
opt = isq.optimizer(0.1)
# 获取优化后参数及当次损失函数计算值
newp = [0.2, 0.4]
for _ in range(1000):
  newp, cost = opt.opt(loss, newp)
  print(newp, cost)
