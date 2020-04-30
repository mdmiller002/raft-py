"""
MessageTranslator.py provides utility functions to translate
messages between the JSON that they are transmitted as over the network
and Message objects
"""


import json
from raft.NodeMetadata import NodeMetadata
from raft.message.Message import Message, MessageType

MSG_TYPE_KEY = "type"
SENDER_HOST_KEY = "senderHost"
SENDER_PORT_KEY = "senderPort"
DATA_KEY = "data"

def json_to_message(data):
  """Translate a JSON message from the network
  into a usable Message object"""

  if not _validate_data(data):
    return None
  data_dict = json.loads(data)
  msg_type = data_dict.get(MSG_TYPE_KEY, None)
  if msg_type is None:
    return None
  try:
    msg_type_enum = MessageType(msg_type)
  except ValueError:
    return None
  sender_host = data_dict.get(SENDER_HOST_KEY, None)
  if sender_host is None:
    return None
  sender_port = data_dict.get(SENDER_PORT_KEY, None)
  if sender_port is None:
    return None
  msg_data = data_dict.get(DATA_KEY, None)

  node_metadata = NodeMetadata(sender_host, sender_port)
  ret = Message(node_metadata, msg_type_enum, msg_data)
  return ret

def _validate_data(data):
  if not isinstance(data, str):
    return False
  if len(data) == 0:
    return False
  return True

def message_to_json(message):
  """Serialize a message object into a JSON string"""

  if not isinstance(message, Message):
    return None
  json_dict = {}
  sender = message.get_sender()
  if message.get_type() is None or sender is None:
    return None
  json_dict[MSG_TYPE_KEY] = message.get_type().value
  json_dict[SENDER_HOST_KEY] = sender.get_host()
  json_dict[SENDER_PORT_KEY] = sender.get_port()
  if message.get_data() is not None:
    json_dict[DATA_KEY] = message.get_data()
  return json.dumps(json_dict)

