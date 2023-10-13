#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsg
from pprint import pformat as pf
from traceback import print_exc, format_exc

from isq import *

WINDOW_TITLE = 'isQ-open Code Runner'
WINDOW_SIZE  = (600, 450)
TX_LINES_IN  = 24
TX_LINES_OUT = 4

DEFAULT_PROGRAM = '''
qbit q[2];
H(q[0]);
CNOT(q[0], q[1]);
M(q[0:2]);
'''.strip()


class App:

  def __init__(self):
    self.qvm = LocalDevice(shots=1000)

    self.setup_gui()
    self.tx_input.insert('0.0', DEFAULT_PROGRAM)

    try:
      self.wnd.mainloop()
    except KeyboardInterrupt:
      self.wnd.destroy()
    except: print_exc()

  def setup_gui(self):
    # window
    wnd = tk.Tk()
    W, H = wnd.winfo_screenwidth(), wnd.winfo_screenheight()
    w, h = WINDOW_SIZE
    wnd.geometry(f'{w}x{h}+{(W-w)//2}+{(H-h)//2}')
    wnd.resizable(False, False)
    wnd.title(WINDOW_TITLE)
    wnd.protocol('WM_DELETE_WINDOW', wnd.quit)
    self.wnd = wnd

    # top: input / output
    frm1 = ttk.Frame(wnd)
    frm1.pack(expand=tk.YES, fill=tk.BOTH)
    if True:
      frm11 = ttk.LabelFrame(frm1, text='Input')
      frm11.pack(expand=tk.YES, fill=tk.BOTH)
      if True:
        tx = tk.Text(frm11, height=TX_LINES_IN)
        tx.pack(expand=tk.YES, fill=tk.BOTH)
        self.tx_input = tx

      frm21 = ttk.LabelFrame(frm1, text='Output')
      frm21.pack(expand=tk.YES, fill=tk.BOTH)
      if True:
        tx = tk.Text(frm21, height=TX_LINES_OUT)
        tx.pack(expand=tk.YES, fill=tk.BOTH)
        self.tx_output = tx

    # bottom: button
    frm2 = ttk.Frame(wnd)
    frm2.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
    if True:
      btn = tk.Button(text='Run!', fg='red', command=self.run)
      btn.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X, padx=16)

  def run(self):
    isq_str = self.tx_input.get('0.0', tk.END).strip()
    if not isq_str: return

    try:
      res = self.qvm.run(isq_str)
    except:
      tkmsg.showerror('Error', format_exc())
      return

    self.tx_output.delete('0.0', tk.END)
    self.tx_output.insert('0.0', pf(res))


if __name__ == '__main__':
  try:
    App()
  except KeyboardInterrupt:
    print('Exit by Ctrl+C')
  except:
    print_exc()
