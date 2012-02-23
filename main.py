import os
import socket
import logging

import config

logger = logging.getLogger(config.SERVER_NAME)

STATIC_PAGE = '''<html><head><title>TEST</title></head><body>NULL</body></html>'''

HTTP_PAGE = 'HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: %s\r\n\r\n%s' % (len(STATIC_PAGE), STATIC_PAGE)

def handle_connection(conn, addr):
	conn.sendall(HTTP_PAGE)

def main():
	logger.debug("Launching ( %s ) on ( %s, %s )", config.SERVER_NAME, config.HOST, config.PORT)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((config.HOST, config.PORT))
	s.listen(config.PENDING_CONNECTIONS)

	try:
		while True:
			logger.debug("Waiting for new connections ...")
			conn, addr = s.accept()
			logger.debug("Received connection from %s", addr)
			# Asynchronously handle the connection
			pid = os.fork()
			if not pid:
				handle_connection(conn, addr)
				conn.close()
				break
	except KeyboardInterrupt:
		logger.debug("Normally exiting.")
	except Exception as ex:
		logger.debug("Uncaught exception raised, (%s)", ex)
	finally:
		s.close()

	

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	main()
