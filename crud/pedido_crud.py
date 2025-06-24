from models import Pedido, Menu, Ingrediente
from database import Session
from datetime import datetime
from pdf_generator import generar_boleta_pdf
import json
import os
from collections import Counter

def crear_pedido(cliente_id, items:list[tuple[int,int]]):
    """
    Crea un nuevo pedido, guarda los detalles y descuenta los ingredientes del stock.
    items = list of (menu_id, cantidad)
    """
    session = Session()
    try:
        # Lógica de descuento de ingredientes
        ingredientes_requeridos = Counter()
        for mid, cant in items:
            ruta_receta = f'recetas/{mid}.json'
            if not os.path.exists(ruta_receta): continue
            with open(ruta_receta, 'r', encoding='utf-8') as f:
                receta = json.load(f)
            for ing_receta in receta:
                ingredientes_requeridos[ing_receta['id']] += ing_receta['cant'] * cant

        ids_requeridos = list(ingredientes_requeridos.keys())
        if ids_requeridos:
            ingredientes_db = session.query(Ingrediente).filter(Ingrediente.id.in_(ids_requeridos)).all()
            stock_map = {ing.id: ing for ing in ingredientes_db}
            for ing_id, cant_total_req in ingredientes_requeridos.items():
                ing_db = stock_map.get(ing_id)
                if not ing_db or ing_db.cantidad < cant_total_req:
                    raise Exception(f"Stock insuficiente para el ingrediente '{ing_db.nombre if ing_db else 'ID '+str(ing_id)}'. Pedido no procesado.")
                ing_db.cantidad -= cant_total_req
        
        # Lógica original de crear_pedido
        descripcion_lines = []
        total = 0.0
        cantidad_total_items = 0
        for mid, cant in items:
            menu = session.query(Menu).get(mid)
            if not menu: continue
            subtotal = menu.precio * cant
            total += subtotal
            cantidad_total_items += cant
            descripcion_lines.append(f"{menu.nombre} x{cant} -> ${subtotal:.0f}")
        
        descripcion = " | ".join(descripcion_lines)
        nuevo_pedido = Pedido(cliente_id=cliente_id, descripcion=descripcion, total=total, cantidad=cantidad_total_items, fecha=datetime.now())
        session.add(nuevo_pedido)
        session.commit()
        return nuevo_pedido
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def generar_boleta_pdf_from_db_pedido(pedido_id:int):
    session = Session()
    pedido = session.query(Pedido).get(pedido_id)
    if not pedido: 
        return
    class OBJ: pass
    pedido_obj = OBJ()
    pedido_obj.items = []
    for line in pedido.descripcion.split(' | '):
        if not line.strip():
            continue
        name_part, rest = line.split(' x')
        cantidad, _ = rest.split(' -> ')
        menu = session.query(Menu).filter_by(nombre=name_part).first()
        if not menu: continue
        item = OBJ()
        item.menu = menu
        item.cantidad = int(cantidad)
        item.calcular_subtotal = lambda m=menu, c=int(cantidad): m.precio * c
        pedido_obj.items.append(item)
        
    nombre_archivo = f"boletas/boleta_{pedido_id}.pdf"
    from pdf_generator import generar_boleta_pdf
    generar_boleta_pdf(pedido_obj, nombre_archivo)
    session.close()
    return nombre_archivo

def obtener_pedidos():
    session = Session()
    datos = session.query(Pedido).all()
    session.close()
    return datos

def eliminar_pedido_por_id(pedido_id: int):
    """
    Elimina un pedido y devuelve los ingredientes al stock.
    Retorna True si fue exitoso, False en caso contrario.
    """
    if not pedido_id:
        return False
        
    session = Session()
    try:
        pedido_a_eliminar = session.query(Pedido).get(pedido_id)
        if not pedido_a_eliminar:
            return False

        # Lógica para devolver ingredientes al stock
        items_pedido = []
        try:
            items_str = pedido_a_eliminar.descripcion.split(' | ')
            for item_str in items_str:
                nombre_part, resto = item_str.rsplit(' x', 1)
                cantidad_str, _ = resto.split(' -> $')
                items_pedido.append((nombre_part.strip(), int(cantidad_str)))
        except Exception:
            raise Exception("No se pudo procesar la descripción del pedido para devolver el stock.")

        ingredientes_a_devolver = Counter()
        for menu_nombre, cantidad in items_pedido:
            menu = session.query(Menu).filter_by(nombre=menu_nombre).first()
            if not menu: continue
            ruta_receta = f'recetas/{menu.id}.json'
            if not os.path.exists(ruta_receta): continue
            with open(ruta_receta, 'r', encoding='utf-8') as f:
                receta = json.load(f)
            for ing_receta in receta:
                ingredientes_a_devolver[ing_receta['id']] += ing_receta['cant'] * cantidad

        if ingredientes_a_devolver:
            ids = list(ingredientes_a_devolver.keys())
            ingredientes_db = session.query(Ingrediente).filter(Ingrediente.id.in_(ids)).all()
            for ing_db in ingredientes_db:
                ing_db.cantidad += ingredientes_a_devolver[ing_db.id]

        session.delete(pedido_a_eliminar)
        session.commit()
        return True
        
    except Exception as e:
        print(f"Error al eliminar el pedido {pedido_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()