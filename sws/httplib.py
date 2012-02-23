from sws.connection import SocketWrapper

class ParsingError(Exception):
	pass

class NotSupportedMethod(Exception):
	pass

class HTTPHeaders(dict):
	def __init__(self, dict=None):
		super(HTTPHeaders, self).__init__()
		dict = dict or {}
		for key, value in dict.items():
			self[key] = value
	
	def get_string(self):
		headers = []
		for key, value in self.items():
			headers.append("%s: %s" % (key, value))
			
		return "\r\n".join(headers)

	def __str__(self):
		return self.get_string()

class HTTPRequest(object):
	def __init__(self, conn):
		self.stream = SocketWrapper(conn)
		headers, method, resource, version = self.parse()
		self.headers = HTTPHeaders(headers)
		self.method = method
		self.resource = resource
		self.version = version
	
	def skip_ws(self):
		while True:
			x = self.stream.read(1)
			if not x.isspace():
				self.stream.seek(-1, 1)
				return

	def get_int(self):
		x = None
		result = ''
		while True:
			x = self.stream.read(1)
			if not x.isdigit():
				self.stream.seek(-1, 1)
				return result
			result += x

	def extract_version(self):
		self.skip_ws()
		http_literal = self.stream.read(4)
		if http_literal != 'HTTP':
			raise ParsingError()
	
		ch = self.stream.read(1)
		if ch != '/':
			raise ParsingError()
		
		major_version = self.get_int()
		ch = self.stream.read(1)
		if ch != '.':
			raise ParsingError()
		minor_version = self.get_int()
		
		return major_version, minor_version

	def parse(self):
		# method
		method = self.stream.read(3)
		if method != 'GET':
			raise NotSupportedMethod()
		
		# resource
		self.skip_ws()
		resource = ''
		while True:
			c = self.stream.read(1)
			if c.isspace():
				break
			resource += c
	
		# version
		version = self.extract_version()
	
		self.skip_ws()
	
		headers = {}
		while True:
			# key
			key = ''
			while True:
				c = self.stream.read(1)
				if c == ':':
					break
				key += c
	
			self.skip_ws()
			value = ''
			while True:
				c = self.stream.read(1)
				if c == '\r':
					c = self.stream.read(1)
					if c == '\n':
						break
				value += c
	
			headers[key] = value
	
			# end of headers
			s = self.stream.read(2)
			if s == '\r\n':
				break
	
			# push the two characters back.
			self.stream.seek(-2, 1)
		return headers, method, resource, version

class HTTPResponse(object):
	def __init__(self, conn, status_line=None, headers=None, body=None):
		self.status_line	= status_line or 'HTTP/1.1 200 OK'
		self.headers		= headers or HTTPHeaders()
		self.body			= body
		self.conn			= conn
		
	def send_response(self):
		if 'Content-length' not in self.headers:
			self.headers['Content-length'] = len(self.body)
		response = self.status_line + '\r\n' + str(self.headers) + '\r\n\r\n' + self.body
		self.conn.sendall(response)

if __name__ == "__main__":
	from cStringIO import StringIO
	x = StringIO("GET / HTTP/1.1\r\nHost: localhost:5001\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0.2) Gecko/20100101 Firefox/10.0.2\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\n\r\n")
	print HTTPRequest(x)