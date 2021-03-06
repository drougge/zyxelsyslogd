#!/usr/bin/env python2
#
# Read the slightly broken syslog messages from my ZyXEL GS1900-24 switch
# and save them to a file named after todays date in a directory named
# after the switch IP.
# Log lines are:
# %Y-%m-%d %H:%M:%S $FACILITY.$LEVEL $MESSAGE
# which is not the format syslogd would have used.

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP
from os.path import isdir, join
from datetime import datetime
from argparse import ArgumentParser

p = ArgumentParser()
p.add_argument('--host', type=str, help='listen host', default='')
p.add_argument('--port', type=int, help='listen port', default=514)
args = p.parse_args()

sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.bind((args.host, args.port,))

def dropped(reason, data):
	print "Dropped %d bytes (%s): %r" % (len(data), reason, data,)

while True:
	data, (saddr, sport) = sock.recvfrom(4096)
	try:
		pri, _, _, _, _, host, msg = data.split(None, 6)
		if host != saddr:
			# Broken message / not from the host it claims, drop it
			dropped("addr mismatch", data)
			continue
		if not isdir(host):
			# Not from something we expect logs from
			dropped("unknown host", data)
			continue
		# Reformat pri to be a little more readable:
		# facility.level, but still numeric.
		pri = int(pri[1:-1], 10)
		pri = "%d.%d" % (pri >> 3, pri & 7,)
		date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# no misleading newlines allowed
		msg = msg.replace("\n", " ").strip()
		logline = "%s %s %s\n" % (date, pri, msg,)
		with open(join(host, date[:10] + ".log"), "ab") as fh:
			fh.write(logline)
	except (ValueError, IOError,):
		dropped("internal error", data)
