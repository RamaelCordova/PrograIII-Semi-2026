from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs
import crud_clientes
import crud_impuestos
import crud_usuario_usss090525
import json
from decimal import Decimal
import datetime

port = 3000
crudClientes = crud_clientes.crud_clientes()
crudImpuestos = crud_impuestos.crud_impuestos()
crudUsuarios = crud_usuario_usss090525.crud_usuario_usss090525()

def json_serial(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return str(obj)

class miServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            longitud = int(self.headers.get('Content-Length', 0))
            datos = self.rfile.read(longitud)
            datos = datos.decode("utf-8")
            datos = parse.unquote(datos)
            datos = json.loads(datos) if datos else {}
            
            urlParse = urlparse(self.path)
            
            if urlParse.path == "/cliente":
                respuesta = {'msg': crudClientes.administrar(datos)}
            elif urlParse.path == "/usuario":
                respuesta = {'msg': crudUsuarios.crud_usuario_usss090525(datos)}
            elif urlParse.path == "/login":
                respuesta = crudUsuarios.autenticar(datos.get('usuario', ''), datos.get('clave', ''))
            elif urlParse.path == "/calcular_impuesto":
                respuesta = crudImpuestos.calcular_impuesto(datos['balance'], datos['producto_codigo'])
            elif urlParse.path == "/guardar_periodo":
                respuesta = {'msg': crudImpuestos.guardar_periodo(datos)}
            else:
                respuesta = {'msg': 'Ruta no encontrada'}

            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta, default=json_serial).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode("utf-8"))

    def do_GET(self):
        try:
            urlParse = urlparse(self.path)
            qs = parse_qs(urlParse.query)

            if urlParse.path == "/clientes":
                buscar = qs.get('buscar', [''])[0]
                if buscar in ('[object Event]', 'undefined', 'null'):
                    buscar = ''
                datos = crudClientes.consultar(buscar)
                self.send_response(200)
                self.send_header("Content-type","application/json")
                self.end_headers()
                self.wfile.write(json.dumps(datos, default=json_serial).encode("utf-8"))

            elif urlParse.path == "/usuarios":
                buscar = qs.get('buscar', [''])[0]
                if buscar in ('[object Event]', 'undefined', 'null'):
                    buscar = ''
                datos = crudUsuarios.consultar(buscar)
                self.send_response(200)
                self.send_header("Content-type","application/json")
                self.end_headers()
                self.wfile.write(json.dumps(datos, default=json_serial).encode("utf-8"))

            elif urlParse.path == "/periodos":
                id_cliente = qs.get('idCliente', [''])[0]
                datos = crudImpuestos.consultar_periodos(id_cliente)
                self.send_response(200)
                self.send_header("Content-type","application/json")
                self.end_headers()
                self.wfile.write(json.dumps(datos, default=json_serial).encode("utf-8"))

            elif self.path == "/" or self.path == "/login":
                self.path = "/login.html"
                return SimpleHTTPRequestHandler.do_GET(self)
            else:
                return SimpleHTTPRequestHandler.do_GET(self)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode("utf-8"))

print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost",port),miServidor)
server.serve_forever()