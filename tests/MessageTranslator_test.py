from raft.message.MessageTranslator import *
from raft.NodeMetadata import *
import json
import pytest

@pytest.mark.parametrize("msg_type", ["heartbeat", "voteRequest", "voteResponse"])
def test_json_to_msg_success(msg_type: str):
  json_obj = {
    "type": msg_type,
    "electionTerm": 1,
    "senderHost": "localhost",
    "senderPort": 12345,
    "data": "abcde"
  }
  sender = NodeMetadata("localhost", 12345)
  json_str = json.dumps(json_obj)
  msg = json_to_message(json_str)
  assert msg.get_election_term() == 1
  assert msg.get_sender() == sender
  assert msg.get_type() == MessageType(msg_type)
  assert msg.get_data() == "abcde"

def test_json_to_msg_success_no_data():
  json_obj = {
    "type": "heartbeat",
    "electionTerm": 1,
    "senderHost": "localhost",
    "senderPort": 12345
  }
  sender = NodeMetadata("localhost", 12345)
  json_str = json.dumps(json_obj)
  msg = json_to_message(json_str)
  assert msg.get_sender() == sender
  assert msg.get_election_term() == 1
  assert msg.get_type() == MessageType.HEARTBEAT
  assert msg.get_data() is None


@pytest.mark.parametrize("json_obj",
[
{},
{
  "type": "BAD_TYPE",
  "electionTerm": 1,
  "senderHost": "localhost",
  "senderPort": 12345,
  "data": "abcde"
},
{
  "type": "heartbeat",
  "electionTerm": 1,
  "senderPort": 12345,
  "data": "abcde"
},
{
  "type": "heartbeat",
  "electionTerm": 1,
  "senderHost": "localhost",
  "data": "abcde"
},
{
  "type": "heartbeat",
  "senderHost": "localhost",
  "senderPort": 12345,
  "data": "abcde"

}
])
def test_json_to_msg_missing_data(json_obj: dict):
  json_str = json.dumps(json_obj)
  msg = json_to_message(json_str)
  assert msg is None

@pytest.mark.parametrize("msg_type", [MessageType.HEARTBEAT, MessageType.VOTE_REQUEST, MessageType.VOTE_RESPONSE])
def test_msg_to_json_success(msg_type: MessageType):
  sender = NodeMetadata("localhost", 12345)
  message = Message(sender, msg_type, 1, "abc")
  msg_json = message_to_json(message)
  type_str = msg_type.value
  assert msg_json == "{\"type\": \"" + type_str + "\", \"electionTerm\": 1, \"senderHost\": \"localhost\", \"senderPort\": 12345, \"data\": \"abc\"}"

@pytest.mark.parametrize("msg_type", [MessageType.HEARTBEAT, MessageType.VOTE_REQUEST, MessageType.VOTE_RESPONSE])
def test_msg_to_json_success_no_data(msg_type: MessageType):
  sender = NodeMetadata("localhost", 12345)
  message = Message(sender, msg_type, 1)
  msg_json = message_to_json(message)
  type_str = msg_type.value
  assert msg_json == "{\"type\": \"" + type_str + "\", \"electionTerm\": 1, \"senderHost\": \"localhost\", \"senderPort\": 12345}"

def test_msg_to_json_no_type():
  sender = NodeMetadata("localhost", 12345)
  message = Message(sender, None, 1, "abc")
  assert message_to_json(message) is None

def test_msg_to_json_no_sender():
  message = Message(None, MessageType.HEARTBEAT, 1, "abc")
  assert message_to_json(message) is None

def test_msg_to_json_no_type_or_sender():
  message = Message(None, None, 1)
  assert message_to_json(message) is None

def test_msg_to_json_no_election_term():
  sender = NodeMetadata("localhost", 12345)
  message = Message(sender, MessageType.HEARTBEAT, None, "abc")
  assert message_to_json(message) is None
