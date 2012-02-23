import socket

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