"""
MessageQueue contains two thread safe queues - a send and a receive queue
These queues are used to share data between the logical node modules
and the network comm modules
"""

from queue import Queue

_recv_queue: Queue = Queue()
_send_queue: Queue = Queue()

def recv_enqueue(item):
  _recv_queue.put(item)

def recv_dequeue():
  return _recv_queue.get()

def recv_empty():
  return _recv_queue.empty()

def recv_qsize():
  return _recv_queue.qsize()

def send_enqueue(item):
  _send_queue.put(item)

def send_dequeue():
  return _send_queue.get()

def send_empty():
  return _send_queue.empty()

def send_qsize():
  return _send_queue.qsize()

