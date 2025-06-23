import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

from crud.cliente_crud import crear_cliente, obtener_clientes, actualizar_cliente, eliminar_cliente
from crud.ingrediente_crud import crear_ingrediente, obtener_ingredientes
from crud.menu_crud import crear_menu, obtener_menus
from crud.pedido_crud import crear_pedido, obtener_pedidos

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


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

        # Treeview + Scrollbar
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

        btn_frame = ctk.CTkFrame(self.menus_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Agregar Menú", command=self.agregar_menu).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Cargar Menús", command=self.cargar_menus).grid(row=0, column=1, padx=5)

        tree_frame = ctk.CTkFrame(self.menus_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree_menus = ttk.Treeview(tree_frame, columns=("id", "nombre", "descripcion"), show="headings")
        for col, header in zip(("id", "nombre", "descripcion"), ("ID", "Nombre", "Descripción")):
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
        if crear_menu(nombre, desc):
            messagebox.showinfo("Éxito", "Menú agregado.")
            self.cargar_menus()
        else:
            messagebox.showwarning("Error", "No se pudo agregar menú.")

    def cargar_menus(self):
        menus = obtener_menus()
        for item in self.tree_menus.get_children():
            self.tree_menus.delete(item)
        for m in menus:
            self.tree_menus.insert('', 'end', iid=m.id, values=(m.id, m.nombre, m.descripcion))

    # ---------------------------  PEDIDOS  ---------------------------
    def init_pedidos_tab(self):
        self.ped_cliente = ctk.CTkEntry(self.pedidos_tab, placeholder_text="ID Cliente")
        self.ped_cliente.pack(pady=5)
        self.ped_desc = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Descripción del Pedido")
        self.ped_desc.pack(pady=5)
        self.ped_total = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Total ($)")
        self.ped_total.pack(pady=5)
        self.ped_cant = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Cantidad de Menús")
        self.ped_cant.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.pedidos_tab)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Guardar Pedido", command=self.guardar_pedido).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Ver Pedidos", command=self.ver_pedidos).grid(row=0, column=1, padx=5)

        tree_frame = ctk.CTkFrame(self.pedidos_tab)
        tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree_pedidos = ttk.Treeview(tree_frame, columns=("id", "cliente", "total", "fecha", "descripcion"), show="headings")
        for col, header in zip(("id", "cliente", "total", "fecha", "descripcion"), ("ID", "Cliente", "Total", "Fecha", "Descripción")):
            self.tree_pedidos.heading(col, text=header)
            self.tree_pedidos.column(col, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_pedidos.yview)
        self.tree_pedidos.configure(yscrollcommand=vsb.set)
        self.tree_pedidos.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def guardar_pedido(self):
        try:
            cliente_id = int(self.ped_cliente.get())
            total = float(self.ped_total.get())
            cantidad = int(self.ped_cant.get())
            descripcion = self.ped_desc.get()
            crear_pedido(cliente_id, descripcion, total, cantidad)
            messagebox.showinfo("Éxito", "Pedido guardado.")
            self.ver_pedidos()
        except:
            messagebox.showerror("Error", "Verifica los campos.")

    def ver_pedidos(self):
        pedidos = obtener_pedidos()
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)
        for p in pedidos:
            self.tree_pedidos.insert('', 'end', iid=p.id, values=(p.id, p.cliente_id, p.total, p.fecha.strftime("%Y-%m-%d"), p.descripcion))

if __name__ == "__main__":
    app = App()
    app.mainloop()