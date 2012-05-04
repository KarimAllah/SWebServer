import logging

from sws import config
from sws.apps.eor import NoopApp
from sws.apps.diretories import DirectoryListing
from sws.workers.fork import ForkingDispatcher
from sws.workers.thread import ThreadingDispatcher

logger = logging.getLogger(config.SERVER_NAME)

def main():
    logger.debug("Launching ( %s ) on ( %s, %s )", config.SERVER_NAME, config.HOST, config.PORT)
    app = DirectoryListing()
    dispatcher = ForkingDispatcher(app)

    try:
        while True:
            dispatcher.dispatch()
    except KeyboardInterrupt:
        logger.debug("Exiting normally.")
    except StopIteration:
        pass
    except Exception as ex:
        logger.debug("Uncaught exception raised, (%s)", ex)
    finally:
        dispatcher.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
