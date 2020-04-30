import time
import pytest
import json

from raft.network.NetworkComm import NetworkComm
from raft.message import MessageTranslator, MessageQueue
from tests.TestingHelper import *

@pytest.fixture
def nodes():
  node1 = NodeMetadata("localhost", find_free_port())
  node2 = NodeMetadata("localhost", find_free_port())
  node3 = NodeMetadata("localhost", find_free_port())
  nodes = [node1, node2, node3]
  return nodes

@pytest.fixture
def json_msg():
  return json.dumps({
    "type": "heartbeat",
    "senderHost": "localhost",
    "senderPort": 12345,
    "data": "abcde"
  })

def test_recv_data_success(nodes, json_msg):
  network_comm = NetworkComm(nodes, nodes[0].get_port())
  network_comm._run_server()
  time.sleep(0.1)
  _send_data(json_msg, nodes[0].get_port())
  time.sleep(0.1)
  msg = MessageTranslator.json_to_message(json_msg)
  assert not MessageQueue.recv_empty()
  assert MessageQueue.recv_qsize() == 1
  assert MessageQueue.recv_dequeue() == msg
  network_comm._shutdown_server()

def test_send_data_success(nodes, json_msg):
  msg = MessageTranslator.json_to_message(json_msg)
  network_comm = NetworkComm(nodes, nodes[0].get_port(), 0.25)
  MessageQueue.send_enqueue(msg)
  network_comm._run_senders()
  time.sleep(0.1)
  assert MessageQueue.send_empty()
  network_comm._shutdown_sender_thread()

def test_send_and_receive(nodes, json_msg):
  network_comm = NetworkComm(nodes, nodes[0].get_port(), 0.25)
  network_comm.run()
  time.sleep(0.1)
  _send_data(json_msg, nodes[0].get_port())
  time.sleep(0.1)
  msg = MessageTranslator.json_to_message(json_msg)
  assert not MessageQueue.recv_empty()
  assert MessageQueue.recv_qsize() == 1
  assert MessageQueue.recv_dequeue() == msg

  MessageQueue.send_enqueue(msg)
  time.sleep(0.1)
  assert MessageQueue.send_empty()

  network_comm.stop()

def _send_data(data, port):
  print("Sending data {} to localhost:{}".format(data, port))
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", port))
    s.sendall(bytes(data + "\n", "utf-8"))
