from sws.httplib import HTTPRequest, HTTPResponse

class BaseApplication(object):
    def handle(self, conn, addr):
        request = HTTPRequest(conn)
        response = HTTPResponse(conn)
        self.handle_request(request, response, addr)
    
    def handle_request(self, request, response, addr):
        raise NotImplemented()
    
    @property
    def conf(self):
        return {
                '404'       : 'templates/404.html',
                'index'     : 'templates/index.html',
                'ls_dir'    : 'templates/ls_dir.html',
                'root_dir'  : '.'
                }