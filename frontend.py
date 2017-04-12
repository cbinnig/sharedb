"""
Demo frontend

Currently lacks any session support, which is kinda big.
"""
import argparse
import logging
import os

# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

# ShareDB
from pipeline import Pipeline, Pipe
from datahub import DataHub
from classification import SSN, Lookup
from filter import SSNFilter, Drop

# ... state ... Yeah. Yeah.
# TODO: Very much fix please
# Ideally shove this into a DB/cache and load from there
def read_names():
    names = set()
    with open('data/names.dat') as f:
        for name in f:
            names.add(name.strip().lower())
    return names

# Data processing pipeline
PIPELINE = Pipeline()
PIPELINE.add_pipe("ssn", Pipe(SSN, SSNFilter()))
PIPELINE.add_pipe("name", Pipe(Lookup(read_names()), Drop()))
# DataHub connection
CONN = None

# API functions
# TODO: OAuth
TESTING_TOKEN = 'u5jWhFhbT6Dfx9lgqufKEHTCqYPHv9'

class DHHandler(tornado.web.RequestHandler):
    def post(self):
        global CONN
        token = self.get_argument('token')
        try:
            CONN = DataHub(token)
            self.write({'ok': True})
        except RuntimeError:
            self.write({'ok': False})

class QueryHandler(tornado.web.RequestHandler):
    def post(self):
        repo_name = self.get_argument('repoName')
        table_name = self.get_argument('tableName')
        sample_size = int(self.get_argument('sampleSize'))
        table = CONN.get_sample(repo_name, table_name, sample_size)
        PIPELINE.add_data(table)
        self.write({
            'ok': True,
            'table': PIPELINE.data
        })

class ClassifyHandler(tornado.web.RequestHandler):
    def post(self):
        ratings = PIPELINE.classify()
        self.write({
            'ok': True,
            'ratings': ratings
        })

class FilterHandler(tornado.web.RequestHandler):
    def post(self):
        # TODO: Make configurable
        PIPELINE.filter({col: max(scores.items(), key=lambda s: s[1])[0] for col, scores in PIPELINE.ratings.items()})
        self.write({
            'ok': True,
            'table': PIPELINE.data
        })

# Web handlers
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render()

    def render(self):
        self.write(self.render_string('templates/index.html'))

class ShareDBService:
    """Registers handlers and kicks off the IOLoop"""
    def __init__(self, port):
        """
        Args:
            port (str): The port to start the server on.
        """
        self.port = port
        static_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'frontend/')
        self._app = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/api/login', DHHandler),
            (r'/api/query', QueryHandler),
            (r'/api/classify', ClassifyHandler),
            (r'/api/filter', FilterHandler),
        ], xsrf_cookie=True, static_path=static_path)
        self.server = tornado.httpserver.HTTPServer(self._app)
        self.sockets = tornado.netutil.bind_sockets(self.port, '0.0.0.0')
        self.server.add_sockets(self.sockets)
        for s in self.sockets:
            sockname = s.getsockname()
            logging.info('Listening on {socket}, port {port}'
                         .format(socket=sockname[0], port=sockname[1]))

    def start(self):
        logging.info('Starting.')
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        logging.info('Stopping.')
        self.server.stop()

    def get_socket(self):
        return self.sockets[0].getsockname()[:2]

def main(port):
    logging.info('Starting up!')
    try:
        service = ShareDBService(port)

        def shutdown():
            logging.info('Shutting down!')
            service.stop()
            logging.info('Stopped.')
            os._exit(0)

        service.start()
    except Exception as e:
        logging.error('Uncaught exception: {e}'.format(e=e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ShareDB frontend')
    parser.add_argument('--port', dest='port', default='8888', type=int)
    args = parser.parse_args()

    main(args.port)