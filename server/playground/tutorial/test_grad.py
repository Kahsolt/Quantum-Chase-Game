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

def calc(params):
  # 使用probs函数进行带参编译和模拟，其中需要微分的参数通过optv封装后传入
  c = ld.probs(isq_str, theta=optv(params))
  return c[0] - c[1]

# 定义grad，并调用，对第0个参数求微分
g = isq.grad(calc, [0])
d = g([0.2, 0.4])
print(d)


from jax import grad, vmap
from jax import numpy as jnp

def calc(params):
  # 使用probs函数进行带参编译和模拟，其中需要优化的参数通过optv封装后传入，mod值为1，使用jax.numpy计算
  c = ld.probs(isq_str, mod=1, theta=optv(params))
  return c[0] - c[1]

g = grad(calc)
c = vmap(g)   # vmap批处理，以第0轴索引，输出每个划分的微分结果。该例子中即为以行为划分，输出10个结果
theta = jnp.array([[0.2, 0.4] for _ in range(10)])
d = c(theta)
print(d)
