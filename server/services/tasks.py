#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

from time import sleep
from threading import Thread, Event
from typing import Tuple, Callable

from services.rand import random_gaussian_expect, random_uniform_expect


def null_decorator(fn):
  def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
  return wrapper

dead_loop = null_decorator


def run_sched_task(is_quit:Event, interval:float, func:Callable, func_args:tuple=()):
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      sleep(interval)
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()


def run_randn_sched_task(is_quit:Event, expect:float, func:Callable, func_args:tuple=()):
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      interval = random_gaussian_expect(expect, vmin=3) 
      sleep(interval)
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()


def run_randu_sched_task(is_quit:Event, vrng:Tuple[float, float], func:Callable, func_args:tuple=()):
  @dead_loop
  def wrapped_task():
    print(f'>> task {func.__name__} started')
    while not is_quit.is_set():
      interval = random_uniform_expect(*vrng) 
      sleep(interval)
      Thread(target=func, args=func_args, daemon=True).start()
    print(f'>> task {func.__name__} stopped')

  if not isinstance(func_args, tuple): func_args = (func_args,)
  Thread(target=wrapped_task, daemon=True).start()
