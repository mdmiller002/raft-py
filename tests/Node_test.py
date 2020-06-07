import pytest

from raft.Node import *
from raft.message.Message import *
from tests.TestingHelper import *

@pytest.fixture
def basic_node():
  return Node(get_test_nodes(), 1738)

def test_promote_to_candidate(basic_node):
  basic_node._process_follower()
  assert basic_node._state == NodeState.CANDIDATE

def test_heard_from_leader(basic_node):
  leader = NodeMetadata("localhost", 12345)
  basic_node._current_leader = leader
  msg = Message(leader, MessageType.HEARTBEAT)
  MessageQueue.recv_enqueue(msg)
  basic_node._process_follower()
  assert basic_node._state == NodeState.FOLLOWER
