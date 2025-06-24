from models import Ingrediente
from database import Session
import json
import os
from collections import Counter

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

def verificar_y_obtener_faltantes(carrito: list[tuple[int, int]]):
    """
    Verifica si hay suficientes ingredientes para los menús en el carrito.
    - carrito: una lista de tuplas (menu_id, cantidad).
    - Retorna: una lista de strings con los nombres de los ingredientes faltantes.
               Si no falta nada, retorna una lista vacía.
    """
    if not carrito:
        return []

    session = Session()
    try:
        ingredientes_requeridos = Counter()
        for menu_id, cantidad in carrito:
            ruta_receta = f'recetas/{menu_id}.json'
            if not os.path.exists(ruta_receta):
                continue
            with open(ruta_receta, 'r', encoding='utf-8') as f:
                receta = json.load(f)
            
            for ing_receta in receta:
                ingredientes_requeridos[ing_receta['id']] += ing_receta['cant'] * cantidad

        if not ingredientes_requeridos:
            return []

        ids_requeridos = list(ingredientes_requeridos.keys())
        stock_actual = session.query(Ingrediente).filter(Ingrediente.id.in_(ids_requeridos)).all()
        stock_map = {ing.id: ing for ing in stock_actual}

        faltantes = []
        for ing_id, cantidad_requerida in ingredientes_requeridos.items():
            ing_en_stock = stock_map.get(ing_id)
            if not ing_en_stock or ing_en_stock.cantidad < cantidad_requerida:
                nombre_ing = "Desconocido"
                if ing_en_stock:
                    nombre_ing = ing_en_stock.nombre
                else: 
                    ing_faltante = session.query(Ingrediente).get(ing_id)
                    if ing_faltante:
                        nombre_ing = ing_faltante.nombre
                faltantes.append(nombre_ing)
                
        return faltantes
    finally:
        session.close()