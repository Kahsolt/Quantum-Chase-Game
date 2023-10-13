#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

from flask import Flask, request, Response
from flask import redirect, jsonify

from modules import *

BASE_PATH = Path(__file__).parent.absolute()
PORT = os.environ.get('PORT', 5000)

app = Flask(__name__)


@app.route('/')
def index():
  apis = [k[len('api_'):] for k, v in globals().items() if k.startswith('api_') and isinstance(v, Callable)]
  return jsonify(apis)


@app.route('/init')
def api_init():
  pass


@app.route('/info')
def api_info():
  loadavg, (rss, vms, mem_usage) = mem_info()

  return f'''
<div>
  <p>pwd: {os.getcwd()}</p>
  <p>BASE_PATH: {BASE_PATH}</p>
  <p>loadavg: {loadavg}</p>
  <p>mem use: {rss:.3f} MB</p>
  <p>mem vms: {vms:.3f} MB</p>
  <p>mem percent: {mem_usage} %</p>
</div>
'''


if __name__ == '__main__':
  try:
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
