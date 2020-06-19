from http.server import BaseHTTPRequestHandler


class WebServer(BaseHTTPRequestHandler):

    _WEB_FILE_BASE = 'web/'

    def do_GET(self):
        if self.path == '/':
            self.path = f'/{self._WEB_FILE_BASE}index.html'
        else:
            self.path = f'/{self._WEB_FILE_BASE}{self.path}'
        try:
            webpage = open(self.path[1:], 'rb').read()
            self.send_response(200)
        except Exception as e:
            print(e)
            webpage = bytes('File not found', 'utf-8')
            self.send_response(404)
        self.end_headers()
        self.wfile.write(webpage)


#httpd = HTTPServer(('localhost', 8080), WebServer)
#httpd.serve_forever()
