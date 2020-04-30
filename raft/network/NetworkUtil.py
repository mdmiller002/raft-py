"""
NetworkUtil.py provides utility networking functions
"""

import socket

_local_ip_address = socket.gethostbyname(socket.gethostname())

def get_localhost_ip_addr():
  return _local_ip_address

def is_ippaddr_localhost(addr):
  return addr == 'localhost' or addr == '127.0.0.1' or addr == _local_ip_address

def are_ipaddrs_equal(addr1, addr2):
  if addr1 == addr2:
    return True
  if addr1 == 'localhost' or addr1 == '127.0.0.1' or addr1 == _local_ip_address:
    return addr2 == 'localhost' or addr2 == '127.0.0.1' or addr2 == _local_ip_address
  return False
