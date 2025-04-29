import datetime
import pytz
from database import DatabaseManager

class InventoryController:
    def __init__(self, db_path='inventario.db'):
        self.db_manager = DatabaseManager(db_path)

    def crear_articulo(self, nombre: str, categoria: str, cantidad: int, costo: float, bar_code: str, fecha_hora: datetime.datetime = None):
        return self.db_manager.crear_articulo(nombre, categoria, cantidad, costo, bar_code, fecha_hora)

    def obtener_articulo(self, articulo_id: int):
        return self.db_manager.obtener_articulo(articulo_id)

    def obtener_todos_articulos(self):
        return self.db_manager.obtener_todos_articulos()

    def actualizar_articulo(self, articulo_id: int, nombre: str, categoria: str, cantidad: int, costo: float, bar_code: str):
        """Llama al método de la base de datos para actualizar un artículo."""
        return self.db_manager.actualizar_articulo(articulo_id, nombre, categoria, cantidad, costo, bar_code)

    def eliminar_articulo(self, articulo_id: int):
        return self.db_manager.eliminar_articulo(articulo_id)

    def crear_categoria(self, nombre_categoria: str):
        return self.db_manager.crear_categoria(nombre_categoria)

    def obtener_categoria(self, nombre_categoria: str):
        return self.db_manager.obtener_categoria(nombre_categoria)

    def obtener_todas_categorias(self):
        return self.db_manager.obtener_todas_categorias()

    def actualizar_categoria(self, nombre_actual: str, nuevo_nombre: str):
        return self.db_manager.actualizar_categoria(nombre_actual, nuevo_nombre)

    def eliminar_categoria(self, nombre_categoria: str):
        try:
            return self.db_manager.eliminar_categoria(nombre_categoria)
        except ValueError as e:
            print(e)
            return False

    def obtener_articulos_por_categoria(self, nombre_categoria: str):
        return self.db_manager.obtener_articulos_por_categoria(nombre_categoria)

    def calcular_cantidad_actual(self, articulo_id: int) -> int:
        """Calcula la cantidad actual de un artículo basándose en los registros."""
        registros = self.db_manager.obtener_registros_por_articulo(articulo_id)
        cantidad_total = 0
        for registro in registros:
            if registro['entrada_salida']:
                cantidad_total += registro['unidad']
            else:
                cantidad_total -= registro['unidad']
        return cantidad_total

    def calcular_costo_promedio(self, articulo_id: int) -> float:
        """Calcula el costo promedio ponderado de un artículo (basado solo en entradas)."""
        registros = self.obtener_registros_por_articulo(articulo_id)
        total_valor = 0
        total_cantidad = 0

        for registro in registros:
            if registro['entrada_salida']:  # Entrada
                total_valor += registro['unidad'] * registro['costo']
                total_cantidad += registro['unidad']
        if total_cantidad > 0:
            return total_valor / total_cantidad
        return 0.0

    def calcular_costo_promedio_articulo(self, articulo_id):
        cantidad_total_acumulada = 0
        valor_total_acumulado = 0
        costo_promedio = 0.0

        registros = self.obtener_registros_por_articulo(articulo_id)
        registros_ordenados = sorted(registros, key=lambda x: x['fecha_hora'])

        for registro in registros_ordenados:
            costo_movimiento = registro['unidad'] * registro['costo']

            if registro['entrada_salida']:
                cantidad_total_acumulada += registro['unidad']
                valor_total_acumulado += costo_movimiento
            else:
                cantidad_total_acumulada -= registro['unidad']
                valor_total_acumulado -= costo_movimiento

            if cantidad_total_acumulada != 0:
                costo_promedio = valor_total_acumulado / cantidad_total_acumulada

        return costo_promedio

    # Métodos para la tabla Registro

    def registrar_movimiento(self, articulo_id: int, descripcion: str, entrada: bool, unidad: int, costo: float, fecha_hora: datetime.datetime = None):
        """Registra un movimiento de inventario para un artículo."""
        fecha_registro = fecha_hora if fecha_hora else datetime.datetime.now(pytz.timezone('America/Caracas'))
        return self.db_manager.registrar_movimiento(articulo_id, descripcion, entrada, unidad, costo, fecha_hora=fecha_registro)

    def obtener_registros_por_articulo(self, articulo_id: int):
        """Obtiene todos los registros de movimiento para un artículo específico."""
        return self.db_manager.obtener_registros_por_articulo(articulo_id)

    def obtener_registro(self, registro_id):
        """Obtiene un registro de movimiento por su fecha y hora."""
        return self.db_manager.obtener_registro(registro_id)

    def eliminar_registro(self, registro_fecha_hora: datetime.datetime):
        """Elimina un registro por su fecha y hora."""
        return self.db_manager.eliminar_registro(registro_fecha_hora)
    
    def eliminar_todo_registro(self, articulo_id: int):
        return self.db_manager.eliminar_todo_registro(articulo_id)
    
    def obtener_registros_por_categoria(self, category_nombre: str):
       return self.db_manager.obtener_registros_por_categoria(category_nombre)

    def obtener_categorias(self):
        return self.db_manager.obtener_categorias()