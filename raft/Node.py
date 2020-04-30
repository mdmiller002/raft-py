"""
Node.py contains a Node class that implements the raft logic
Node is the top layer level in the system
"""

from enum import Enum
import random
import time

from raft.NodeMetadata import NodeMetadata
from raft.message import MessageQueue
from raft.message.Message import MessageType, Message
from raft.LoggingHelper import get_logger
from raft.network import NetworkUtil

LOG = get_logger(__name__)

class NodeState(Enum):
  FOLLOWER = 1
  CANDIDATE = 2
  LEADER = 3

class Node:

  def __init__(self, nodes_list):
    self._state = NodeState.FOLLOWER
    self._election_timeout = None
    self._current_term = 0
    self._current_leader = None
    self._nodes = nodes_list
    self._cluster_size = len(nodes_list)
    self._port = None
    self._ip_address = NetworkUtil.get_localhost_ip_addr()

  def run(self):
    """run this node's raft algorithm forever"""
    while True:
      self._process_node()

  def _process_node(self):
    if self._state == NodeState.FOLLOWER:
      self._process_follower()
    elif self._state == NodeState.CANDIDATE:
      self._process_candidate()
    elif self._state == NodeState.LEADER:
      self._process_leader()

  def _process_follower(self):
    LOG.info("Node entering FOLLOWER state")
    self._election_timeout = random.randint(150, 301)
    LOG.info("Election timeout generated: {}ms".format(self._election_timeout))

    start = time.time()
    while self._not_timed_out(start):
      if not MessageQueue.recv_empty():
        msg = MessageQueue.recv_dequeue()
        LOG.info("Received a message...")
        if msg.get_sender() == self._current_leader and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received heartbeat from leader, remaining in follower state")
          return
      time.sleep(10 / 1000)
    LOG.info("Election timeout reached, entering candidate state")
    self._state = NodeState.CANDIDATE

  def _not_timed_out(self, start):
    return (time.time() - start) * 1000 < self._election_timeout

  def _process_candidate(self):
    LOG.info("Node entering CANDIDATE STATE")
    sender = self._get_node_metadata()
    message = Message(sender, MessageType.VOTE_REQUEST)
    MessageQueue.send_enqueue(message)

    while True:
      while MessageQueue.recv_empty():
        pass
      msg = MessageQueue.recv_dequeue()
      if msg.get_sender() not in self._nodes:
        LOG.info("Received message from {}:{}, not in nodes list".format(
          msg.get_sender().get_host(), msg.get_sender().get_port()))
        continue
      voted_for_me = []
      if msg.get_type() == MessageType.VOTE_RESPONSE and msg.get_sender not in voted_for_me:
        voted_for_me.append(msg.get_sender())


  def _process_leader(self):
    LOG.info("Node entering LEADER state")
    time.sleep(1)

  def _get_node_metadata(self):
    return NodeMetadata(self._ip_address, self._port)
