from models import Menu
from database import Session

def crear_menu(nombre, descripcion, precio):
    session = Session()
    nuevo = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
    session.add(nuevo)
    session.commit()
    session.close()

def obtener_menus():
    session = Session()
    menus = session.query(Menu).all()
    session.close()
    return menus

def actualizar_menu(id_menu, nombre, descripcion):
    session = Session()
    menu = session.query(Menu).get(id_menu)
    if menu:
        menu.nombre = nombre
        menu.descripcion = descripcion
        session.commit()
    session.close()

def eliminar_menu(id_menu):
    session = Session()
    menu = session.query(Menu).get(id_menu)
    if menu:
        session.delete(menu)
        session.commit()
    session.close()