#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from flask import Blueprint, render_template

from services.utils import *

app = Blueprint('doc', __name__)


@app.route('/')
@app.route('/api')
def api():
  return render_template('api.html')


@app.route('/data')
def data():
  return render_template('data.html')


@app.route('/ws')
def ws():
  return render_template('ws.html')


@app.route('/info')
def info():
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
