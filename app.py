import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import json
import os

# --- Imports para Gráficos ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

from crud.cliente_crud import crear_cliente, obtener_clientes, actualizar_cliente, eliminar_cliente
from crud.ingrediente_crud import crear_ingrediente, obtener_ingredientes
from crud.menu_crud import crear_menu, obtener_menus
from crud.pedido_crud import crear_pedido, obtener_pedidos, generar_boleta_pdf_from_db_pedido, eliminar_pedido_por_id

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Restaurante")
        self.geometry("1100x750")

        self.tabview = ctk.CTkTabview(self, width=1080)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.clientes_tab = self.tabview.add("Clientes")
        self.ingredientes_tab = self.tabview.add("Ingredientes")
        self.menus_tab = self.tabview.add("Menús")
        self.pedidos_tab = self.tabview.add("Pedidos")
        # <<< NUEVO >>> Se añade la pestaña de Gráficos
        self.graficos_tab = self.tabview.add("Gráficos")

        self.init_clientes_tab()
        self.init_ingredientes_tab()
        self.init_menus_tab()
        self.init_pedidos_tab()
        # <<< NUEVO >>> Se inicializa la nueva pestaña
        self.init_graficos_tab()

    # --- PESTAÑAS ANTERIORES (SIN CAMBIOS) ---
    def init_clientes_tab(self):
        self.entry_nombre = ctk.CTkEntry(self.clientes_tab, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=5)
        self.entry_correo = ctk.CTkEntry(self.clientes_tab, placeholder_text="Correo")
        self.entry_correo.pack(pady=5)
        btn_frame = ctk.CTkFrame(self.clientes_tab); btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Cliente", command=self.agregar_cliente).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Editar Cliente", command=self.editar_cliente).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Lista", command=self.cargar_clientes).grid(row=0, column=3, padx=5)
        tree_frame = ctk.CTkFrame(self.clientes_tab); tree_frame.pack(pady=10, fill="both", expand=True)
        self.tree_clientes = ttk.Treeview(tree_frame, columns=("id","nombre","correo"), show="headings")
        for col, hdr in zip(("id","nombre","correo"),("ID","Nombre","Correo")):
            self.tree_clientes.heading(col, text=hdr); self.tree_clientes.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_clientes.yview); self.tree_clientes.configure(yscrollcommand=vsb.set)
        self.tree_clientes.pack(side="left", fill="both", expand=True); vsb.pack(side="right", fill="y")
        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente_evento)
        self.cliente_seleccionado_id = None; self.cargar_clientes()
    def cargar_clientes(self):
        self.clientes = obtener_clientes()
        for i in self.tree_clientes.get_children(): self.tree_clientes.delete(i)
        for c in self.clientes: self.tree_clientes.insert('', 'end', iid=c.id, values=(c.id, c.nombre, c.correo))
        self.cliente_seleccionado_id=None; self.entry_nombre.delete(0,'end'); self.entry_correo.delete(0,'end')
    def seleccionar_cliente_evento(self,event):
        sel = self.tree_clientes.selection()
        if not sel: return
        cid = int(sel[0]); cli = next((c for c in self.clientes if c.id==cid),None)
        if cli:
            self.entry_nombre.delete(0,'end'); self.entry_nombre.insert(0,cli.nombre)
            self.entry_correo.delete(0,'end'); self.entry_correo.insert(0,cli.correo)
            self.cliente_seleccionado_id = cli.id
    def agregar_cliente(self):
        nom=self.entry_nombre.get().strip(); corr=self.entry_correo.get().strip().lower()
        if not nom or not corr: messagebox.showerror("Error","Debe ingresar nombre y correo"); return
        if any(c.correo.lower()==corr for c in obtener_clientes()): messagebox.showerror("Error","Correo duplicado"); return
        crear_cliente(nom,corr); self.cargar_clientes(); self.cargar_comboboxes()
    def editar_cliente(self):
        if self.cliente_seleccionado_id is None: messagebox.showwarning("Aviso","Seleccione un cliente"); return
        nom=self.entry_nombre.get().strip(); corr=self.entry_correo.get().strip().lower()
        if not nom or not corr: messagebox.showerror("Error","Complete nombre y correo"); return
        for c in obtener_clientes():
            if c.correo.lower()==corr and c.id!=self.cliente_seleccionado_id: messagebox.showerror("Error","Correo ya registrado a otro cliente"); return
        actualizar_cliente(self.cliente_seleccionado_id,nom,corr); self.cargar_clientes()
    def eliminar_cliente(self):
        if self.cliente_seleccionado_id is None: messagebox.showwarning("Aviso","Seleccione un cliente"); return
        if not messagebox.askyesno("Confirmar","Eliminar cliente seleccionado?"): return
        eliminar_cliente(self.cliente_seleccionado_id); self.cargar_clientes(); self.cargar_comboboxes()
    def init_ingredientes_tab(self):
        self.ing_nombre = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Nombre"); self.ing_nombre.pack(pady=5)
        self.ing_tipo = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Tipo"); self.ing_tipo.pack(pady=5)
        self.ing_cantidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Cantidad"); self.ing_cantidad.pack(pady=5)
        self.ing_unidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Unidad (g,u,ml)"); self.ing_unidad.pack(pady=5)
        btn = ctk.CTkButton(self.ingredientes_tab, text="Agregar Ingrediente", command=self.agregar_ingrediente); btn.pack(pady=5)
        ctk.CTkButton(self.ingredientes_tab, text="Cargar Ingredientes", command=self.cargar_ingredientes).pack(pady=5)
        frame = ctk.CTkFrame(self.ingredientes_tab); frame.pack(expand=True, fill="both", pady=10)
        self.tree_ingredientes = ttk.Treeview(frame, columns=("id","nombre","tipo","cantidad","unidad"), show="headings")
        for col,hdr in zip(("id","nombre","tipo","cantidad","unidad"),("ID","Nombre","Tipo","Cant","Unidad")):
            self.tree_ingredientes.heading(col,text=hdr); self.tree_ingredientes.column(col,anchor="center")
        vsb=ttk.Scrollbar(frame, orient="vertical", command=self.tree_ingredientes.yview); self.tree_ingredientes.configure(yscrollcommand=vsb.set)
        self.tree_ingredientes.pack(side="left", fill="both", expand=True); vsb.pack(side="right", fill="y")
        self.cargar_ingredientes()
    def cargar_ingredientes(self):
        ingr=obtener_ingredientes()
        for i in self.tree_ingredientes.get_children(): self.tree_ingredientes.delete(i)
        for ing in ingr: self.tree_ingredientes.insert('', 'end', iid=ing.id, values=(ing.id, ing.nombre, ing.tipo, ing.cantidad, ing.unidad))
    def agregar_ingrediente(self):
        nombre=self.ing_nombre.get(); tipo=self.ing_tipo.get(); cant=self.ing_cantidad.get(); unidad=self.ing_unidad.get()
        try: cant=float(cant)
        except ValueError: messagebox.showerror("Error","Cantidad inválida"); return
        if crear_ingrediente(nombre,tipo,cant,unidad): self.cargar_ingredientes(); self.cargar_ingredientes_combo()
        else: messagebox.showwarning("Error","Ingrediente ya existe")
    def init_menus_tab(self):
        self.menu_nombre = ctk.CTkEntry(self.menus_tab, placeholder_text="Nombre del plato"); self.menu_nombre.pack(pady=5)
        self.menu_desc = ctk.CTkEntry(self.menus_tab, placeholder_text="Descripción"); self.menu_desc.pack(pady=5)
        self.menu_precio = ctk.CTkEntry(self.menus_tab, placeholder_text="Precio ($)"); self.menu_precio.pack(pady=5)
        ingr_frame = ctk.CTkFrame(self.menus_tab); ingr_frame.pack(pady=5)
        ctk.CTkLabel(ingr_frame, text="Ingrediente").grid(row=0, column=0, padx=5)
        self.combo_ing = ttk.Combobox(ingr_frame, state="readonly", width=25); self.combo_ing.grid(row=0, column=1, padx=5)
        self.entry_ing_cant = ctk.CTkEntry(ingr_frame, placeholder_text="Cant.", width=70); self.entry_ing_cant.grid(row=0, column=2, padx=5)
        ctk.CTkButton(ingr_frame, text="Añadir a Receta", command=self.anadir_ing_receta).grid(row=0, column=3, padx=5)
        recipe_frame = ctk.CTkFrame(self.menus_tab); recipe_frame.pack(pady=5, fill="x")
        self.tree_receta = ttk.Treeview(recipe_frame, columns=("ing","cant","unidad"), show="headings", height=6)
        for col,hdr in zip(("ing","cant","unidad"),("Ingrediente","Cant","Unidad")):
            self.tree_receta.heading(col,text=hdr); self.tree_receta.column(col, anchor="center")
        vsb=ttk.Scrollbar(recipe_frame, orient="vertical", command=self.tree_receta.yview); self.tree_receta.configure(yscrollcommand=vsb.set)
        self.tree_receta.pack(side="left", fill="both", expand=True); vsb.pack(side="right", fill="y")
        btn_frame = ctk.CTkFrame(self.menus_tab); btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Crear Menú", command=self.crear_menu_receta).grid(row=0,column=0,padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Menús", command=self.cargar_menus).grid(row=0,column=1,padx=5)
        ctk.CTkButton(btn_frame, text="Limpiar Receta", command=self.limpiar_receta).grid(row=0,column=2,padx=5)
        list_frame = ctk.CTkFrame(self.menus_tab); list_frame.pack(pady=10, fill="both", expand=True)
        self.tree_menus = ttk.Treeview(list_frame, columns=("id","nombre","precio","descripcion"), show="headings")
        for col,hdr in zip(("id","nombre","precio","descripcion"),("ID","Nombre","Precio","Descripción")):
            self.tree_menus.heading(col,text=hdr); self.tree_menus.column(col, anchor="center")
        vsb2=ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_menus.yview); self.tree_menus.configure(yscrollcommand=vsb2.set)
        self.tree_menus.pack(side="left", fill="both", expand=True); vsb2.pack(side="right", fill="y")
        self.receta=[]; self.cargar_ingredientes_combo(); self.cargar_menus()
    def cargar_ingredientes_combo(self):
        self.ingredientes_source=obtener_ingredientes()
        self.combo_ing['values']=[f"{ing.id} - {ing.nombre}" for ing in self.ingredientes_source]
        if self.ingredientes_source: self.combo_ing.current(0)
    def anadir_ing_receta(self):
        if not self.combo_ing.get(): messagebox.showwarning("Aviso","Ingrese ingrediente"); return
        try: cant=float(self.entry_ing_cant.get());
        except ValueError: messagebox.showerror("Error","Cantidad inválida"); return
        idx=self.combo_ing.current(); ing=self.ingredientes_source[idx]
        if any(r['id']==ing.id for r in self.receta): messagebox.showwarning("Aviso","Ingrediente ya añadido"); return
        entry={'id':ing.id,'nombre':ing.nombre,'cant':cant,'unidad':ing.unidad}
        self.receta.append(entry)
        self.tree_receta.insert('', 'end', iid=ing.id, values=(ing.nombre, cant, ing.unidad)); self.entry_ing_cant.delete(0,'end')
    def limpiar_receta(self):
        self.receta.clear()
        for i in self.tree_receta.get_children(): self.tree_receta.delete(i)
    def crear_menu_receta(self):
        nombre=self.menu_nombre.get().strip(); desc=self.menu_desc.get().strip()
        try: precio=float(self.menu_precio.get())
        except ValueError: messagebox.showerror("Error","Precio inválido"); return
        if not nombre or not desc: messagebox.showerror("Error","Complete nombre y descripción"); return
        if not self.receta: messagebox.showwarning("Aviso","Añada al menos 1 ingrediente"); return
        crear_menu(nombre, desc, precio); menu_id=max(obtener_menus(), key=lambda m:m.id).id
        os.makedirs('recetas', exist_ok=True)
        with open(f'recetas/{menu_id}.json','w', encoding='utf-8') as f: json.dump(self.receta, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Éxito", "Menú creado con receta"); self.menu_nombre.delete(0,'end'); self.menu_desc.delete(0,'end'); self.menu_precio.delete(0,'end')
        self.limpiar_receta(); self.cargar_menus(); self.cargar_comboboxes()
    def cargar_menus(self):
        menus=obtener_menus()
        for i in self.tree_menus.get_children(): self.tree_menus.delete(i)
        for m in menus: self.tree_menus.insert('', 'end', iid=m.id, values=(m.id, m.nombre, f"${m.precio:,.0f}", m.descripcion))
    def init_pedidos_tab(self):
        crear_pedido_frame = ctk.CTkFrame(self.pedidos_tab); crear_pedido_frame.pack(pady=10, padx=10, fill="x")
        top_frame = ctk.CTkFrame(crear_pedido_frame); top_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(top_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(top_frame, state="readonly", width=30); self.combo_clientes.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="🔄", command=self.cargar_comboboxes, width=40).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(top_frame, text="Menú:").grid(row=0, column=3, padx=(20, 5), pady=5)
        self.combo_menus = ttk.Combobox(top_frame, state="readonly", width=30); self.combo_menus.grid(row=0, column=4, padx=5, pady=5)
        self.entry_cant = ctk.CTkEntry(top_frame, placeholder_text="Cant.", width=70); self.entry_cant.grid(row=0, column=5, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="Añadir Item", command=self.anadir_item_pedido).grid(row=0, column=6, padx=5, pady=5)
        frame_items = ctk.CTkFrame(crear_pedido_frame); frame_items.pack(fill="both", expand=True, pady=5)
        self.tree_items = ttk.Treeview(frame_items, columns=("menu", "cant", "precio", "sub"), show="headings", height=5)
        for col, hdr in zip(("menu", "cant", "precio", "sub"), ("Menu", "Cant", "Precio Unit.", "Subtotal")):
            self.tree_items.heading(col, text=hdr); self.tree_items.column(col, anchor="center")
        self.tree_items.pack(side="left", fill="both", expand=True)
        total_frame = ctk.CTkFrame(crear_pedido_frame); total_frame.pack(pady=5, fill="x")
        self.label_total = ctk.CTkLabel(total_frame, text="Total: $0", font=(None, 16, "bold")); self.label_total.pack(side="left", padx=10)
        ctk.CTkButton(total_frame, text="Guardar Pedido", command=self.guardar_pedido).pack(side="right", padx=10)
        history_main_frame = ctk.CTkFrame(self.pedidos_tab); history_main_frame.pack(fill="both", expand=True, pady=10, padx=10)
        ctk.CTkLabel(history_main_frame, text="Historial de Pedidos", font=("", 16, "bold")).pack(pady=(0, 10))
        history_btn_frame = ctk.CTkFrame(history_main_frame); history_btn_frame.pack(pady=5, fill="x")
        ctk.CTkButton(history_btn_frame, text="🔄 Actualizar Pedidos", command=self.ver_pedidos).pack(side="left", padx=5)
        ctk.CTkButton(history_btn_frame, text="🧾 Generar Boleta Seleccionada", command=self.generar_boleta_seleccionada).pack(side="left", padx=5)
        ctk.CTkButton(history_btn_frame, text="🗑️ Borrar Seleccionado", command=self.borrar_pedido_seleccionado, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", padx=15)
        tree_hist_frame = ctk.CTkFrame(history_main_frame); tree_hist_frame.pack(fill="both", expand=True)
        self.tree_pedidos = ttk.Treeview(tree_hist_frame, columns=("id", "cli", "total", "fecha", "desc"), show="headings")
        for col, hdr in zip(("id", "cli", "total", "fecha", "desc"), ("ID", "Cliente", "Total", "Fecha", "Descripción")): self.tree_pedidos.heading(col, text=hdr)
        vsb2 = ttk.Scrollbar(tree_hist_frame, orient="vertical", command=self.tree_pedidos.yview); self.tree_pedidos.configure(yscrollcommand=vsb2.set)
        self.tree_pedidos.pack(side="left", fill="both", expand=True); vsb2.pack(side="right", fill="y")
        self.tree_pedidos.bind("<<TreeviewSelect>>", self.seleccionar_pedido_evento)
        self.pedido_seleccionado_id = None
        self.carrito = []; self.cargar_comboboxes(); self.ver_pedidos()
    def cargar_comboboxes(self):
        self.clientes_cb = obtener_clientes(); self.combo_clientes['values'] = [f"{c.id} - {c.nombre}" for c in self.clientes_cb]
        if self.clientes_cb: self.combo_clientes.current(0)
        else: self.combo_clientes.set("")
        self.menus_cb = obtener_menus(); self.combo_menus['values'] = [f"{m.id} - {m.nombre}" for m in self.menus_cb]
        if self.menus_cb: self.combo_menus.current(0)
        else: self.combo_menus.set("")
        print("Comboboxes actualizados.")
    def anadir_item_pedido(self):
        if not self.combo_menus.get(): return
        try:
            cant = int(self.entry_cant.get())
            if cant <= 0: raise ValueError
        except (ValueError, AssertionError): messagebox.showerror("Error", "Cantidad inválida"); return
        menu = self.menus_cb[self.combo_menus.current()]
        item_existente = next((item for item in self.carrito if item[0] == menu.id), None)
        if item_existente:
            self.carrito.remove(item_existente); cant += item_existente[1]
        self.carrito.append((menu.id, cant))
        self.actualizar_tree_items(); self.entry_cant.delete(0, 'end'); self.actualizar_total()
    def actualizar_tree_items(self):
        for i in self.tree_items.get_children(): self.tree_items.delete(i)
        menus_data = {m.id: m for m in self.menus_cb}
        for menu_id, cantidad in self.carrito:
            menu = menus_data.get(menu_id)
            if menu:
                subtotal = menu.precio * cantidad
                self.tree_items.insert('', 'end', values=(menu.nombre, cantidad, f"${menu.precio:,.0f}", f"${subtotal:,.0f}"))
    def actualizar_total(self):
        total = 0; menus_data = {m.id: m.precio for m in self.menus_cb}
        for menu_id, cantidad in self.carrito: total += menus_data.get(menu_id, 0) * cantidad
        self.label_total.configure(text=f"Total: ${total:,.0f}"); return total
    def guardar_pedido(self):
        if not self.combo_clientes.get(): messagebox.showwarning("Aviso", "Seleccione un cliente"); return
        if not self.carrito: messagebox.showwarning("Aviso", "Añada items al pedido"); return
        cli = self.clientes_cb[self.combo_clientes.current()]
        crear_pedido(cli.id, self.carrito); messagebox.showinfo("Éxito", "Pedido guardado correctamente.")
        self.carrito.clear(); self.actualizar_tree_items(); self.actualizar_total(); self.ver_pedidos()
    def seleccionar_pedido_evento(self, event):
        seleccion = self.tree_pedidos.selection()
        if not seleccion: self.pedido_seleccionado_id = None; return
        self.pedido_seleccionado_id = int(seleccion[0])
    def generar_boleta_seleccionada(self):
        if self.pedido_seleccionado_id is None: messagebox.showwarning("Sin selección", "Por favor, seleccione un pedido del historial."); return
        try:
            nombre_archivo = generar_boleta_pdf_from_db_pedido(self.pedido_seleccionado_id)
            if nombre_archivo and os.path.exists(nombre_archivo):
                 if messagebox.askyesno("Éxito", f"Boleta generada:\n{nombre_archivo}\n\n¿Desea abrir el archivo?"):
                     os.startfile(os.path.realpath(nombre_archivo))
            else: messagebox.showerror("Error", "No se pudo generar o encontrar la boleta.")
        except Exception as e: messagebox.showerror("Error Inesperado", f"Ocurrió un error al generar el PDF: {e}")
    def ver_pedidos(self):
        peds = obtener_pedidos(); clientes_map = {c.id: c.nombre for c in obtener_clientes()}
        for i in self.tree_pedidos.get_children(): self.tree_pedidos.delete(i)
        for p in sorted(peds, key=lambda x: x.fecha, reverse=True):
            nombre_cliente = clientes_map.get(p.cliente_id, "ID: " + str(p.cliente_id))
            self.tree_pedidos.insert('', 'end', iid=p.id, values=(p.id, nombre_cliente, f"${p.total:,.0f}", p.fecha.strftime("%Y-%m-%d %H:%M"), p.descripcion))
        self.pedido_seleccionado_id = None
    def borrar_pedido_seleccionado(self):
        if self.pedido_seleccionado_id is None:
            messagebox.showwarning("Sin selección", "Por favor, seleccione un pedido del historial para eliminar.")
            return
        try:
            if eliminar_pedido_por_id(self.pedido_seleccionado_id):
                self.ver_pedidos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pedido. Es posible que ya no exista.")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al eliminar el pedido: {e}")

    # --- PESTAÑA DE GRÁFICOS (NUEVA) ---
    def init_graficos_tab(self):
        """Inicializa la pestaña que contendrá los gráficos."""
        # Frame para los controles (botones, etc.)
        controls_frame = ctk.CTkFrame(self.graficos_tab)
        controls_frame.pack(pady=10, padx=10, fill="x")

        # Botón para generar el gráfico
        btn_generar = ctk.CTkButton(controls_frame, text="Generar Gráfico de Platos Más Vendidos", command=self.generar_grafico_platos)
        btn_generar.pack()

        # Frame donde se mostrará el gráfico
        chart_frame = ctk.CTkFrame(self.graficos_tab)
        chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Creación de la figura y el canvas de Matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Mostrar un mensaje inicial en el gráfico
        self.ax.text(0.5, 0.5, "Presione el botón para generar el gráfico",
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes)
        self.canvas.draw()

    def generar_grafico_platos(self):
        """Obtiene los datos y genera el gráfico de platos más vendidos."""
        # 1. Obtener todos los pedidos de la base de datos
        pedidos = obtener_pedidos()
        if not pedidos:
            messagebox.showinfo("Sin Datos", "No hay pedidos registrados para generar un gráfico.")
            return

        # 2. Procesar la descripción de cada pedido para contar los platos
        platos_vendidos = Counter()
        for pedido in pedidos:
            # La descripción es como: "Completo x1 -> $2500 | Papas Fritas x2 -> $3000"
            items = pedido.descripcion.split(' | ')
            for item in items:
                try:
                    # Separar el nombre del resto de la cadena
                    nombre_plato_part, resto = item.rsplit(' x', 1)
                    # Separar la cantidad del precio
                    cantidad_str, _ = resto.split(' -> ')
                    cantidad = int(cantidad_str)
                    platos_vendidos[nombre_plato_part.strip()] += cantidad
                except ValueError:
                    # Ignorar líneas que no sigan el formato esperado
                    print(f"Línea de descripción ignorada por formato incorrecto: '{item}'")
                    continue

        if not platos_vendidos:
            messagebox.showinfo("Sin Datos", "No se pudieron procesar los datos de los pedidos.")
            return

        # 3. Preparar los datos para el gráfico (top 10 platos)
        top_platos = platos_vendidos.most_common(10)
        # Invertir la lista para que el más vendido quede arriba en gráficos horizontales, o a la derecha en verticales
        top_platos.reverse()
        
        nombres = [item[0] for item in top_platos]
        cantidades = [item[1] for item in top_platos]

        # 4. Limpiar el gráfico anterior y dibujar el nuevo
        self.ax.clear()
        bars = self.ax.barh(nombres, cantidades, color='teal') # barh para gráfico horizontal
        self.ax.set_title('Top 10 - Platos Más Vendidos')
        self.ax.set_xlabel('Cantidad Vendida')
        
        # Añadir etiquetas con el valor al final de cada barra
        for bar in bars:
            self.ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                         f'{int(bar.get_width())}',
                         va='center')

        # Ajustar el layout y redibujar el canvas
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    if not os.path.exists('boletas'): os.makedirs('boletas')
    app = App()
    app.mainloop()
