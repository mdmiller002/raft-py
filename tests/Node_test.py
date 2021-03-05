import pytest
from unittest.mock import Mock

from raft.Node import *
from raft.message.Message import *
from tests.TestingHelper import *

def setup_mock_network_comm() -> Mock:
  nc = Mock()
  def side_effect(arg):
    if arg == NodeMetadata("localhost", 1738):
      return True
    return False
  nc.is_node_me.side_effect = side_effect
  return nc

network_comm = setup_mock_network_comm()

@pytest.fixture
def basic_node() -> Node:
  nodes = get_test_nodes()
  node = Node(nodes, 1738, network_comm)
  node._populate_neighbors()
  return node

@pytest.fixture(autouse=True)
def before_and_after_each():
  MessageQueue._recv_clear()
  yield
  MessageQueue._recv_clear()

def test_start_follower_promote_to_candidate(basic_node: Node):
  basic_node._process_follower()
  assert basic_node._state == NodeState.CANDIDATE

def test_start_follower_heard_from_leader(basic_node: Node):
  leader = NodeMetadata("localhost", 1739)
  basic_node._current_leader = leader
  basic_node._current_term = 1
  msg = Message(leader, MessageType.HEARTBEAT, 1)
  MessageQueue.recv_enqueue(msg)
  basic_node._process_follower()
  assert basic_node._state == NodeState.FOLLOWER
  assert basic_node._current_term == 1
  assert basic_node._current_leader == leader
  resp_msg = Message(basic_node._get_node_metadata(), MessageType.HEARTBEAT_RESPONSE, 0)
  network_comm.send_data.assert_called_with(resp_msg, leader)

def test_start_follower_join_cluster(basic_node: Node):
  leader = NodeMetadata("localhost", 1739)
  msg = Message(leader, MessageType.HEARTBEAT, 1)
  MessageQueue.recv_enqueue(msg)
  basic_node._process_follower()
  assert basic_node._state == NodeState.FOLLOWER
  assert basic_node._current_term == 1
  assert basic_node._current_leader == leader

def test_start_follower_have_leader_new_leader(basic_node: Node):
  old_leader = NodeMetadata("localhost", 1739)
  new_leader = NodeMetadata("localhost", 1740)
  basic_node._current_leader = old_leader
  basic_node._current_term = 1
  msg = Message(new_leader, MessageType.HEARTBEAT, 2)
  MessageQueue.recv_enqueue(msg)
  basic_node._process_follower()
  assert basic_node._state == NodeState.FOLLOWER
  assert basic_node._current_term == 2
  assert basic_node._current_leader == new_leader

def test_start_follower_vote_request(basic_node: Node):
  candidate = NodeMetadata("localhost", 1739)
  msg = Message(candidate, MessageType.VOTE_REQUEST, 1)
  MessageQueue.recv_enqueue(msg)
  basic_node._process_follower()
  resp_msg = Message(basic_node._get_node_metadata(), MessageType.VOTE_RESPONSE, 0)
  network_comm.send_data.assert_called_with(resp_msg, msg.get_sender())


