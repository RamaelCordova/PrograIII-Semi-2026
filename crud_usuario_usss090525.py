# pyrefly: ignore [missing-import]
from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_usuario_usss090525:
    def __init__(self):
        self.tabla = "usss090525"
        self._inicializar_usuario_admin()

    def _inicializar_usuario_admin(self):
        """Si la tabla está vacía, crea un usuario inicial por defecto para poder iniciar sesión."""
        try:
            sql_check = f"SELECT COUNT(*) AS total FROM {self.tabla}"
            resultado = db.consultar(sql_check)
            if resultado and resultado[0]['total'] == 0:
                sql_insert = f"""
                    INSERT INTO {self.tabla}(usuario, clave, nombre, direccion, telefono)
                    VALUES(%s, %s, %s, %s, %s)
                """
                db.ejecutar(sql_insert, ('admin', 'admin123', 'Administrador del Sistema', 'San Salvador, El Salvador', '7777-8888'))
                print("Usuario inicial 'admin' creado exitosamente.")
        except Exception as e:
            print(f"Nota en inicialización de usuario: {e}")

    def consultar(self, buscar=""):
        """Consulta y búsqueda de usuarios en la tabla usss090525 por nombre, usuario o teléfono."""
        sql = f"""
            SELECT idUsuario, usuario, clave, nombre, direccion, telefono 
            FROM {self.tabla} 
            WHERE nombre LIKE %s OR usuario LIKE %s OR telefono LIKE %s 
            ORDER BY idUsuario DESC
        """
        param = f"%{buscar}%"
        return db.consultar(sql, (param, param, param))

    def crud_usuario_usss090525(self, datos):
        """
        Procesa los datos enviados desde el cliente para almacenar,
        modificar o eliminar registros en la tabla usss090525.
        """
        try:
            accion = datos.get('accion', 'nuevo')

            if accion == 'nuevo':
                sql = f"""
                    INSERT INTO {self.tabla}(usuario, clave, nombre, direccion, telefono)
                    VALUES(%s, %s, %s, %s, %s)
                """
                valores = (
                    datos.get('usuario', '').strip(),
                    datos.get('clave', '').strip(),
                    datos.get('nombre', '').strip(),
                    datos.get('direccion', '').strip(),
                    datos.get('telefono', '').strip()
                )
            elif accion == 'modificar':
                sql = f"""
                    UPDATE {self.tabla} 
                    SET usuario=%s, clave=%s, nombre=%s, direccion=%s, telefono=%s
                    WHERE idUsuario=%s
                """
                valores = (
                    datos.get('usuario', '').strip(),
                    datos.get('clave', '').strip(),
                    datos.get('nombre', '').strip(),
                    datos.get('direccion', '').strip(),
                    datos.get('telefono', '').strip(),
                    datos.get('idUsuario')
                )
            elif accion == 'eliminar':
                sql = f"DELETE FROM {self.tabla} WHERE idUsuario=%s"
                valores = (datos.get('idUsuario'),)
            else:
                return "Acción no válida"

            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error en la tabla usss090525: {e}"
        except Exception as e:
            return f"Error inesperado: {e}"

    def administrar(self, datos):
        """Alias de compatibilidad con crud_clientes."""
        return self.crud_usuario_usss090525(datos)

    def autenticar(self, usuario, clave):
        """
        Valida las credenciales en la base de datos (tabla usss090525).
        Si no está registrado, deniega el acceso al sistema.
        """
        try:
            usuario = str(usuario).strip()
            clave = str(clave).strip()

            if not usuario or not clave:
                return {'acceso': False, 'msg': 'Ingrese usuario y contraseña'}

            sql = f"""
                SELECT idUsuario, usuario, nombre, direccion, telefono 
                FROM {self.tabla} 
                WHERE usuario = %s AND clave = %s
            """
            resultado = db.consultar(sql, (usuario, clave))

            if resultado and len(resultado) > 0:
                usuario_info = resultado[0]
                return {
                    'acceso': True,
                    'msg': 'Acceso concedido',
                    'usuario': usuario_info
                }
            else:
                return {
                    'acceso': False,
                    'msg': 'Acceso denegado: Usuario o contraseña no registrados en el sistema.'
                }
        except Error as e:
            return {'acceso': False, 'msg': f'Error de base de datos: {e}'}
        except Exception as e:
            return {'acceso': False, 'msg': f'Error inesperado: {e}'}
