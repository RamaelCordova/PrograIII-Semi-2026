from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs

import json 

PORT = 3080

class miservisor(SimpleHTTPRequestHandler):
    def do_GET(self):
        url=urlparse(self.path)
        qs = parse_qs(url.query)

        if url.path == "/saludo":
            saludo =qs["nombre"][0] + "biwnvenido a Phyton"\
                
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(saludo.encode("utf-8"))

        if url.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

print(f"Servidor corriendo en el puerto {PORT}")
server = HTTPServer(('localhost', PORT), miservisor)
server.serve_forever()
            
            
