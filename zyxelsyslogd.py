#!/usr/bin/env python2

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP

sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.bind(('', 514))
while True:
	data, (saddr, sport) = sock.recvfrom(4096)
	print saddr, repr(data)
