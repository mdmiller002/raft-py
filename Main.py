import configparser
import sys
import os
from pathlib import Path
from raft.NodeMetadata import NodeMetadata
from raft.network.NetworkComm import NetworkComm
from raft.Node import Node

config_file = Path(sys.argv[1])

def _read_config():
  config = configparser.ConfigParser()
  config.read(config_file)
  nodes = []
  for key in list(config['nodes'].keys()):
    curr_node = config['nodes'][key]
    (host, port) = curr_node.split(":")
    port = int(port)
    node_metadata = NodeMetadata(host, port)
    nodes.append(node_metadata)
  port = int(config['conf']['listenPort'])
  return nodes, port

def main():
  nodes, port = _read_config()
  network_comm = NetworkComm(nodes, port, 0.25)
  network_comm.run()
  node = Node(nodes, port, network_comm)

  node.run()

if __name__ == '__main__':
  main()
