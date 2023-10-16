#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/16

from flask import Blueprint, redirect, render_template

from services.utils import *

app = Blueprint('doc', __name__)


@app.route('/')
def index():
  return redirect('/api')

@app.route('/api')
def api():
  API_PATH = HTML_PATH / 'api'
  pages = [fp.stem for fp in API_PATH.iterdir() if fp.suffix == '.html' and not fp.stem.startswith('_')]
  return render_template('api.html', pages=pages)

@app.route('/api/<page>')
def api_(page:str):
  return render_template(f'api/{page}.html')


@app.route('/doc')
def doc():
  return render_template('doc.html')


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
