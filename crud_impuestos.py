from decimal import Decimal, ROUND_HALF_UP
import math
import conexion

db = conexion.Conexion()

class crud_impuestos:
    def calcular_impuesto(self, balance, producto_codigo):
        try:
            balance = Decimal(str(balance))
            if balance <= 0:
                return {"error": "Ingrese un balance mayor que cero."}

            # Consulta parametrizada en MySQL
            sql = "SELECT * FROM tarifas WHERE producto_codigo = %s AND desde <= %s AND hasta >= %s"
            tarifas = db.consultar(sql, (producto_codigo, float(balance), float(balance)))

            if not tarifas:
                return {"error": "No existe una tarifa configurada para el balance indicado."}
            
            if len(tarifas) > 1:
                return {"error": "Existe más de una tarifa aplicable. Corrija la tabla tarifaria."}

            tarifa = tarifas[0]
            porcentaje = Decimal(str(tarifa['porcentaje']))
            precio_base = Decimal(str(tarifa['precio_base']))
            adicional = Decimal(str(tarifa['adicional']))
            desde = Decimal(str(tarifa['desde']))
            hasta = Decimal(str(tarifa['hasta']))
            
            excedente = Decimal('0')
            bloques = 0

            if porcentaje > 0:
                impuesto = balance * (porcentaje / Decimal('100.0'))
            else:
                # Ajuste del límite base para rangos mayores a 0.01 (ej. 500.01 -> base 500.00)
                base_rango = (desde - Decimal('0.01')) if desde > Decimal('0.01') else Decimal('0.00')
                excedente = balance - base_rango
                
                if excedente > 0:
                    bloques = math.ceil(excedente / Decimal('1000.0'))
                
                impuesto = precio_base + (Decimal(bloques) * adicional)

            impuesto = impuesto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            tarifa_convertida = {
                "id": tarifa['id'],
                "producto_codigo": str(tarifa['producto_codigo']),
                "desde": float(desde),
                "hasta": float(hasta),
                "precio_base": float(precio_base),
                "adicional": float(adicional),
                "porcentaje": float(porcentaje),
                "excedente": float(excedente),
                "bloques": int(bloques)
            }

            return {
                "msg": "ok",
                "impuesto_mensual": float(impuesto),
                "tarifa_aplicada": tarifa_convertida
            }
        except Exception as e:
            return {"error": f"Error en cálculo: {e}"}

    def guardar_periodo(self, datos):
        try:
            if not datos.get('idCliente'):
                return "Debe seleccionar un cliente válido."

            if datos['fecha_desde'] >= datos['fecha_hasta']:
                return "La fecha Hasta debe ser posterior a la fecha Desde."

            sql_overlap = """
                SELECT idPeriodo FROM periodos_impuestos 
                WHERE idCliente = %s 
                AND producto_codigo = %s
                AND estado = 'Vigente'
                AND fecha_desde < %s 
                AND fecha_hasta > %s
            """
            overlap = db.consultar(sql_overlap, (datos['idCliente'], datos['producto_codigo'], datos['fecha_hasta'], datos['fecha_desde']))
            if overlap:
                return "El período indicado se superpone con un período existente."

            sql_update = """
                UPDATE periodos_impuestos 
                SET estado = 'Histórico' 
                WHERE idCliente = %s AND producto_codigo = %s
            """
            db.ejecutar(sql_update, (datos['idCliente'], datos['producto_codigo']))

            sql_insert = """
            INSERT INTO periodos_impuestos(idCliente, producto_codigo, fecha_desde, fecha_hasta, balance, precio_mensual, estado)
            VALUES(%s, %s, %s, %s, %s, %s, 'Vigente')
            """
            valores = (datos['idCliente'], datos['producto_codigo'], datos['fecha_desde'], datos['fecha_hasta'], datos['balance'], datos['precio_mensual'])
            
            return db.ejecutar(sql_insert, valores)
        except Exception as e:
            return f"Error al guardar el periodo: {e}"

    def consultar_periodos(self, idCliente):
        try:
            sql = """
                SELECT idPeriodo, producto_codigo, fecha_desde, fecha_hasta, balance, precio_mensual, estado 
                FROM periodos_impuestos 
                WHERE idCliente = %s 
                ORDER BY fecha_desde DESC
            """
            periodos = db.consultar(sql, (idCliente,)) or []
            for p in periodos:
                if 'balance' in p and p['balance'] is not None:
                    p['balance'] = float(p['balance'])
                if 'precio_mensual' in p and p['precio_mensual'] is not None:
                    p['precio_mensual'] = float(p['precio_mensual'])
                if 'fecha_desde' in p and p['fecha_desde'] is not None:
                    p['fecha_desde'] = str(p['fecha_desde'])
                if 'fecha_hasta' in p and p['fecha_hasta'] is not None:
                    p['fecha_hasta'] = str(p['fecha_hasta'])
            return periodos
        except Exception as e:
            print(f"Error al consultar periodos: {e}")
            return []