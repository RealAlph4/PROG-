from models import Cliente
from database import Session

def crear_cliente(nombre, correo):
    session = Session()
    if session.query(Cliente).filter_by(correo=correo).first():
        session.close()
        return False
    nuevo = Cliente(nombre=nombre, correo=correo)
    session.add(nuevo)
    session.commit()
    session.close()
    return True

def obtener_clientes():
    session = Session()
    clientes = session.query(Cliente).all()
    session.close()
    return clientes

def actualizar_cliente(id_cliente, nuevo_nombre, nuevo_correo):
    session = Session()
    cliente = session.query(Cliente).get(id_cliente)
    if cliente:
        cliente.nombre = nuevo_nombre
        cliente.correo = nuevo_correo
        session.commit()
    session.close()

def eliminar_cliente(id_cliente):
    session = Session()
    cliente = session.query(Cliente).get(id_cliente)
    if cliente:
        session.delete(cliente)
        session.commit()
    session.close()