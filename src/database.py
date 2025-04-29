from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import List, Optional
import datetime
import pytz

Base = declarative_base()
date_time = pytz.timezone('America/Caracas')

# Modelo de Categoría
class Categoria(Base):
    __tablename__ = 'categorias'

    nombre_categoria = Column(String, primary_key=True)
    articulos = relationship("Articulo", back_populates="categoria_rel")

    def __repr__(self):
        return f"Categoria(nombre_categoria='{self.nombre_categoria}')"

# Modelo de Artículo
class Articulo(Base):
    __tablename__ = 'articulos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    categoria = Column(String, ForeignKey('categorias.nombre_categoria'))
    cantidad = Column(Integer)
    costo = Column(Float)
    bar_code = Column(String)

    categoria_rel = relationship("Categoria", back_populates="articulos")
    registros = relationship("Registro", back_populates="articulo_rel")

    def __repr__(self):
        return (f"Articulo(id={self.id}, nombre='{self.nombre}', "
                f"categoria='{self.categoria}', cantidad={self.cantidad}, "
                f"costo={self.costo}, codigo de barras={self.bar_code})")

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'cantidad': self.cantidad,
            'costo': self.costo,
            'bar_code': self.bar_code
        }

# Modelo de Registro
class Registro(Base):
    __tablename__ = 'registros'

    fecha_hora = Column(DateTime, primary_key=True)
    descripcion = Column(String)
    entrada_salida = Column(Boolean)  # True para entrada, False para salida
    unidad = Column(Integer)
    costo = Column(Float)
    articulo_id = Column(Integer, ForeignKey('articulos.id'))

    articulo_rel = relationship("Articulo", back_populates="registros")

    def __repr__(self):
        return (f"Registro(fecha_hora='{self.fecha_hora}', descripcion='{self.descripcion}', "
                f"entrada_salida={self.entrada_salida}, unidad={self.unidad}, "
                f"costo={self.costo}, articulo_id={self.articulo_id})")
    
    def to_dict(self):
        """Convierte el objeto Registro en un diccionario."""
        return {
            'fecha_hora': self.fecha_hora,
            'descripcion': self.descripcion,
            'entrada_salida': self.entrada_salida,
            'unidad': self.unidad,
            'costo': self.costo,
            'articulo_id': self.articulo_id
        }

# Clase para manejar la base de datos
class DatabaseManager:
    def __init__(self, db_name: str = 'inventario.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    # Métodos CRUD para Artículos

    def crear_articulo(self, nombre: str, categoria: str, cantidad: int, costo: float, bar_code: str, fecha_hora: datetime.datetime = None) -> dict:
        """Crea un nuevo artículo en la base de datos y registra la entrada inicial."""
        with self.Session() as session:
            # Verificar si la categoría existe
            cat = session.query(Categoria).filter_by(nombre_categoria=categoria).first()
            if not cat:
                cat = Categoria(nombre_categoria=categoria)
                session.add(cat)

            articulo = Articulo(
                nombre=nombre,
                categoria=categoria,
                cantidad=cantidad,
                costo=costo,
                bar_code=bar_code
            )
            session.add(articulo)
            session.flush()  # Flush para obtener el ID del artículo

            # Registrar la entrada inicial
            registro_fecha_hora = fecha_hora if fecha_hora else datetime.now(date_time) # Usar la fecha y hora proporcionada o la actual

            registro = Registro(
                articulo_id=articulo.id,
                descripcion="Creación inicial del artículo",
                entrada_salida=True,  # Entrada
                unidad=cantidad,
                costo=costo,  # Asumimos el costo inicial como el costo unitario del registro
                fecha_hora=registro_fecha_hora
            )
            session.add(registro)

            session.commit()
            return articulo.to_dict()

    def obtener_articulo(self, articulo_id: int) -> Optional[Articulo]:
        """Obtiene un artículo por su ID"""
        with self.Session() as session:
            return session.query(Articulo).filter_by(id=articulo_id).first()

    def obtener_todos_articulos(self) -> List[dict]:
        """Obtiene todos los artículos como una lista de diccionarios"""
        with self.Session() as session:
            articulos = session.query(Articulo).all()
            return [articulo.to_dict() for articulo in articulos]

    def actualizar_articulo(self, articulo_id: int, nombre: str, categoria: str, cantidad: int, costo: float, bar_code: str) -> Optional[dict]:
        """Actualiza un artículo en la base de datos."""
        with self.Session() as session:
            try:
                articulo = session.query(Articulo).filter_by(id=articulo_id).first()
                if articulo:
                    articulo.nombre = nombre
                    articulo.cantidad = cantidad
                    articulo.costo = costo
                    articulo.bar_code = bar_code

                    # Verificar y actualizar la categoría
                    cat = session.query(Categoria).filter_by(nombre_categoria=categoria).first()
                    if not cat:
                        cat = Categoria(nombre_categoria=categoria)
                        session.add(cat)
                    articulo.categoria = categoria  # Asignar el nombre de la categoría

                    session.commit()
                    session.refresh(articulo)
                    return articulo.to_dict()
                return None  # Retorna None si el artículo no fue encontrado
            except Exception as e:
                session.rollback()  # En caso de error, revierte la transacción
                print(f"Error al actualizar el artículo con ID {articulo_id}: {e}")
                return None

    def eliminar_articulo(self, articulo_id: int) -> bool:
        """Elimina un artículo por su ID"""
        with self.Session() as session:
            articulo = session.query(Articulo).filter_by(id=articulo_id).first()
            if articulo:
                session.delete(articulo)
                session.commit()
                return True
            return False

    # Métodos CRUD para Categorías

    def crear_categoria(self, nombre_categoria: str) -> Categoria:
        """Crea una nueva categoría"""
        with self.Session() as session:
            categoria = Categoria(nombre_categoria=nombre_categoria)
            session.add(categoria)
            session.commit()
            return categoria

    def obtener_categoria(self, nombre_categoria: str) -> Optional[Categoria]:
        """Obtiene una categoría por su nombre"""
        with self.Session() as session:
            return session.query(Categoria).filter_by(nombre_categoria=nombre_categoria).first()

    def obtener_todas_categorias(self) -> List[Categoria]:
        """Obtiene todas las categorías"""
        with self.Session() as session:
            return session.query(Categoria).all()

    def actualizar_categoria(self, nombre_actual: str, nuevo_nombre: str) -> Optional[Categoria]:
        """Actualiza el nombre de una categoría"""
        with self.Session() as session:
            categoria = session.query(Categoria).filter_by(nombre_categoria=nombre_actual).first()
            if categoria:
                # Actualizar también los artículos asociados
                articulos = session.query(Articulo).filter_by(categoria=nombre_actual).all()
                for articulo in articulos:
                    articulo.categoria = nuevo_nombre

                categoria.nombre_categoria = nuevo_nombre
                session.commit()
                return categoria
            return None

    def eliminar_categoria(self, nombre_categoria: str) -> bool:
        """Elimina una categoría (solo si no tiene artículos asociados)"""
        with self.Session() as session:
            categoria = session.query(Categoria).filter_by(nombre_categoria=nombre_categoria).first()
            if categoria:
                # Verificar si hay artículos asociados
                articulos = session.query(Articulo).filter_by(categoria=nombre_categoria).count()
                if articulos > 0:
                    raise ValueError("No se puede eliminar la categoría porque tiene artículos asociados")

                session.delete(categoria)
                session.commit()
                return True
            return False

    def obtener_articulos_por_categoria(self, nombre_categoria: str) -> List[dict]:
        """Obtiene todos los artículos de una categoría específica y los devuelve como diccionarios."""
        with self.Session() as session:
            articulos = session.query(Articulo).filter_by(categoria=nombre_categoria).all()
            return [articulo.to_dict() for articulo in articulos]

    # Métodos para la tabla Registro

    def registrar_movimiento(self, articulo_id: int, descripcion: str, entrada: bool, unidad: int, costo: float, fecha_hora: datetime.datetime = None):
        """Registra un movimiento de inventario para un artículo."""
        with self.Session() as session:
            registro = Registro(
                articulo_id=articulo_id,
                descripcion=descripcion,
                entrada_salida=entrada,
                unidad=unidad,
                costo=costo,
                fecha_hora=fecha_hora if fecha_hora else datetime.datetime.now(date_time)
            )
            session.add(registro)
            session.commit()

    def obtener_registros_por_articulo(self, articulo_id: int) -> List[dict]:
        """Obtiene todos los registros de movimiento para un artículo específico como diccionarios."""
        with self.Session() as session:
            registros = session.query(Registro).filter_by(articulo_id=articulo_id).all()
        return [registro.to_dict() for registro in registros]

    def obtener_registro(self, registro_id: datetime.datetime) -> Optional[Registro]:
        """Obtiene un registro de movimiento por su fecha y hora."""
        with self.Session() as session:
            return session.query(Registro).filter_by(fecha_hora=registro_id).first()

    def eliminar_registro(self, registro_fecha_hora: datetime.datetime) -> bool:
        """Elimina un registro por su fecha y hora."""
        with self.Session() as session:
            registro = session.query(Registro).filter_by(fecha_hora=registro_fecha_hora).first()
            if registro:
                session.delete(registro)
                session.commit()
                return True
            return False
        
    def eliminar_todo_registro(self, articulo_id: int) -> bool:
        """Elimina todos los registros asociados a un artículo específico."""
        with self.Session() as session:
            registros = session.query(Registro).filter_by(
                articulo_id=articulo_id).all()
            if registros:
                for registro in registros:
                    session.delete(registro)
                session.commit()
                return True
            return False
        
    def obtener_registros_por_categoria(self, category_nombre: str) -> List[Articulo]:
        """Obtiene todos los registros de artículos que pertenecen a la categoría especificada por nombre."""
        with self.Session() as session:
            return session.query(Articulo).filter(Articulo.categoria == category_nombre).all()

    def obtener_categorias(self) -> List[Categoria]:
        """Obtiene todas las categorías."""
        with self.Session() as session:
            return session.query(Categoria).all()