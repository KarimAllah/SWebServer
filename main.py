import os
import socket
import logging
import mimetypes

import config
import http_lib

logger = logging.getLogger(config.SERVER_NAME)

INDEX = '''
<html>
        <head>
                <title>This is supposed to be a fancy index page.</title>
        </head>
        <body>
                <h1>FakeWebserver</h1>
                <p>Welcome to our fake webserver.
We've specifically created it for you. Because it does absolutely nothing.__EVIL_SMILE__</p>
        </body>
</html>'''

DIR_TEMPLATE = '''
<html>
        <head>
                <title>Directory Listing</title>
        </head>
        <body>
                <h3>Directory : %s</h3>
                %s
        </body>
</html>'''

def handle_connection(conn, addr):
	file_conn = SocketWrapper(conn)
	headers, method, resource, version = http_lib.extract_headers(file_conn)
	host = headers['Host']

	# Apparently os.path.join will return any component that sounds like an absolute path without doing any joining.
	if resource.startswith("/"):
		resource = resource[1:]
	full_path = os.path.join(config.ROOT_DIR, resource)
	content_type, _ = mimetypes.guess_type(full_path)

	if os.path.exists(full_path):
		if os.path.isfile(full_path):
			fp = open(full_path)
			entity = fp.read()
			fp.close()
		elif os.path.isdir(full_path):
			files = []
			if resource:
				if resource.endswith("/"):
					files.append("[d]\t<a href='%s'>%s</a>" % ("..", "(UP)"))
				else:
					files.append("[d]\t<a href='%s'>%s</a>" % (".", "(UP)"))

			parent_resource = resource.rsplit("/", 1)[-1]
			for _file in os.listdir(full_path):
				prefix = "[d]\t"
				cur_path = os.path.join(full_path, _file)

				if os.path.isfile(cur_path):
					prefix = "[f]\t"

				file_name = _file if resource.endswith("/") else "/".join([parent_resource, _file])
				files.append(prefix + "<a href='%s'>%s</a>" % (file_name, _file))

			entity = DIR_TEMPLATE % (full_path, '<br>'.join(files))
	else:
		entity = INDEX

	response = http_lib.HTTP_VERSION_STR
	response += ' 200 OK\r\nConnection: close\r\nContent-Length: %s\r\nContent-Type: %s\r\n\r\n%s' % (len(entity), content_type, entity)
	conn.sendall(response)


class SocketWrapper(object):
	''' provide a semi file-like interface for sockets '''
	def __init__(self, connection, buf_size=1024*8):
		self.conn = connection
		self.buf_size = buf_size
		self.cache = ''
		self.index = 0
	
	def read(self, count):
		while True:
			try:
				if self.index + count > len(self.cache):
					raise Exception()

				result = self.cache[self.index:self.index + count]
				break
			except:
				try:
					read = self.conn.recv(self.buf_size)
					self.cache += read
				except socket.timeout:
					result = ''
					break

		self.index += len(result)
		return result

	def seek(self, index, type):
		if type == 0:
			if len(self.cache) < index < 0:
				raise Exception("Out of bounds")
			self.index = index
		elif type == 1:
			if len(self.cache) < self.index + index < 0:
				raise Exception("Out of bounds")
			self.index += index
		elif type == 2:
			raise TypeError("can't do that on a socket")

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
