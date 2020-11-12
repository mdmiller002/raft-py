from enum import Enum
from raft.NodeMetadata import NodeMetadata

class MessageType(Enum):
  HEARTBEAT = "heartbeat"
  VOTE_REQUEST = "voteRequest"
  VOTE_RESPONSE = "voteResponse"

class Message:
  """Usable container for a raft message"""

  def __init__(self, sender: NodeMetadata, msg_type: MessageType, data: str = None):
    self._sender = sender
    self._type = msg_type
    self._data = data

  def __eq__(self, other):
    if other is None:
      return False
    return self._sender == other.get_sender() and \
            self._type == other.get_type() and \
            self._data == other.get_data()

  def __str__(self):
    return "{}, {}, {}".format(self._sender,
                               self._type,
                               self._data)

  def get_sender(self) -> NodeMetadata:
    return self._sender

  def get_type(self) -> MessageType:
    return self._type

  def get_data(self) -> str:
    return self._data


