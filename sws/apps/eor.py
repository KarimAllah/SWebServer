import os
import mimetypes

from sws.apps import BaseApplication


class NoopApp(BaseApplication):
    def handle_request(self, request, response, addr): 
        response.headers['Content-length']  = 0
        response.headers['Content-Type']    = 'text/plain'
        response.headers['Connection']      = "close"

        #response.body = entity
        response.send_response()
