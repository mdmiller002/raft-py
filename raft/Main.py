import configparser
import pathlib
from raft.NodeMetadata import NodeMetadata


def _read_config():
  current_dir = pathlib.Path(__file__).parent.absolute()
  config = configparser.ConfigParser()
  config.read(current_dir / "raft.conf")
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

if __name__ == '__main__':
  main()
