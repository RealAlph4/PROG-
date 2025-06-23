import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

from crud.cliente_crud import crear_cliente, obtener_clientes, actualizar_cliente, eliminar_cliente
from crud.ingrediente_crud import crear_ingrediente, obtener_ingredientes
from crud.menu_crud import crear_menu, obtener_menus
from crud.pedido_crud import crear_pedido, obtener_pedidos

# BUG FIX: Remove backslashes from string literals in set_appearance_mode and set_default_color_theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def parse_menu_price(descripcion: str) -> float:
    """Intenta extraer el precio (float) desde la descripción del menú.
    Si no encuentra '|precio', devuelve 0."""
    if "|" in descripcion:
        try:
            return float(descripcion.split("|")[-1])
        except ValueError:
            return 0.0
    return 0.0


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Restaurante")
        self.geometry("900x700")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.clientes_tab = self.tabview.add("Clientes")
        self.ingredientes_tab = self.tabview.add("Ingredientes")
        self.menus_tab = self.tabview.add("Menús")
        self.pedidos_tab = self.tabview.add("Pedidos")

        self.init_clientes_tab()
        self.init_ingredientes_tab()
        self.init_menus_tab()
        self.init_pedidos_tab()

    # ---------------------------  CLIENTES  ---------------------------
    def init_clientes_tab(self):
        self.entry_nombre = ctk.CTkEntry(self.clientes_tab, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=5)
        self.entry_correo = ctk.CTkEntry(self.clientes_tab, placeholder_text="Correo")
        self.entry_correo.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.clientes_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Cliente", command=self.agregar_cliente).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Editar Cliente", command=self.editar_cliente).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Lista", command=self.cargar_clientes).grid(row=0, column=3, padx=5)

        tree_frame = ctk.CTkFrame(self.clientes_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree_clientes = ttk.Treeview(tree_frame, columns=("id", "nombre", "correo"), show="headings")
        for col, header in zip(("id", "nombre", "correo"), ("ID", "Nombre", "Correo")):
            self.tree_clientes.heading(col, text=header)
            self.tree_clientes.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=vsb.set)

        self.tree_clientes.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente_evento)

        self.cliente_seleccionado_id = None
        self.cargar_clientes()

    def cargar_clientes(self):
        self.clientes = obtener_clientes()
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.clientes:
            self.tree_clientes.insert('', 'end', iid=c.id, values=(c.id, c.nombre, c.correo))
        self.cliente_seleccionado_id = None
        self.entry_nombre.delete(0, "end")
        self.entry_correo.delete(0, "end")

    def seleccionar_cliente_evento(self, event):
        selected = self.tree_clientes.selection()
        if not selected:
            return
        item_id = int(selected[0])
        cliente = next((c for c in self.clientes if c.id == item_id), None)
        if cliente:
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, cliente.nombre)
            self.entry_correo.delete(0, "end")
            self.entry_correo.insert(0, cliente.correo)
            self.cliente_seleccionado_id = cliente.id

    def agregar_cliente(self):
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip().lower()
        if not nombre or not correo:
            messagebox.showerror("Error", "Debe ingresar nombre y correo.")
            return
        clientes = obtener_clientes()
        if any(c.correo.lower() == correo for c in clientes):
            messagebox.showerror("Error", "El correo ya está registrado.")
            return
        if crear_cliente(nombre, correo):
            messagebox.showinfo("Éxito", "Cliente agregado.")
            self.cargar_clientes()
        else:
            messagebox.showwarning("Error", "No se pudo agregar el cliente.")

    def editar_cliente(self):
        if self.cliente_seleccionado_id is None:
            messagebox.showwarning("Aviso", "Seleccione un cliente en la lista.")
            return
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip().lower()
        if not nombre or not correo:
            messagebox.showerror("Error", "Debe ingresar nombre y correo.")
            return
        clientes = obtener_clientes()
        for c in clientes:
            if c.correo.lower() == correo and c.id != self.cliente_seleccionado_id:
                messagebox.showerror("Error", "El correo ya está registrado a otro cliente.")
                return
        if actualizar_cliente(self.cliente_seleccionado_id, nombre, correo):
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            self.cargar_clientes()
        else:
            messagebox.showwarning("Error", "No se pudo actualizar el cliente.")

    def eliminar_cliente(self):
        if self.cliente_seleccionado_id is None:
            messagebox.showwarning("Aviso", "Seleccione un cliente en la lista.")
            return
        confirm = messagebox.askyesno("Confirmar", "¿Seguro que quiere eliminar este cliente?\nEsta acción no se puede deshacer.")
        if not confirm:
            return
        if eliminar_cliente(self.cliente_seleccionado_id):
            messagebox.showinfo("Éxito", "Cliente eliminado.")
            self.cargar_clientes()
        else:
            messagebox.showwarning("Error", "No se pudo eliminar el cliente (puede tener pedidos asociados).")

    # ---------------------------  INGREDIENTES  ---------------------------
    def init_ingredientes_tab(self):
        self.ing_nombre = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Nombre")
        self.ing_nombre.pack(pady=5)
        self.ing_tipo = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Tipo")
        self.ing_tipo.pack(pady=5)
        self.ing_cantidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Cantidad")
        self.ing_cantidad.pack(pady=5)
        self.ing_unidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Unidad (g, u, ml...)")
        self.ing_unidad.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.ingredientes_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Ingrediente", command=self.agregar_ingrediente).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Ingredientes", command=self.cargar_ingredientes).grid(row=0, column=1, padx=5)

        tree_frame = ctk.CTkFrame(self.ingredientes_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree_ingredientes = ttk.Treeview(tree_frame, columns=("id", "nombre", "tipo", "cantidad", "unidad"), show="headings")
        for col, header in zip(("id", "nombre", "tipo", "cantidad", "unidad"), ("ID", "Nombre", "Tipo", "Cantidad", "Unidad")):
            self.tree_ingredientes.heading(col, text=header)
            self.tree_ingredientes.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_ingredientes.yview)
        self.tree_ingredientes.configure(yscrollcommand=vsb.set)
        self.tree_ingredientes.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.cargar_ingredientes()

    def agregar_ingrediente(self):
        nombre = self.ing_nombre.get()
        tipo = self.ing_tipo.get()
        cantidad = self.ing_cantidad.get()
        unidad = self.ing_unidad.get()
        try:
            cantidad = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        if crear_ingrediente(nombre, tipo, cantidad, unidad):
            messagebox.showinfo("Éxito", "Ingrediente agregado.")
            self.cargar_ingredientes()
        else:
            messagebox.showwarning("Error", "Ingrediente ya existe.")

    def cargar_ingredientes(self):
        ingredientes = obtener_ingredientes()
        for item in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(item)
        for i in ingredientes:
            self.tree_ingredientes.insert('', 'end', iid=i.id, values=(i.id, i.nombre, i.tipo, i.cantidad, i.unidad))

    # ---------------------------  MENÚS  ---------------------------
    def init_menus_tab(self):
        self.menu_nombre = ctk.CTkEntry(self.menus_tab, placeholder_text="Nombre del Menú")
        self.menu_nombre.pack(pady=5)
        self.menu_desc = ctk.CTkEntry(self.menus_tab, placeholder_text="Descripción")
        self.menu_desc.pack(pady=5)
        self.menu_precio = ctk.CTkEntry(self.menus_tab, placeholder_text="Precio ($)")
        self.menu_precio.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.menus_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Menú", command=self.agregar_menu).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Menús", command=self.cargar_menus).grid(row=0, column=1, padx=5)

        tree_frame = ctk.CTkFrame(self.menus_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree_menus = ttk.Treeview(tree_frame, columns=("id", "nombre", "descripcion", "precio"), show="headings")
        for col, header in zip(("id", "nombre", "descripcion", "precio"), ("ID", "Nombre", "Descripción", "Precio")):
            self.tree_menus.heading(col, text=header)
            self.tree_menus.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_menus.yview)
        self.tree_menus.configure(yscrollcommand=vsb.set)
        self.tree_menus.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.cargar_menus()

    def agregar_menu(self):
        nombre = self.menu_nombre.get()
        desc = self.menu_desc.get()
        try:
            precio = float(self.menu_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Precio inválido.")
            return
        # Guardamos precio concatenado en descripción por compatibilidad si el CRUD no soporta campo precio
        desc_con_precio = f"{desc}|{precio}"
        if crear_menu(nombre, desc_con_precio):
            messagebox.showinfo("Éxito", "Menú agregado.")
            self.cargar_menus()
        else:
            messagebox.showwarning("Error", "No se pudo agregar menú.")

    def cargar_menus(self):
        menus = obtener_menus()
        for item in self.tree_menus.get_children():
            self.tree_menus.delete(item)
        for m in menus:
            precio = parse_menu_price(m.descripcion)
            desc = m.descripcion.split("|")[0] if "|" in m.descripcion else m.descripcion
            self.tree_menus.insert('', 'end', iid=m.id, values=(m.id, m.nombre, desc, precio))

    # ---------------------------  PEDIDOS  ---------------------------
    def init_pedidos_tab(self):
        # Cliente selector
        client_frame = ctk.CTkFrame(self.pedidos_tab)
        client_frame.pack(pady=5)
        ctk.CTkLabel(client_frame, text="Cliente").grid(row=0, column=0, padx=5)
        self.combo_clientes = ttk.Combobox(client_frame, state="readonly")
        self.combo_clientes.grid(row=0, column=1, padx=5)

        # Menú selector
        menu_frame = ctk.CTkFrame(self.pedidos_tab)
        menu_frame.pack(pady=5)
        ctk.CTkLabel(menu_frame, text="Menú").grid(row=0, column=0, padx=5)
        self.combo_menus = ttk.Combobox(menu_frame, state="readonly")
        self.combo_menus.grid(row=0, column=1, padx=5)
        self.entry_cant = ctk.CTkEntry(menu_frame, placeholder_text="Cantidad", width=80)
        self.entry_cant.grid(row=0, column=2, padx=5)
        ctk.CTkButton(menu_frame, text="Añadir Item", command=self.anadir_item).grid(row=0, column=3, padx=5)

        # Lista temporal de items del pedido
        tree_frame = ctk.CTkFrame(self.pedidos_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)
        self.tree_items = ttk.Treeview(tree_frame, columns=("menu", "cantidad", "precio", "subtotal"), show="headings")
        for col, header in zip(("menu", "cantidad", "precio", "subtotal"), ("Menú", "Cant", "Precio", "Subtotal")):
            self.tree_items.heading(col, text=header)
            self.tree_items.column(col, anchor="center")
        vsb_items = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_items.yview)
        self.tree_items.configure(yscrollcommand=vsb_items.set)
        self.tree_items.pack(side="left", fill="both", expand=True)
        vsb_items.pack(side="right", fill="y")

        # Total y acciones
        total_frame = ctk.CTkFrame(self.pedidos_tab)
        total_frame.pack(pady=5)
        self.label_total = ctk.CTkLabel(total_frame, text="Total: $0", font=(None, 16, "bold"))
        self.label_total.grid(row=0, column=0, padx=10)
        ctk.CTkButton(total_frame, text="Guardar Pedido", command=self.guardar_pedido).grid(row=0, column=1, padx=5)
        ctk.CTkButton(total_frame, text="Ver Pedidos", command=self.ver_pedidos).grid(row=0, column=2, padx=5)

        # Treeview pedidos históricos
        history_frame = ctk.CTkFrame(self.pedidos_tab)
        history_frame.pack(pady=10, fill="both", expand=True)
        self.tree_pedidos = ttk.Treeview(history_frame, columns=("id", "cliente", "total", "fecha", "descripcion"), show="headings")
        for col, header in zip(("id", "cliente", "total", "fecha", "descripcion"), ("ID", "Cliente", "Total", "Fecha", "Descripción")):
            self.tree_pedidos.heading(col, text=header)
            self.tree_pedidos.column(col, anchor="center")
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree_pedidos.yview)
        self.tree_pedidos.configure(yscrollcommand=vsb.set)
        self.tree_pedidos.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Datos auxiliares
        self.carrito = []  # [(menu_id, nombre, cant, precio, subtotal)]
        self.cargar_comboboxes()

    def cargar_comboboxes(self):
        # Clientes
        self.clientes_cb_source = obtener_clientes()
        self.combo_clientes['values'] = [f"{c.id} - {c.nombre}" for c in self.clientes_cb_source]
        if self.clientes_cb_source:
            self.combo_clientes.current(0)
        # Menús
        self.menus_cb_source = obtener_menus()
        self.combo_menus['values'] = [f"{m.id} - {m.nombre}" for m in self.menus_cb_source]
        if self.menus_cb_source:
            self.combo_menus.current(0)

    def anadir_item(self):
        if not self.combo_menus.get():
            messagebox.showwarning("Aviso", "Debe seleccionar un menú")
            return
        try:
            cantidad = int(self.entry_cant.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
        # Obtener menú seleccionado
        idx = self.combo_menus.current()
        menu = self.menus_cb_source[idx]
        precio = parse_menu_price(menu.descripcion)
        subtotal = precio * cantidad
        self.carrito.append((menu.id, menu.nombre, cantidad, precio, subtotal))
        self.tree_items.insert('', 'end', values=(menu.nombre, cantidad, precio, subtotal))
        self.actualizar_total()
        # Limpiar cantidad
        self.entry_cant.delete(0, 'end')

    def actualizar_total(self):
        total = sum(item[4] for item in self.carrito)
        self.label_total.configure(text=f"Total: ${total}")
        return total

    def guardar_pedido(self):
        if not self.combo_clientes.get():
            messagebox.showwarning("Aviso", "Seleccione un cliente")
            return
        if not self.carrito:
            messagebox.showwarning("Aviso", "Añada items al pedido")
            return
        cliente_idx = self.combo_clientes.current()
        cliente = self.clientes_cb_source[cliente_idx]

        total = self.actualizar_total()
        descripcion = ", ".join([f"{cant}x {name}" for _, name, cant, _, _ in self.carrito])
        try:
            crear_pedido(cliente.id, descripcion, total, sum(item[2] for item in self.carrito))
            messagebox.showinfo("Éxito", "Pedido guardado")
            # Reset carrito e UI
            self.carrito.clear()
            for item in self.tree_items.get_children():
                self.tree_items.delete(item)
            self.actualizar_total()
            self.ver_pedidos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar pedido: {e}")

    def ver_pedidos(self):
        pedidos = obtener_pedidos()
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)
        for p in pedidos:
            self.tree_pedidos.insert('', 'end', iid=p.id, values=(p.id, p.cliente_id, p.total, p.fecha.strftime("%Y-%m-%d"), p.descripcion))

if __name__ == "__main__":
    app = App()
    app.mainloop()