HTTP_VERSION_STR = 'HTTP/1.1'

class ParsingError(Exception):
	pass

class NotSupportedMethod(Exception):
	pass


def skip_ws(stream):
	while True:
		x = stream.read(1)
		if not x.isspace():
			stream.seek(-1, 1)
			return

def get_int(stream):
	x = None
	result = ''
	while True:
		x = stream.read(1)
		if not x.isdigit():
			stream.seek(-1, 1)
			return result
		result += x

def extract_version(stream):
	skip_ws(stream)
	http_literal = stream.read(4)
	if http_literal != 'HTTP':
		raise ParsingError()
	
	ch = stream.read(1)
	if ch != '/':
		raise ParsingError()

	major_version = get_int(stream)
	ch = stream.read(1)
	if ch != '.':
		raise ParsingError()
	minor_version = get_int(stream)

	return major_version, minor_version

def extraxt_uri(stream, init_char=None):

	# scheme
	if init_char == None:
		init_char = stream.read(1)
	rest_str = stream.read(3)
	scheme = init_char + rest_str
	if scheme != 'http':
		raise ParsingError()

	if stream.read(3) != '://':
		raise ParsingError()
	

	# host
	host = ''
	while True:
		next_char = stream.read(1)
		if not next_char.isalnum() or next_char != '_':
			break
		host += next_char

	# port
	if next_char == ':':
		port = ''
		while True:
			next_char = stream.read(1)
			if not next_char.isdigit():
				break
			port += next_char
	

	# abs_path
	abs_path = ''
	while True:
		next_char = stream.read(1)
		if next_char.isspace():
			break
		abs_path += next_char
	
	if abs_path == '':
		abs_path = '/'

def extract_headers(stream):
	# method
	method = stream.read(3)
	if method != 'GET':
		raise NotSupportedMethod()
	
	# resource
	skip_ws(stream)
	resource = ''
	while True:
		c = stream.read(1)
		if c.isspace():
			break
		resource += c

	# version
	version = extract_version(stream)

	skip_ws(stream)

	headers = {}
	while True:
		# key
		key = ''
		while True:
			c = stream.read(1)
			if c == ':':
				break
			key += c

		skip_ws(stream)
		value = ''
		while True:
			c = stream.read(1)
			if c == '\r':
				c = stream.read(1)
				if c == '\n':
					break
			value += c

		headers[key] = value

		# end of headers
		s = stream.read(2)
		if s == '\r\n':
			break

		# push the two characters back.
		stream.seek(-2, 1)
	return headers, method, resource, version

if __name__ == "__main__":
	from cStringIO import StringIO
	x = StringIO("GET / HTTP/1.1\r\nHost: localhost:5001\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0.2) Gecko/20100101 Firefox/10.0.2\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\n\r\n")
	print extract_headers(x)

