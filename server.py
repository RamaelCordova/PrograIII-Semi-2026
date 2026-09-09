from http.server import SimpleHTTPRequestHandler
server.py

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs

import json 

PORT = 8080

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

print(f"Servidor corriendo en el puerto {PORT}")
server = HTTPServer(('localhost', PORT), RequestHandler)
server.serve_forever()
            
            
