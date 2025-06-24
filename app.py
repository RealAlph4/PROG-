import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import json
import os

from graficos import GraficosFrame
from crud.cliente_crud import crear_cliente, obtener_clientes, actualizar_cliente, eliminar_cliente
from crud.ingrediente_crud import crear_ingrediente, obtener_ingredientes, verificar_y_obtener_faltantes
from crud.menu_crud import crear_menu, obtener_menus
from crud.pedido_crud import crear_pedido, obtener_pedidos, generar_boleta_pdf_from_db_pedido, eliminar_pedido_por_id


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# -------------------------------------------
# CLASE PRINCIPAL DE LA APLICACION
# -------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Configuracion de la ventana principal ---
        self.title("Sistema de Gestion de Restaurante")
        self.geometry("1100x750")

        # --- Creacion del sistema de pestañas (Tabs) ---
        self.tabview = ctk.CTkTabview(self, width=1080)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Definicion de las pestañas ---
        self.clientes_tab = self.tabview.add("Clientes")
        self.ingredientes_tab = self.tabview.add("Ingredientes")
        self.menus_tab = self.tabview.add("Menús")
        self.pedidos_tab = self.tabview.add("Pedidos")
        self.graficos_tab = self.tabview.add("Gráficos")

        # --- Inicializacion del contenido de cada pestaña ---
        self.init_clientes_tab()
        self.init_ingredientes_tab()
        self.init_menus_tab()
        self.init_pedidos_tab()
        self.init_graficos_tab()

    # -------------------------------------------------------------------
    # METODOS PARA LA PESTAÑA DE CLIENTES
    # -------------------------------------------------------------------

    def init_clientes_tab(self):
        # --- Widgets de entrada para datos del cliente ---
        self.entry_nombre = ctk.CTkEntry(self.clientes_tab, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=5)
        self.entry_correo = ctk.CTkEntry(self.clientes_tab, placeholder_text="Correo")
        self.entry_correo.pack(pady=5)
        
        # --- Botones de accion (Agregar, Editar, etc.) ---
        btn_frame = ctk.CTkFrame(self.clientes_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Cliente", command=self.agregar_cliente).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Editar Cliente", command=self.editar_cliente).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Lista", command=self.cargar_clientes).grid(row=0, column=3, padx=5)
        
        # --- Tabla (Treeview) para mostrar los clientes ---
        tree_frame = ctk.CTkFrame(self.clientes_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)
        self.tree_clientes = ttk.Treeview(tree_frame, columns=("id","nombre","correo"), show="headings")
        for col, hdr in zip(("id","nombre","correo"),("ID","Nombre","Correo")):
            self.tree_clientes.heading(col, text=hdr)
            self.tree_clientes.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=vsb.set)
        self.tree_clientes.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # --- Evento de seleccion y carga inicial ---
        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente_evento)
        self.cliente_seleccionado_id = None
        self.cargar_clientes()

    def cargar_clientes(self):
        # Carga los clientes desde la DB y los muestra en la tabla
        self.clientes = obtener_clientes()
        for i in self.tree_clientes.get_children(): self.tree_clientes.delete(i)
        for c in self.clientes: self.tree_clientes.insert('', 'end', iid=c.id, values=(c.id, c.nombre, c.correo))
        self.cliente_seleccionado_id = None
        self.entry_nombre.delete(0,'end')
        self.entry_correo.delete(0,'end')

    def seleccionar_cliente_evento(self, event):
        # Se activa al seleccionar un cliente de la tabla.
        # Carga sus datos en los campos de entrada.
        seleccion = self.tree_clientes.selection()
        if not seleccion: return
        cid = int(seleccion[0])
        cliente = next((c for c in self.clientes if c.id == cid), None)
        if cliente:
            self.entry_nombre.delete(0, 'end')
            self.entry_nombre.insert(0, cliente.nombre)
            self.entry_correo.delete(0, 'end')
            self.entry_correo.insert(0, cliente.correo)
            self.cliente_seleccionado_id = cliente.id

    def agregar_cliente(self):
        # Valida los datos y crea un nuevo cliente.
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip().lower()
        if not nombre or not correo:
            messagebox.showerror("Error", "Debe ingresar nombre y correo")
            return
        if any(c.correo.lower() == correo for c in obtener_clientes()):
            messagebox.showerror("Error", "Correo duplicado")
            return
        crear_cliente(nombre, correo)
        self.cargar_clientes()
        self.cargar_comboboxes() # Actualiza los combos en otras pestañas

    def editar_cliente(self):
        # Edita el cliente seleccionado con los nuevos datos.
        if self.cliente_seleccionado_id is None:
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip().lower()
        if not nombre or not correo:
            messagebox.showerror("Error", "Complete nombre y correo")
            return
        # Evita duplicar el correo con otro cliente existente
        for c in obtener_clientes():
            if c.correo.lower() == correo and c.id != self.cliente_seleccionado_id:
                messagebox.showerror("Error", "Correo ya registrado a otro cliente")
                return
        actualizar_cliente(self.cliente_seleccionado_id, nombre, correo)
        self.cargar_clientes()

    def eliminar_cliente(self):
        # Elimina el cliente seleccionado de la DB.
        if self.cliente_seleccionado_id is None:
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar cliente seleccionado?"):
            return
        eliminar_cliente(self.cliente_seleccionado_id)
        self.cargar_clientes()
        self.cargar_comboboxes()

    # -------------------------------------------------------------------
    # METODOS PARA LA PESTAÑA DE INGREDIENTES
    # -------------------------------------------------------------------

    def init_ingredientes_tab(self):
        # --- Widgets de entrada para datos de ingredientes ---
        self.ing_nombre = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Nombre")
        self.ing_nombre.pack(pady=5)
        self.ing_tipo = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Tipo")
        self.ing_tipo.pack(pady=5)
        self.ing_cantidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Cantidad")
        self.ing_cantidad.pack(pady=5)
        self.ing_unidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Unidad (g, u, ml)")
        self.ing_unidad.pack(pady=5)
        
        # --- Botones de accion ---
        ctk.CTkButton(self.ingredientes_tab, text="Agregar Ingrediente", command=self.agregar_ingrediente).pack(pady=5)
        ctk.CTkButton(self.ingredientes_tab, text="Cargar Ingredientes", command=self.cargar_ingredientes).pack(pady=5)
        
        # --- Tabla (Treeview) para mostrar los ingredientes ---
        frame = ctk.CTkFrame(self.ingredientes_tab)
        frame.pack(expand=True, fill="both", pady=10)
        self.tree_ingredientes = ttk.Treeview(frame, columns=("id", "nombre", "tipo", "cantidad", "unidad"), show="headings")
        for col, hdr in zip(("id", "nombre", "tipo", "cantidad", "unidad"), ("ID", "Nombre", "Tipo", "Cant", "Unidad")):
            self.tree_ingredientes.heading(col, text=hdr)
            self.tree_ingredientes.column(col, anchor="center")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_ingredientes.yview)
        self.tree_ingredientes.configure(yscrollcommand=vsb.set)
        self.tree_ingredientes.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # --- Carga inicial de datos ---
        self.cargar_ingredientes()

    def cargar_ingredientes(self):
        # Carga los ingredientes y los muestra en la tabla.
        ingredientes = obtener_ingredientes()
        for i in self.tree_ingredientes.get_children(): self.tree_ingredientes.delete(i)
        for ing in ingredientes:
            self.tree_ingredientes.insert('', 'end', iid=ing.id, values=(ing.id, ing.nombre, ing.tipo, ing.cantidad, ing.unidad))

    def agregar_ingrediente(self):
        # Agrega un nuevo ingrediente a la DB.
        nombre = self.ing_nombre.get()
        tipo = self.ing_tipo.get()
        cantidad = self.ing_cantidad.get()
        unidad = self.ing_unidad.get()
        try:
            cantidad_float = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Cantidad invalida")
            return
        if crear_ingrediente(nombre, tipo, cantidad_float, unidad):
            self.cargar_ingredientes()
            self.cargar_ingredientes_combo()
        else:
            messagebox.showwarning("Error", "Ingrediente ya existe")

    # -------------------------------------------------------------------
    # METODOS PARA LA PESTAÑA DE MENUS
    # -------------------------------------------------------------------

    def init_menus_tab(self):
        # --- Widgets de entrada para datos del menu ---
        self.menu_nombre = ctk.CTkEntry(self.menus_tab, placeholder_text="Nombre del plato")
        self.menu_nombre.pack(pady=5)
        self.menu_desc = ctk.CTkEntry(self.menus_tab, placeholder_text="Descripcion")
        self.menu_desc.pack(pady=5)
        self.menu_precio = ctk.CTkEntry(self.menus_tab, placeholder_text="Precio ($)")
        self.menu_precio.pack(pady=5)
        
        # --- Frame para añadir ingredientes a la receta ---
        ingr_frame = ctk.CTkFrame(self.menus_tab)
        ingr_frame.pack(pady=5)
        ctk.CTkLabel(ingr_frame, text="Ingrediente").grid(row=0, column=0, padx=5)
        self.combo_ing = ttk.Combobox(ingr_frame, state="readonly", width=25)
        self.combo_ing.grid(row=0, column=1, padx=5)
        self.entry_ing_cant = ctk.CTkEntry(ingr_frame, placeholder_text="Cant.", width=70)
        self.entry_ing_cant.grid(row=0, column=2, padx=5)
        ctk.CTkButton(ingr_frame, text="Añadir a Receta", command=self.anadir_ing_receta).grid(row=0, column=3, padx=5)
        
        # --- Tabla para mostrar la receta que se esta creando ---
        recipe_frame = ctk.CTkFrame(self.menus_tab)
        recipe_frame.pack(pady=5, fill="x")
        self.tree_receta = ttk.Treeview(recipe_frame, columns=("ing", "cant", "unidad"), show="headings", height=6)
        for col, hdr in zip(("ing", "cant", "unidad"), ("Ingrediente", "Cant", "Unidad")):
            self.tree_receta.heading(col, text=hdr)
            self.tree_receta.column(col, anchor="center")
        vsb_receta = ttk.Scrollbar(recipe_frame, orient="vertical", command=self.tree_receta.yview)
        self.tree_receta.configure(yscrollcommand=vsb_receta.set)
        self.tree_receta.pack(side="left", fill="both", expand=True)
        vsb_receta.pack(side="right", fill="y")
        
        # --- Botones de accion para el menu ---
        btn_frame_menu = ctk.CTkFrame(self.menus_tab)
        btn_frame_menu.pack(pady=5)
        ctk.CTkButton(btn_frame_menu, text="Crear Menu", command=self.crear_menu_receta).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame_menu, text="Cargar Menus", command=self.cargar_menus).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame_menu, text="Limpiar Receta", command=self.limpiar_receta).grid(row=0, column=2, padx=5)
        
        # --- Tabla para mostrar la lista de todos los menus ---
        list_frame = ctk.CTkFrame(self.menus_tab)
        list_frame.pack(pady=10, fill="both", expand=True)
        self.tree_menus = ttk.Treeview(list_frame, columns=("id", "nombre", "precio", "descripcion"), show="headings")
        for col, hdr in zip(("id", "nombre", "precio", "descripcion"), ("ID", "Nombre", "Precio", "Descripcion")):
            self.tree_menus.heading(col, text=hdr)
            self.tree_menus.column(col, anchor="center")
        vsb_menus = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_menus.yview)
        self.tree_menus.configure(yscrollcommand=vsb_menus.set)
        self.tree_menus.pack(side="left", fill="both", expand=True)
        vsb_menus.pack(side="right", fill="y")
        
        # --- Carga inicial de datos ---
        self.receta = []
        self.cargar_ingredientes_combo()
        self.cargar_menus()

    def cargar_ingredientes_combo(self):
        # Carga los ingredientes en el combobox para crear recetas.
        self.ingredientes_source = obtener_ingredientes()
        self.combo_ing['values'] = [f"{ing.id} - {ing.nombre}" for ing in self.ingredientes_source]
        if self.ingredientes_source:
            self.combo_ing.current(0)

    def anadir_ing_receta(self):
        # Añade un ingrediente a la lista de la receta actual.
        if not self.combo_ing.get():
            messagebox.showwarning("Aviso", "Ingrese ingrediente")
            return
        try:
            cantidad = float(self.entry_ing_cant.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad invalida")
            return
        
        idx = self.combo_ing.current()
        ing = self.ingredientes_source[idx]
        if any(r['id'] == ing.id for r in self.receta):
            messagebox.showwarning("Aviso", "Ingrediente ya añadido")
            return
        
        entry = {'id': ing.id, 'nombre': ing.nombre, 'cant': cantidad, 'unidad': ing.unidad}
        self.receta.append(entry)
        self.tree_receta.insert('', 'end', iid=ing.id, values=(ing.nombre, cantidad, ing.unidad))
        self.entry_ing_cant.delete(0, 'end')

    def limpiar_receta(self):
        # Limpia la tabla y la lista de la receta actual.
        self.receta.clear()
        for i in self.tree_receta.get_children():
            self.tree_receta.delete(i)

    def crear_menu_receta(self):
        # Guarda el nuevo menu en la DB y su receta en un archivo JSON.
        nombre = self.menu_nombre.get().strip()
        desc = self.menu_desc.get().strip()
        try:
            precio = float(self.menu_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Precio invalido")
            return
        
        if not nombre or not desc:
            messagebox.showerror("Error", "Complete nombre y descripcion")
            return
        if not self.receta:
            messagebox.showwarning("Aviso", "Añada al menos 1 ingrediente")
            return
        
        crear_menu(nombre, desc, precio)
        menu_id = max(obtener_menus(), key=lambda m: m.id).id
        
        # Guarda la receta en un archivo JSON cuyo nombre es el ID del menu.
        os.makedirs('recetas', exist_ok=True)
        with open(f'recetas/{menu_id}.json', 'w', encoding='utf-8') as f:
            json.dump(self.receta, f, ensure_ascii=False, indent=2)
            
        messagebox.showinfo("Exito", "Menu creado con receta")
        self.menu_nombre.delete(0, 'end')
        self.menu_desc.delete(0, 'end')
        self.menu_precio.delete(0, 'end')
        self.limpiar_receta()
        self.cargar_menus()
        self.cargar_comboboxes()

    def cargar_menus(self):
        # Carga todos los menus existentes y los muestra en la tabla.
        menus = obtener_menus()
        for i in self.tree_menus.get_children():
            self.tree_menus.delete(i)
        for m in menus:
            self.tree_menus.insert('', 'end', iid=m.id, values=(m.id, m.nombre, f"${m.precio:,.0f}", m.descripcion))

    # -------------------------------------------------------------------
    # METODOS PARA LA PESTAÑA DE PEDIDOS
    # -------------------------------------------------------------------

    def init_pedidos_tab(self):
        # --- Frame para la creacion de un nuevo pedido ---
        crear_pedido_frame = ctk.CTkFrame(self.pedidos_tab)
        crear_pedido_frame.pack(pady=10, padx=10, fill="x")
        
        # --- Parte superior: seleccion de cliente, menu y cantidad ---
        top_frame = ctk.CTkFrame(crear_pedido_frame)
        top_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(top_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(top_frame, state="readonly", width=30)
        self.combo_clientes.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="🔄", command=self.cargar_comboboxes, width=40).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(top_frame, text="Menu:").grid(row=0, column=3, padx=(20, 5), pady=5)
        self.combo_menus = ttk.Combobox(top_frame, state="readonly", width=30)
        self.combo_menus.grid(row=0, column=4, padx=5, pady=5)
        self.entry_cant = ctk.CTkEntry(top_frame, placeholder_text="Cant.", width=70)
        self.entry_cant.grid(row=0, column=5, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="Añadir Item", command=self.anadir_item_pedido).grid(row=0, column=6, padx=5, pady=5)
        
        # --- Tabla para mostrar los items del pedido actual (carrito) ---
        frame_items = ctk.CTkFrame(crear_pedido_frame)
        frame_items.pack(fill="both", expand=True, pady=5)
        self.tree_items = ttk.Treeview(frame_items, columns=("menu", "cant", "precio", "sub"), show="headings", height=5)
        for col, hdr in zip(("menu", "cant", "precio", "sub"), ("Menu", "Cant", "Precio Unit.", "Subtotal")):
            self.tree_items.heading(col, text=hdr)
            self.tree_items.column(col, anchor="center")
        self.tree_items.pack(side="left", fill="both", expand=True)
        
        # --- Parte inferior: total y boton para guardar ---
        total_frame = ctk.CTkFrame(crear_pedido_frame)
        total_frame.pack(pady=5, fill="x")
        self.label_total = ctk.CTkLabel(total_frame, text="Total: $0", font=(None, 16, "bold"))
        self.label_total.pack(side="left", padx=10)
        ctk.CTkButton(total_frame, text="Guardar Pedido", command=self.guardar_pedido).pack(side="right", padx=10)
        
        # --- Frame para el historial de pedidos ---
        history_main_frame = ctk.CTkFrame(self.pedidos_tab)
        history_main_frame.pack(fill="both", expand=True, pady=10, padx=10)
        ctk.CTkLabel(history_main_frame, text="Historial de Pedidos", font=("", 16, "bold")).pack(pady=(0, 10))
        
        # --- Botones de accion para el historial ---
        history_btn_frame = ctk.CTkFrame(history_main_frame)
        history_btn_frame.pack(pady=5, fill="x")
        ctk.CTkButton(history_btn_frame, text="🔄 Actualizar Pedidos", command=self.ver_pedidos).pack(side="left", padx=5)
        ctk.CTkButton(history_btn_frame, text="🧾 Generar Boleta Seleccionada", command=self.generar_boleta_seleccionada).pack(side="left", padx=5)
        ctk.CTkButton(history_btn_frame, text="🗑️ Borrar Seleccionado", command=self.borrar_pedido_seleccionado, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", padx=15)
        
        # --- Tabla (Treeview) para mostrar el historial de pedidos ---
        tree_hist_frame = ctk.CTkFrame(history_main_frame)
        tree_hist_frame.pack(fill="both", expand=True)
        self.tree_pedidos = ttk.Treeview(tree_hist_frame, columns=("id", "cli", "total", "fecha", "desc"), show="headings")
        for col, hdr in zip(("id", "cli", "total", "fecha", "desc"), ("ID", "Cliente", "Total", "Fecha", "Descripcion")):
            self.tree_pedidos.heading(col, text=hdr)
        vsb_hist = ttk.Scrollbar(tree_hist_frame, orient="vertical", command=self.tree_pedidos.yview)
        self.tree_pedidos.configure(yscrollcommand=vsb_hist.set)
        self.tree_pedidos.pack(side="left", fill="both", expand=True)
        vsb_hist.pack(side="right", fill="y")
        
        # --- Carga inicial y configuracion de eventos ---
        self.tree_pedidos.bind("<<TreeviewSelect>>", self.seleccionar_pedido_evento)
        self.pedido_seleccionado_id = None
        self.carrito = []
        self.cargar_comboboxes()
        self.ver_pedidos()

    def cargar_comboboxes(self):
        # Actualiza los combobox de clientes y menus con datos de la DB.
        self.clientes_cb = obtener_clientes()
        self.combo_clientes['values'] = [f"{c.id} - {c.nombre}" for c in self.clientes_cb]
        if self.clientes_cb: self.combo_clientes.current(0)
        else: self.combo_clientes.set("")
        
        self.menus_cb = obtener_menus()
        self.combo_menus['values'] = [f"{m.id} - {m.nombre}" for m in self.menus_cb]
        if self.menus_cb: self.combo_menus.current(0)
        else: self.combo_menus.set("")

    def anadir_item_pedido(self):
        # Añade un item al carrito, verificando el stock de ingredientes primero.
        if not self.combo_menus.get(): return
        try:
            cant = int(self.entry_cant.get())
            if cant <= 0: raise ValueError
        except (ValueError, AssertionError):
            messagebox.showerror("Error", "Cantidad invalida")
            return
        
        menu = self.menus_cb[self.combo_menus.current()]
        
        # Crea un carrito temporal para simular el pedido y verificar el stock.
        carrito_temporal = self.carrito[:]
        item_existente_idx = next((i for i, item in enumerate(carrito_temporal) if item[0] == menu.id), -1)
        
        if item_existente_idx != -1:
            _, cant_existente = carrito_temporal.pop(item_existente_idx)
            carrito_temporal.append((menu.id, cant + cant_existente))
        else:
            carrito_temporal.append((menu.id, cant))

        # Llama a la funcion de verificacion de stock.
        ingredientes_faltantes = verificar_y_obtener_faltantes(carrito_temporal)
        if ingredientes_faltantes:
            msg = "No hay suficientes ingredientes:\n\n- " + "\n- ".join(ingredientes_faltantes)
            messagebox.showerror("Stock Insuficiente", msg)
            return

        # Si la verificacion es exitosa, se actualiza el carrito real.
        item_existente = next((item for item in self.carrito if item[0] == menu.id), None)
        if item_existente:
            self.carrito.remove(item_existente)
            cant += item_existente[1]
        
        self.carrito.append((menu.id, cant))
        self.actualizar_tree_items()
        self.entry_cant.delete(0, 'end')
        self.actualizar_total()

    def actualizar_tree_items(self):
        # Actualiza la tabla del carrito con los items actuales.
        for i in self.tree_items.get_children(): self.tree_items.delete(i)
        menus_data = {m.id: m for m in self.menus_cb}
        for menu_id, cantidad in self.carrito:
            menu = menus_data.get(menu_id)
            if menu:
                subtotal = menu.precio * cantidad
                self.tree_items.insert('', 'end', values=(menu.nombre, cantidad, f"${menu.precio:,.0f}", f"${subtotal:,.0f}"))

    def actualizar_total(self):
        # Calcula el costo total del carrito y actualiza la etiqueta.
        total = 0
        menus_data = {m.id: m.precio for m in self.menus_cb}
        for menu_id, cantidad in self.carrito:
            total += menus_data.get(menu_id, 0) * cantidad
        self.label_total.configure(text=f"Total: ${total:,.0f}")

    def guardar_pedido(self):
        # Guarda el pedido en la DB, lo que descuenta los ingredientes.
        if not self.combo_clientes.get():
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return
        if not self.carrito:
            messagebox.showwarning("Aviso", "Añada items al pedido")
            return
        
        cliente_seleccionado = self.clientes_cb[self.combo_clientes.current()]
        try:
            crear_pedido(cliente_seleccionado.id, self.carrito)
            messagebox.showinfo("Exito", "Pedido guardado correctamente.")
            # Limpia el carrito y actualiza las vistas
            self.carrito.clear()
            self.actualizar_tree_items()
            self.actualizar_total()
            self.ver_pedidos()
            self.cargar_ingredientes()
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo completar el pedido:\n{e}")

    def seleccionar_pedido_evento(self, event):
        # Guarda el ID del pedido seleccionado en el historial.
        seleccion = self.tree_pedidos.selection()
        if not seleccion:
            self.pedido_seleccionado_id = None
            return
        self.pedido_seleccionado_id = int(seleccion[0])

    def generar_boleta_seleccionada(self):
        # Genera un PDF para el pedido seleccionado.
        if self.pedido_seleccionado_id is None:
            messagebox.showwarning("Sin seleccion", "Por favor, seleccione un pedido del historial.")
            return
        try:
            nombre_archivo = generar_boleta_pdf_from_db_pedido(self.pedido_seleccionado_id)
            if nombre_archivo and os.path.exists(nombre_archivo):
                if messagebox.askyesno("Exito", f"Boleta generada:\n{nombre_archivo}\n\nDesea abrir el archivo?"):
                    os.startfile(os.path.realpath(nombre_archivo))
            else:
                messagebox.showerror("Error", "No se pudo generar o encontrar la boleta.")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrio un error al generar el PDF: {e}")

    def ver_pedidos(self):
        # Carga y muestra el historial de pedidos en la tabla.
        pedidos = obtener_pedidos()
        clientes_map = {c.id: c.nombre for c in obtener_clientes()}
        for i in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(i)
        # Ordena los pedidos por fecha, del mas nuevo al mas viejo.
        for p in sorted(pedidos, key=lambda x: x.fecha, reverse=True):
            nombre_cliente = clientes_map.get(p.cliente_id, "ID: " + str(p.cliente_id))
            self.tree_pedidos.insert('', 'end', iid=p.id, values=(p.id, nombre_cliente, f"${p.total:,.0f}", p.fecha.strftime("%Y-%m-%d %H:%M"), p.descripcion))
        self.pedido_seleccionado_id = None

    def borrar_pedido_seleccionado(self):
        # Elimina el pedido seleccionado y devuelve los ingredientes al stock.
        if self.pedido_seleccionado_id is None:
            messagebox.showwarning("Sin seleccion", "Por favor, seleccione un pedido del historial para eliminar.")
            return
        
        try:
            if eliminar_pedido_por_id(self.pedido_seleccionado_id):
                messagebox.showinfo("Exito", "Pedido eliminado y stock de ingredientes restaurado.")
                self.ver_pedidos()
                self.cargar_ingredientes() # Actualiza la vista de ingredientes
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pedido.")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrio un error al eliminar el pedido: {e}")
            
    # -------------------------------------------------------------------
    # METODOS PARA LA PESTAÑA DE GRAFICOS
    # -------------------------------------------------------------------

    def init_graficos_tab(self):
        # Integra el frame de los graficos en su pestaña.
        graficos_view = GraficosFrame(master=self.graficos_tab)
        graficos_view.pack(fill="both", expand=True)


# -------------------------------------------
# PUNTO DE ENTRADA DE LA APLICACION
# -------------------------------------------
if __name__ == "__main__":
    # Crea el directorio de boletas si no existe
    if not os.path.exists('boletas'):
        os.makedirs('boletas')
    
    # Inicia la aplicacion
    app = App()
    app.mainloop()