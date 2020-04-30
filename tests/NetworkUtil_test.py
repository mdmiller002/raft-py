import pytest
from raft.network.NetworkUtil import *

@pytest.mark.parametrize(["addr1", "addr2"],
[("999.999.999.999", "999.999.999.999"),
 ("localhost", "localhost"),
 ("localhost", "127.0.0.1"),
 ("localhost", get_localhost_ip_addr()),
 ("127.0.0.1", "localhost"),
 ("127.0.0.1", "127.0.0.1"),
 ("127.0.0.1", get_localhost_ip_addr()),
 (get_localhost_ip_addr(), "localhost"),
 (get_localhost_ip_addr(), "127.0.0.1"),
 (get_localhost_ip_addr(), get_localhost_ip_addr()),])
def test_addrs_equal(addr1, addr2):
  assert are_ipaddrs_equal(addr1, addr2)

@pytest.mark.parametrize(["addr1", "addr2"],
[('localhost', '999.999.999.999'),
 ('127.0.0.1', '999.999.999.999'),
 (get_localhost_ip_addr(), '999.999.999.999'),
 ('999.999.999.999', 'localhost'),
 ('999.999.999.999', '127.0.0.1'),
 ('999.999.999.999', get_localhost_ip_addr())])
def test_addrs_not_equal(addr1, addr2):
  assert not are_ipaddrs_equal(addr1, addr2)
