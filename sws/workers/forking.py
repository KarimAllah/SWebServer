import os
import sys
import logging

from sws import config

from sws.workers import RequestDispatcher
import socket

logger = logging.getLogger("ForkingDispatcher")

class ForkingDispatcher(RequestDispatcher):
    def init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((config.HOST, config.PORT))
        self.socket.listen(config.PENDING_CONNECTIONS)

    def dispatch(self):
        logger.debug("Waiting for new connections ...")
        conn, addr = self.socket.accept()
        logger.debug("Received connection from %s", addr)
        pid = os.fork()
        if not pid:
            # close this listening socket as early as possible
            self.socket.close()
            self.app.handle(conn, addr)
            conn.close()
            sys.exit(0)

    def stop(self):
        self.socket.close()