import threading

from http.server import ThreadingHTTPServer


class WebServer(ThreadingHTTPServer):

    # Server_address is a tuple: (ip, port)
    def __init__(self, server_address, request_handler):
        super().__init__(server_address, request_handler)
        self._lock = threading.Lock()
        self._serve_thread = None

    def serve_forever(self, poll_interval=0.5):
        # Don't want to unnecessarily block the async loop, if called from there, so spawn thread to grab lock
        serve_thread = threading.Thread(target=self._serve_forever, args=(poll_interval,))
        serve_thread.start()

    def shutdown(self):
        # BaseServer shutdown is blocking
        shutdown_thread = threading.Thread(target=self._shutdown_server)
        shutdown_thread.start()

    def _serve_forever(self, poll_interval):
        with self._lock:
            if self._serve_thread is None:
                self._serve_thread = threading.current_thread()
        super().serve_forever(poll_interval)

    def _shutdown_server(self):
        with self._lock:
            self._serve_thread.shutdown()
            self._serve_thread = None
