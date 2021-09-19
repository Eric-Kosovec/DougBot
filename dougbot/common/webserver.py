import threading

from http.server import ThreadingHTTPServer


class WebServer(ThreadingHTTPServer):

    # Server_address is a tuple: (ip, port)
    def __init__(self, server_address, request_handler):
        super().__init__(server_address, request_handler)
        self._lock = threading.Lock()
        self._serve_thread = None

    def serve_forever(self, poll_interval=0.5):
        with self._lock:
            if self._serve_thread is None:
                self._serve_thread = threading.Thread(target=super().serve_forever, args=(poll_interval,))
                self._serve_thread.start()

    def shutdown(self):
        # BaseServer shutdown is blocking
        shutdown_thread = threading.Thread(target=self._kill_server())
        shutdown_thread.start()

    def _kill_server(self):
        with self._lock:
            self._serve_thread.shutdown()
            self._serve_thread = None

'''
class Handler(CGIHTTPRequestHandler):

    def do_HEAD(self):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open('E:\\Programming\\Projects\\DougBot\\resources\\hello.html', 'r') as fd:
            data = fd.read()
        self.wfile.write(bytes(data, 'utf-8'))

    def do_POST(self):
        pass


def main():
    ws = WebServer(('localhost', 8080), Handler)
    ws.serve_forever()
    while True:
        pass


if __name__ == '__main__':
    main()
'''
