import configparser
import sys
from flask import Blueprint, request
from pathlib import Path

from raft.NodeMetadata import NodeMetadata
from raft.Node import Node

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

def init():
  global node
  nodes, port = _read_config()
  node = Node(nodes, port)

bp = Blueprint("raft", __name__, url_prefix="/raft")
config_file = Path(sys.argv[1])
node : Node = None
init()

@bp.route("/state", methods=("GET",))
def state():
  if request.method == "GET":
    return str(node.get_state().value) + "\n"


