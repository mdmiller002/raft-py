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

  # These parameters can be used to tune the speed of the raft algorithm
  SLEEP_TIME_SECS = 0.5
  TIMEOUT_MIN_MSECS = int(1.5 * 1000)
  TIMEOUT_MAX_MSECS = int(3.1 * 1000)

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
    self._populate_neighbors()
    LOG.info("Neighbors: {}".format(self._neighbors))
    while True:
      self._process_node()

  def _populate_neighbors(self):
    for node in self._nodes:
      if not self._network_comm.is_node_me(node):
        self._neighbors.append(node)

  def _process_node(self):
    if self._state == NodeState.FOLLOWER:
      self._process_follower()
    elif self._state == NodeState.CANDIDATE:
      self._process_candidate()
    elif self._state == NodeState.LEADER:
      self._process_leader()

  def _process_follower(self):
    LOG.info("Node entering FOLLOWER state with term {}".format(self._current_term))
    self._election_timeout = self._generate_timeout()
    LOG.info("Election timeout generated: {}ms".format(self._election_timeout))

    voted_this_term = False
    start = time.time()
    while not self._timed_out(start, self._election_timeout):
      if not MessageQueue.recv_empty():
        msg = MessageQueue.recv_dequeue()
        if not self._validate_message_sender(msg):
          continue
        LOG.info("Received a message: {}, {}, term: {}".format(msg.get_sender(), msg.get_type(), msg.get_election_term()))

        # Joining the cluster when a leader has already been established
        if self._current_leader is None and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received a heartbeat from the new leader {}".format(msg.get_sender()))
          self._current_leader = msg.get_sender()
          self._current_term = msg.get_election_term()
          self._send_heartbeat_response()
          return

        # Heartbeat from current leader
        if msg.get_sender() == self._current_leader and msg.get_type() == MessageType.HEARTBEAT:
          LOG.info("Received heartbeat from leader, remaining in follower state")
          self._send_heartbeat_response()
          return

        # Have a leader, but a new leader with a higher term has been elected
        if msg.get_sender() != self._current_leader and msg.get_type() == MessageType.HEARTBEAT \
                and msg.get_election_term() > self._current_term:
          LOG.info("Received a heartbeat from the new leader {}".format(msg.get_sender()))
          self._current_leader = msg.get_sender()
          self._current_term = msg.get_election_term()
          self._send_heartbeat_response()
          return

        # Vote request
        if msg.get_sender() != self._current_leader and msg.get_type() == MessageType.VOTE_REQUEST \
                and msg.get_election_term() > self._current_term and not voted_this_term:
          LOG.info("Received vote request from {}, sending vote response".format(msg.get_sender()))
          sender = self._get_node_metadata()
          message = Message(sender, MessageType.VOTE_RESPONSE, self._current_term)
          LOG.info("Sending vote response: {}".format(message))
          self._network_comm.send_data(message, msg.get_sender())
          voted_this_term = True

    LOG.info("Election timeout reached, entering candidate state")
    self._state = NodeState.CANDIDATE

  def _send_heartbeat_response(self):
    message = Message(self._get_node_metadata(), MessageType.HEARTBEAT_RESPONSE, self._current_term)
    self._network_comm.send_data(message, self._current_leader)

  def _process_candidate(self):
    self._current_term += 1
    LOG.info("Node entering CANDIDATE STATE with term {}".format(self._current_term))
    sender = self._get_node_metadata()
    message = Message(sender, MessageType.VOTE_REQUEST, self._current_term)
    for neighbor in self._neighbors:
      self._network_comm.send_data(message, neighbor)

    candidate_timeout = self._generate_timeout()
    LOG.info("Candidate timeout: {}".format(candidate_timeout))
    start = time.time()
    voted_for_me = []
    while not self._timed_out(start, candidate_timeout):
      while MessageQueue.recv_empty() and not self._timed_out(start, candidate_timeout):
        pass
      if self._timed_out(start, candidate_timeout):
        break
      msg = MessageQueue.recv_dequeue()
      if not self._validate_message_sender(msg):
        continue
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
      self._current_term -= 1


  def _process_leader(self):
    LOG.info("Node entering LEADER state")
    sender = self._get_node_metadata()
    message = Message(sender, MessageType.HEARTBEAT, self._current_term)
    for neighbor in self._neighbors:
      self._network_comm.send_data(message, neighbor)

    leader_timeout = self._generate_timeout()
    start = time.time()
    heartbeat_responses = []

    # TODO fix this so we don't timeout but remain as leader until there is another leader with a higher term
    while not self._timed_out(start, leader_timeout):
      while MessageQueue.recv_empty() and not self._timed_out(start, leader_timeout):
        pass
      if self._timed_out(start, leader_timeout):
        self._state = NodeState.FOLLOWER
        break
      msg = MessageQueue.recv_dequeue()
      LOG.info("Received a message: {}, {}, term: {}".format(msg.get_sender(), msg.get_type(), msg.get_election_term()))
      if not self._validate_message_sender(msg):
        continue

      if msg.get_type() == MessageType.HEARTBEAT_RESPONSE and msg.get_sender() not in heartbeat_responses:
        heartbeat_responses.append(msg.get_sender())

      if msg.get_type() == MessageType.HEARTBEAT_RESPONSE and msg.get_election_term() > self._current_term:
        LOG.info("Received a heartbeat from a leader with a higher term")

      # As soon as we get a majority ack, return
      if len(heartbeat_responses) + 1 >= self._votes_needed:
        return

    if self._state == NodeState.FOLLOWER:
      LOG.info("Failed to get majority ack in allotted time, stepping down")
      self._current_leader = None

  def _validate_message_sender(self, msg: Message) -> bool:
    if msg.get_sender() not in self._neighbors:
      LOG.info("Received message from {}:{}, not in neighbors".format(
        msg.get_sender().get_host(), msg.get_sender().get_port()))
      return False
    return True

  def _get_node_metadata(self) -> NodeMetadata:
    return NodeMetadata(self._ip_address, self._port)

  def _timed_out(self, start: float, timeout: int) -> bool:
    return (time.time() - start) * 1000 > timeout

  def _generate_timeout(self) -> int:
    return random.randint(Node.TIMEOUT_MIN_MSECS, Node.TIMEOUT_MAX_MSECS)

