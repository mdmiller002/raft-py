from raft.network import NetworkUtil

"""
Metadata about one node in the system
Used to keep status of all other nodes in the system by the Node class
"""
class NodeMetadata:
  def __init__(self, host, port):
    self._host = host
    self._port = port

  def __eq__(self, other):
    return NetworkUtil.are_ipaddrs_equal(self._host, other.get_host()) and self._port == other.get_port()

  def get_host(self):
    return self._host

  def get_port(self):
    return self._port
