"""
MessageQueue contains two thread safe queues - a send and a receive queue
These queues are used to share data between the logical node modules
and the network comm modules
"""

from queue import Queue

from raft.message.Message import Message

_recv_queue: Queue = Queue()

def recv_enqueue(item):
  _recv_queue.put(item)

def recv_dequeue() -> Message:
  return _recv_queue.get()

def recv_empty() -> bool:
  return _recv_queue.empty()

def recv_qsize() -> int:
  return _recv_queue.qsize()

def _recv_clear():
  with _recv_queue.mutex:
    _recv_queue.queue.clear()

