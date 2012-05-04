import os
import sys
import logging
import threading

from sws import config

from sws.workers import RequestDispatcher
import socket

logger = logging.getLogger("ThreadingDispatcher")

class WorkerClass(threading.Thread):
	def set_connection(self, app, conn, addr):
		self.conn = conn
		self.addr = addr
		self.app = app

	def run(self):
		self.app.handle(self.conn, self.addr)


class ThreadingDispatcher(RequestDispatcher):
    def init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((config.HOST, config.PORT))
        self.socket.listen(config.PENDING_CONNECTIONS)

    def dispatch(self):
        logger.debug("Waiting for new connections ...")
        conn, addr = self.socket.accept()
        logger.debug("Received connection from %s", addr)
	worker = WorkerClass()
	worker.set_connection(self.app, conn, addr)
	worker.start()

    def stop(self):
        self.socket.close()
