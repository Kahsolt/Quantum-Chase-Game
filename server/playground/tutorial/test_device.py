#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import LocalDevice, QcisDevice, AwsDevice

isq_str = '''
  qbit a, b;
  X(a);
  CNOT(a, b);
  M(a);
  M(b);
'''

# local device
ld = LocalDevice(shots=200)
# 返回dict
ld_res = ld.run(isq_str)
print(ld_res)


# qcis device
qd = QcisDevice(user='20021230', passwd='021230', max_wait_time=60)
# 返回 ISQTask
task = qd.run(isq_str)
# 输出状态和结果
print(task.state)
print(task.result())


# aws device
import logging
logger = logging.getLogger()    # initialize logging class
logger.setLevel(logging.CRITICAL)
from isq import TaskState
ad = AwsDevice(shots=100, device_arn='arn:aws:braket:::device/qpu/ionq/ionQdevice', s3=('amazon-braket-arclight', 'simulate'), max_wait_time=10, logger=logger)
task = ad.run(isq_str)
print(task.state)
# 等待结果直到执行完成
while task.state == TaskState.WAIT:
  task.result()
print(task.result())
