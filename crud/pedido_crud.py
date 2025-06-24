from models import Pedido, Menu
from database import Session
from datetime import datetime
from pdf_generator import generar_boleta_pdf

def crear_pedido(cliente_id, items:list[tuple[int,int]]):
    """items = list of (menu_id, cantidad)"""
    session = Session()
    descripcion_lines = []
    total = 0.0
    cantidad_total = 0
    for mid, cant in items:
        menu = session.query(Menu).get(mid)
        if not menu:
            continue
        subtotal = menu.precio * cant
        total += subtotal
        cantidad_total += cant
        descripcion_lines.append(f"{menu.nombre} x{cant} -> ${subtotal:.0f}")
    descripcion = " | ".join(descripcion_lines)
    nuevo = Pedido(
        cliente_id=cliente_id,
        descripcion=descripcion,
        total=total,
        cantidad=cantidad_total,
        fecha=datetime.now()
    )
    session.add(nuevo)
    session.commit()

    # <<< CAMBIO: HEMOS ELIMINADO LAS SIGUIENTES LÍNEAS >>>
    # session.refresh(nuevo)
    # generar_boleta_pdf_from_db_pedido(nuevo.id)

    session.close()
    return nuevo

# El resto del archivo no necesita cambios
def generar_boleta_pdf_from_db_pedido(pedido_id:int):
    session = Session()
    pedido = session.query(Pedido).get(pedido_id)
    if not pedido: 
        return
    # build fake objeto pedido con items
    class OBJ: pass
    pedido_obj = OBJ()
    pedido_obj.items = []
    for line in pedido.descripcion.split(' | '):
        if not line.strip():
            continue
        # parse 'name x2 -> $1234'
        name_part, rest = line.split(' x')
        cantidad, _ = rest.split(' -> ')
        menu = session.query(Menu).filter_by(nombre=name_part).first()
        if not menu: continue # Ignorar si el menú no se encuentra
        item = OBJ()
        item.menu = menu
        item.cantidad = int(cantidad)
        item.calcular_subtotal = lambda m=menu, c=int(cantidad): m.precio * c
        pedido_obj.items.append(item)
        
    nombre_archivo = f"boletas/boleta_{pedido_id}.pdf"
    from pdf_generator import generar_boleta_pdf
    generar_boleta_pdf(pedido_obj, nombre_archivo)
    session.close()
    
    # <<< NUEVO: Devolvemos el nombre del archivo para mostrarlo al usuario >>>
    return nombre_archivo

def obtener_pedidos():
    session = Session()
    datos = session.query(Pedido).all()
    session.close()
    return datos