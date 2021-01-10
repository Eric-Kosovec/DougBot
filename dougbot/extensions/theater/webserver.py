import threading

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class WebServer:

    def __init__(self, server_ip, server_port, directory):
        self._ip = server_ip
        self._port = server_port
        self._directory = directory
        self._running = False
        self._thread = None
        self._httpd = None

    def run(self):
        if not self._running and self._thread is None:
            self._thread = threading.Thread(target=self._thread_main)
            self._thread.start()

    def close(self):
        if self._running and self._httpd is not None:
            self._running = False
            self._thread = None
            self._httpd.shutdown()

    def is_running(self):
        return self._running

    def directory(self):
        return self._directory

    def _thread_main(self):
        self._running = True
        try:
            self._httpd = WebThreadingHTTPServer((self._ip, self._port), WebRequestHandler, self._directory)
            self._httpd.serve_forever()  # blocks until shutdown is called on it
        finally:
            self._running = False


class WebThreadingHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address, request_handler_class, directory):
        super().__init__(server_address, request_handler_class)
        self._directory = directory

    def directory(self):
        return self._directory


class WebRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.path = ''

    def do_GET(self):
        if self.path == '/':
            self.path = f'/{self.server.directory()}/index.html'
        else:
            self.path = f'/{self.server.directory()}{self.path}'
        try:
            webpage = open(self.path[1:], 'rb').read()
            self.send_response(200)
        except Exception as e:
            print(e)
            webpage = bytes('File not found', 'utf-8')
            self.send_response(404)
        self.end_headers()
        self.wfile.write(webpage)

    def do_HEAD(self):
        pass
