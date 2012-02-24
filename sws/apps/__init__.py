from sws.httplib import HTTPRequest, HTTPResponse

class Config(dict):
    def __init__(self, dict=None):
        dict = dict or {}
        for key, value in dict.items():
            self[key] = value
            
    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, value):
        self[key] = value

class BaseApplication(object):
    def __init__(self):
        self._conf = None

    def handle(self, conn, addr):
        request = HTTPRequest(conn)
        response = HTTPResponse(conn)
        self.handle_request(request, response, addr)
    
    def handle_request(self, request, response, addr):
        raise NotImplemented()
    
    @property
    def conf(self):
        if not self._conf:
            configs = {
                    '404'       : 'templates/404.html',
                    'index'     : 'templates/index.html',
                    'ls_dir'    : 'templates/ls_dir.html',
                    'root_dir'  : '.'
                    }
            self._conf = Config(configs)
        return self._conf
