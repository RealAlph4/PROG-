from models import Ingrediente
from database import Session

def crear_ingrediente(nombre, tipo, cantidad, unidad):
    session = Session()
    if session.query(Ingrediente).filter_by(nombre=nombre).first():
        session.close()
        return False
    nuevo = Ingrediente(nombre=nombre, tipo=tipo, cantidad=cantidad, unidad=unidad)
    session.add(nuevo)
    session.commit()
    session.close()
    return True

def obtener_ingredientes():
    session = Session()
    ingredientes = session.query(Ingrediente).all()
    session.close()
    return ingredientes

def actualizar_ingrediente(id_ing, nombre, tipo, cantidad, unidad):
    session = Session()
    ingrediente = session.query(Ingrediente).get(id_ing)
    if ingrediente:
        ingrediente.nombre = nombre
        ingrediente.tipo = tipo
        ingrediente.cantidad = cantidad
        ingrediente.unidad = unidad
        session.commit()
    session.close()

def eliminar_ingrediente(id_ing):
    session = Session()
    ingrediente = session.query(Ingrediente).get(id_ing)
    if ingrediente:
        session.delete(ingrediente)
        session.commit()
    session.close()