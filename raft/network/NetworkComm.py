"""
NetworkComm.py provides a network communication layer
that abstracts the details of network communication to other nodes
The NetworkComm class starts two threads - a sender and a receiver thread -
and interacts with the message queue to exchange data with the rest of the
system
"""

import socket
import threading
import socketserver
import logging

from raft.LoggingHelper import get_logger
from raft.message import MessageTranslator, MessageQueue
from raft.network import NetworkUtil

LOG = get_logger(__name__)
LOG.setLevel(logging.ERROR)

class NetworkComm:

  def __init__(self, nodes, port, send_timeout=None):
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._nodes = nodes
    self._port = port
    self._server = None
    self._stop_sending = False
    self._sending_thread = None
    self._send_timeout = send_timeout

  def run(self):
    """Run the network comm layer - detaches two threads"""
    self._run_server()
    self._run_senders()

  def stop(self):
    """Completely shut down and kill the network comm layer"""
    self._shutdown_server()
    self._shutdown_sender_thread()

  def _run_server(self):
    LOG.info("Starting server thread")
    thread = threading.Thread(target=self._process_server_thread)
    thread.daemon = True
    thread.start()

  def _process_server_thread(self):
    LOG.info("Serving...")
    with socketserver.TCPServer(("", self._port), NetworkComm.TcpHandler) as server:
      # Save off the server object so we can shut it down later for testing purposes
      self._server = server
      server.serve_forever()

  class TcpHandler(socketserver.BaseRequestHandler):
    """TcpHandler that receives incoming data and puts it into the message queue"""
    def handle(self):
      data = self.request.recv(1024).strip().decode("utf-8")
      LOG.info("Received data {} from {}".format(data, self.client_address))
      message = MessageTranslator.json_to_message(data)
      if message is not None:
        MessageQueue.recv_enqueue(message)

  def _shutdown_server(self):
    LOG.info("Shutdown server called -- stopping server")
    self._server.shutdown()
    self._server.server_close()

  def _run_senders(self):
    LOG.info("Starting senders thread")
    self._sending_thread = threading.Thread(target=self._process_senders_thread)
    self._sending_thread.daemon = True
    self._sending_thread.start()

  def _process_senders_thread(self):
    while not self._stop_sending:
      self._send_messages_in_queue()
    LOG.info("Shutdown senders thread called -- stopping sending")

  def _shutdown_sender_thread(self):
    self._stop_sending = True
    if self._sending_thread is not None:
      self._sending_thread.join()

  def _send_messages_in_queue(self):
    if not MessageQueue.send_empty():
      msg = MessageQueue.send_dequeue()
      data = MessageTranslator.message_to_json(msg)
      if data is not None:
        LOG.info("Sending data {}".format(data))
        self._send_data(data)

  def _send_data(self, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      if self._send_timeout is not None:
        s.settimeout(self._send_timeout)
      for node in self._nodes:
        if self._is_node_me(node):
          continue
        try:
          s.connect((node.get_host(), node.get_port()))
          s.sendall(bytes(data + "\n", "utf-8"))
        except ConnectionRefusedError as e:
          LOG.info("Failed to connect to {}:{} and send data: {}".format(node.get_host(), node.get_port(), e))
        except Exception as e:
          LOG.info("Failed to send data for unknown reason: {}".format(e))

  def _is_node_me(self, node):
    return NetworkUtil.is_ippaddr_localhost(node.get_host()) and node.get_port() == self._port
