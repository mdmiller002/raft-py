import socket
from raft.NodeMetadata import NodeMetadata

def get_test_nodes():
  node1 = NodeMetadata("localhost", 1738)
  node2 = NodeMetadata("localhost", 1739)
  node3 = NodeMetadata("localhost", 1740)
  nodes = [node1, node2, node3]
  return nodes

def find_free_port():
  s = socket.socket()
  s.bind(('', 0))  # Bind to a free port provided by the host.
  return s.getsockname()[1]

