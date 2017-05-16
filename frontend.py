"""
Demo frontend

Currently lacks any session support, which is kinda big.
"""
import argparse
import functools
import logging
import os

# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web
import tornado.auth 
import urllib.parse

# ShareDB
from datahub import DataHub

# Bundles
from bundle import HIPAABundle, FERPABundle

# ... state ... Yeah. Yeah.
# TODO: Very much fix please
# Ideally shove this into a DB/cache and load from there
# Names are read in .bundle, which should be better integrated

# Data processing pipelines
PIPELINES = {
    'hipaa': HIPAABundle,
    'ferpa': FERPABundle,
}
PIPELINE = None
# DataHub connection
CONN = None

# OAuth2
class DataHubMixin(tornado.auth.OAuth2Mixin):
    """DataHub authentication via OAuth2."""
    _OAUTH_AUTHORIZE_URL = 'http://datahub-local.mit.edu/oauth2/authorize/'
    _OAUTH_ACCESS_TOKEN_URL = 'http://datahub-local.mit.edu/oauth2/token/'
    _OAUTH_SETTINGS_KEY = 'datahub_oauth'
    _OAUTH_SCOPE = 'read write'

    @tornado.auth._auth_return_future
    def get_authenticated_user(self, code, callback):
        """Handles the login for a DataHub user, returning a user object."""
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode({
            'redirect_uri': self.settings['auth_redirect'],
            'code': code,
            'client_id': self.settings['datahub_id'],
            'client_secret': self.settings['datahub_secret'],
            'grant_type': 'authorization_code',
            'scope': self._OAUTH_SCOPE
        })

        http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            functools.partial(self._on_access_token, callback),
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body=body
        )

    def _on_access_token(self, future, response):
        """Callback function for the exchange to the access token."""
        print(response)
        if response.error:
            msg = 'DataHub auth error: {}'.format(str(response))
            future.set_exception(tornado.auth.AuthError(msg))
            return

        args = tornado.escape.json_decode(response.body)
        future.set_result(args)

    def get_auth_http_client(self):
        return tornado.httpclient.AsyncHTTPClient()

    def authorize_redirect(self, callback=None):
        kwargs = {
            'redirect_uri': self.settings['auth_redirect'],
            'client_id': self.settings['datahub_id'],
            'callback': callback,
            'extra_params': {'response_type': 'code'}
        }

        return super(DataHubMixin, self).authorize_redirect(**kwargs)

class AuthHandler(tornado.web.RequestHandler, DataHubMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        code = self.get_argument('code', None)

        if code is not None:
            user = yield self.get_authenticated_user(code=code)

            # TODO: This must be a secure cookie
            self.set_cookie('oauth_token', user.get('access_token', ''), expires_days=1)

            self.redirect('/')
        else:
            yield self.authorize_redirect()

# API functions
class DHHandler(tornado.web.RequestHandler):
    def post(self):
        global CONN
        token = self.get_argument('token')
        try:
            CONN = DataHub(token)
            self.write({'ok': True})
        except RuntimeError:
            self.write({'ok': False})

class PipelineHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({
            'ok': True,
            'pipelines': {k: v.description for k, v in PIPELINES.items()}
        })

    def post(self):
        global PIPELINE
        pipeline_name = self.get_argument('pipeline')
        if pipeline_name in PIPELINES:
            PIPELINE = PIPELINES[pipeline_name].pipeline
            self.write({
                'ok': True,
                'pipeline': pipeline_name
            })
        else:
            self.write({
                'ok': False,
                'error': 'Pipeline {0} not found'.format(pipeline_name)
            })


class QueryHandler(tornado.web.RequestHandler):
    def post(self):
        repo_name = self.get_argument('repoName')
        table_name = self.get_argument('tableName')
        sample_size = int(self.get_argument('sampleSize'))
        if sample_size == 0:
            table = CONN.get_all_rows(repo_name, table_name)
        else:
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
        filters = {}
        for arg in self.request.arguments:
            filters[arg] = self.get_argument(arg)
        PIPELINE.filter(filters)
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
    def __init__(self, options):
        """
        Args:
            options (tornado.options): Tornado server options.
        """
        self.port = options.port
        static_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'frontend/')
        self._app = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/auth', AuthHandler),
            (r'/api/login', DHHandler),
            (r'/api/pipeline', PipelineHandler),
            (r'/api/query', QueryHandler),
            (r'/api/classify', ClassifyHandler),
            (r'/api/filter', FilterHandler),
        ],
            xsrf_cookie=True,
            static_path=static_path,
            autoreload=True,
            auth_redirect=options.auth_redirect,
            datahub_id=options.datahub_id,
            datahub_secret=options.datahub_secret,
            cookie_secret=options.secret_cookie)
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
    from tornado.options import define, options
    define('port', help='Start service on this port', type=int, default=8888)
    define('auth_redirect', help='OAuth2 redirect URL')
    define('datahub_id', help='DataHub client ID')
    define('datahub_secret', help='DataHub secret key')
    define('secret_cookie', help='Secret cookie hash')

    logging.info('Starting up!')
    tornado.options.parse_config_file('sharedb.conf')
    service = ShareDBService(options)

    def shutdown():
        logging.info('Shutting down!')
        service.stop()
        logging.info('Stopped.')
        os._exit(0)

    service.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ShareDB frontend')
    parser.add_argument('--port', dest='port', default='8888', type=int)
    args = parser.parse_args()

    main(args.port)

