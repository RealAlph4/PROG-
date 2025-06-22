from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    pedidos = relationship("Pedido", back_populates="cliente")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String, nullable=False)

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    precio = Column(Float, nullable=False, default=0.0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    descripcion = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    cantidad = Column(Integer, nullable=False)
    cliente = relationship("Cliente", back_populates="pedidos")