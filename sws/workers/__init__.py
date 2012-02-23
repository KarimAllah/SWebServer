class RequestDispatcher(object):
    def __init__(self, app):
        self.app = app
        self.conf = app.conf
        self.init()

    def init(self):
        raise NotImplemented()

    def dispatch(self, conn, addr):
        raise NotImplemented()
    
    def stop(self):
        raise NotImplemented()