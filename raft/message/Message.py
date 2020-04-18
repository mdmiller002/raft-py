from enum import Enum


class MessageType(Enum):
  HEARTBEAT = "heartbeat"
  VOTE_REQUEST = "voteRequest"
  VOTE_RESPONSE = "voteResponse"

class Message:
  """Usable container for a raft message"""

  def __init__(self, sender, msg_type, data=None):
    self._sender = sender
    self._type = msg_type
    self._data = data

  def __eq__(self, other):
    return self._sender == other.get_sender() and \
            self._type == other.get_type() and \
            self._data == other.get_data()

  def get_sender(self):
    return self._sender

  def get_type(self):
    return self._type

  def get_data(self):
    return self._data


