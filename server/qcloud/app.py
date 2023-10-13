#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

import os
import json
import psutil
from pathlib import Path
from traceback import print_exc
from typing import *

from flask import Flask, request
from flask import jsonify

BASE_PATH = Path(__file__).parent.absolute()
PORT = os.environ.get('PORT', 5001)
TMP_ISQ_FILE = 'tmp.isq'

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run():
  params: Dict[str, Any] = request.json
  isq = params.get('isq', '')
  shots = params.get('shots', 1000)

  with open(TMP_ISQ_FILE, 'w', encoding='utf-8') as fh:
    fh.write(isq)

  ret = os.popen(f'isqc run {TMP_ISQ_FILE} --shots {shots}').read()
  try:
    res = json.loads(ret)
    return jsonify({'ok': True, 'data': res})
  except:
    return jsonify({'ok': False, 'error': ret})


@app.route('/info', methods=['GET'])
def info():
  import gc ; gc.collect()
  pid = os.getpid()
  loadavg = psutil.getloadavg()
  p = psutil.Process(pid)
  meminfo = p.memory_full_info()

  isqc_ver = os.popen('isqc -V').read()

  return f'''
<div>
  <p>isqc version: {isqc_ver}</p>
  <p>pwd: {os.getcwd()}</p>
  <p>BASE_PATH: {BASE_PATH}</p>
  <p>loadavg: {loadavg}</p>
  <p>mem use: {meminfo.rss / 2**20:.3f} MB</p>
  <p>mem vms: {meminfo.vms / 2**20:.3f} MB</p>
  <p>mem percent: {p.memory_percent()} %</p>
</div>
'''


if __name__ == '__main__':
  try:
    app.run(host='0.0.0.0', port=PORT, threaded=False, debug=False)
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
