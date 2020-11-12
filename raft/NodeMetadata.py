from raft.network import NetworkUtil

"""
Metadata about one node in the system
Used to keep status of all other nodes in the system by the Node class
"""
class NodeMetadata:
  def __init__(self, host: str, port: int):
    self._host: str = host
    self._port: int = port

  def __eq__(self, other):
    if other is None:
      return False
    return NetworkUtil.are_ipaddrs_equal(self._host, other.get_host()) and self._port == other.get_port()

  def get_host(self) -> str:
    return self._host

  def get_port(self) -> int:
    return self._port

  def __str__(self):
    return "{}:{}".format(self._host, self._port)
