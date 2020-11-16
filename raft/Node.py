"""
Node.py contains a Node class that implements the raft logic
Node is the top layer level in the system
"""

from enum import Enum
import random
import time
from typing import Optional

from raft.NodeMetadata import NodeMetadata
from raft.message import MessageQueue
from raft.message.Message import MessageType, Message
from raft.LoggingHelper import get_logger
from raft.network import NetworkUtil
from raft.network import NetworkComm

LOG = get_logger(__name__)

class NodeState(Enum):
  FOLLOWER = 1
  CANDIDATE = 2
  LEADER = 3

class Node:

  SLEEP_TIME = 1

  def __init__(self, nodes_list: list, port: int, network_comm: NetworkComm):
    self._state: NodeState = NodeState.FOLLOWER
    self._election_timeout: Optional[int] = None
    self._current_term: int = 0
    self._current_leader: Optional[NodeMetadata] = None
    self._nodes: list = nodes_list
    self._neighbors: list = []
    self._cluster_size: int = len(nodes_list)
    self._votes_needed: int = self._cluster_size // 2 + 1
    self._port: int = port
    self._ip_address: str = NetworkUtil.get_localhost_ip_addr()
    self._network_comm: NetworkComm = network_comm

  def run(self):
    """run this node's raft algorithm forever"""
    for node in self._nodes:
      if not self._network_comm.is_node_me(node):
        self._neighbors.append(node)
    LOG.info("Neighbors: {}".format(self._neighbors))
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
    # TODO next when a failover has happened, we don't switch leaders.
    # Use terms to implement this (i.e. if the heartbeat has a higher
    # term number, take them as the new leader
    LOG.info("Node entering FOLLOWER state")
    self._election_timeout = self._generate_timeout()
    LOG.info("Election timeout generated: {}ms".format(self._election_timeout))

    start = time.time()
    while self._not_timed_out(start, self._election_timeout):
      time.sleep(Node.SLEEP_TIME)
      if not MessageQueue.recv_empty():
        msg = MessageQueue.recv_dequeue()
        LOG.info("Received a message: {}, {}".format(msg.get_sender(), msg.get_type()))
        if self._current_leader is None and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received a heartbeat from the new leader {}".format(msg.get_sender()))
          self._current_leader = msg.get_sender()
          return
        if msg.get_sender() == self._current_leader and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received heartbeat from leader, remaining in follower state")
          return
        if msg.get_sender() != self._current_leader and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received a heartbeat from the new leader {}".format(msg.get_sender()))
          self._current_leader = msg.get_sender()
          return
        if msg.get_sender() != self._current_leader and msg.get_type() == MessageType.VOTE_REQUEST:
          LOG.info("Received vote request from {}, sending vote response".format(msg.get_sender()))
          sender = self._get_node_metadata()
          message = Message(sender, MessageType.VOTE_RESPONSE)
          LOG.info("Sending vote response: {}".format(message))
          self._network_comm.send_data(message, msg.get_sender())
    LOG.info("Election timeout reached, entering candidate state")
    self._state = NodeState.CANDIDATE

  def _process_candidate(self):
    LOG.info("Node entering CANDIDATE STATE")
    # TODO handle election terms
    self._current_term += 1
    sender = self._get_node_metadata()
    message = Message(sender, MessageType.VOTE_REQUEST)
    MessageQueue.send_enqueue(message)
    for neighbor in self._neighbors:
      self._network_comm.send_data(message, neighbor)

    candidate_timeout = self._generate_timeout()
    LOG.info("Candidate timeout: {}".format(candidate_timeout))
    start = time.time()
    while self._not_timed_out(start, candidate_timeout):
      while MessageQueue.recv_empty() and self._not_timed_out(start, candidate_timeout):
        pass
      if not self._not_timed_out(start, candidate_timeout):
        break
      msg = MessageQueue.recv_dequeue()
      if msg.get_sender() not in self._nodes:
        LOG.info("Received message from {}:{}, not in nodes list".format(
          msg.get_sender().get_host(), msg.get_sender().get_port()))
        continue
      voted_for_me = []
      if msg.get_type() == MessageType.VOTE_RESPONSE and msg.get_sender not in voted_for_me:
        LOG.info("Got vote from {}".format(msg.get_sender()))
        voted_for_me.append(msg.get_sender())
      if len(voted_for_me) + 1 >= self._votes_needed:
        LOG.info("Got enough votes to enter leader state")
        self._state = NodeState.LEADER
        return

    if self._state == NodeState.CANDIDATE:
      LOG.info("Failed to get votes, falling back to follower state")
      self._state = NodeState.FOLLOWER


  def _process_leader(self):
    LOG.info("Node entering LEADER state")
    while True:
      sender = self._get_node_metadata()
      message = Message(sender, MessageType.HEARTBEAT)
      for neighbor in self._neighbors:
        self._network_comm.send_data(message, neighbor)
      time.sleep(Node.SLEEP_TIME)

  def _get_node_metadata(self) -> NodeMetadata:
    return NodeMetadata(self._ip_address, self._port)

  def _not_timed_out(self, start: float, timeout: int) -> bool:
    return (time.time() - start) * 1000 < timeout

  def _generate_timeout(self) -> int:
    return random.randint(5000, 6000)
    #return random.randint(500, 1001)

