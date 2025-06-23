import customtkinter as ctk
import tkinter.messagebox as messagebox

from crud.cliente_crud import crear_cliente, obtener_clientes
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

    def init_clientes_tab(self):
        self.entry_nombre = ctk.CTkEntry(self.clientes_tab, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=5)
        self.entry_correo = ctk.CTkEntry(self.clientes_tab, placeholder_text="Correo")
        self.entry_correo.pack(pady=5)
        ctk.CTkButton(self.clientes_tab, text="Agregar Cliente", command=self.agregar_cliente).pack(pady=5)
        ctk.CTkButton(self.clientes_tab, text="Cargar Lista", command=self.cargar_clientes).pack(pady=5)
        self.lista_clientes = ctk.CTkTextbox(self.clientes_tab, height=250)
        self.lista_clientes.pack(pady=10)

    def agregar_cliente(self):
        nombre = self.entry_nombre.get()
        correo = self.entry_correo.get()
        if crear_cliente(nombre, correo):
            messagebox.showinfo("Éxito", "Cliente agregado.")
            self.cargar_clientes()
        else:
            messagebox.showwarning("Error", "Correo ya registrado.")

    def cargar_clientes(self):
        clientes = obtener_clientes()
        self.lista_clientes.delete("0.0", "end")
        for c in clientes:
            self.lista_clientes.insert("end", f"{c.id}: {c.nombre} - {c.correo}\n")

    def init_ingredientes_tab(self):
        self.ing_nombre = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Nombre")
        self.ing_nombre.pack(pady=5)
        self.ing_tipo = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Tipo")
        self.ing_tipo.pack(pady=5)
        self.ing_cantidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Cantidad")
        self.ing_cantidad.pack(pady=5)
        self.ing_unidad = ctk.CTkEntry(self.ingredientes_tab, placeholder_text="Unidad (g, u, ml...)")
        self.ing_unidad.pack(pady=5)
        ctk.CTkButton(self.ingredientes_tab, text="Agregar Ingrediente", command=self.agregar_ingrediente).pack(pady=5)
        ctk.CTkButton(self.ingredientes_tab, text="Cargar Ingredientes", command=self.cargar_ingredientes).pack(pady=5)
        self.lista_ingredientes = ctk.CTkTextbox(self.ingredientes_tab, height=250)
        self.lista_ingredientes.pack(pady=10)

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
        self.lista_ingredientes.delete("0.0", "end")
        for i in ingredientes:
            self.lista_ingredientes.insert("end", f"{i.id}: {i.nombre} - {i.tipo} - {i.cantidad} {i.unidad}\n")

    def init_menus_tab(self):
        self.menu_nombre = ctk.CTkEntry(self.menus_tab, placeholder_text="Nombre del Menú")
        self.menu_nombre.pack(pady=5)
        self.menu_desc = ctk.CTkEntry(self.menus_tab, placeholder_text="Descripción")
        self.menu_desc.pack(pady=5)
        ctk.CTkButton(self.menus_tab, text="Agregar Menú", command=self.agregar_menu).pack(pady=5)
        ctk.CTkButton(self.menus_tab, text="Cargar Menús", command=self.cargar_menus).pack(pady=5)
        self.lista_menus = ctk.CTkTextbox(self.menus_tab, height=250)
        self.lista_menus.pack(pady=10)

    def agregar_menu(self):
        nombre = self.menu_nombre.get()
        descripcion = self.menu_desc.get()
        if nombre and descripcion:
            crear_menu(nombre, descripcion)
            messagebox.showinfo("Éxito", "Menú agregado.")
            self.cargar_menus()
        else:
            messagebox.showwarning("Error", "Campos incompletos.")

    def cargar_menus(self):
        menus = obtener_menus()
        self.lista_menus.delete("0.0", "end")
        for m in menus:
            self.lista_menus.insert("end", f"{m.id}: {m.nombre} - {m.descripcion}\n")

    def init_pedidos_tab(self):
        self.ped_cliente = ctk.CTkEntry(self.pedidos_tab, placeholder_text="ID Cliente")
        self.ped_cliente.pack(pady=5)
        self.ped_desc = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Descripción del Pedido")
        self.ped_desc.pack(pady=5)
        self.ped_total = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Total ($)")
        self.ped_total.pack(pady=5)
        self.ped_cant = ctk.CTkEntry(self.pedidos_tab, placeholder_text="Cantidad de Menús")
        self.ped_cant.pack(pady=5)
        ctk.CTkButton(self.pedidos_tab, text="Guardar Pedido", command=self.guardar_pedido).pack(pady=5)
        ctk.CTkButton(self.pedidos_tab, text="Ver Pedidos", command=self.ver_pedidos).pack(pady=5)
        self.lista_pedidos = ctk.CTkTextbox(self.pedidos_tab, height=250)
        self.lista_pedidos.pack(pady=10)

    def guardar_pedido(self):
        try:
            cliente_id = int(self.ped_cliente.get())
            total = float(self.ped_total.get())
            cantidad = int(self.ped_cant.get())
            descripcion = self.ped_desc.get()
            crear_pedido(cliente_id, descripcion, total, cantidad)
            messagebox.showinfo("Éxito", "Pedido guardado.")
        except:
            messagebox.showerror("Error", "Verifica los campos.")

    def ver_pedidos(self):
        pedidos = obtener_pedidos()
        self.lista_pedidos.delete("0.0", "end")
        for p in pedidos:
            self.lista_pedidos.insert("end", f"{p.id}: Cliente {p.cliente_id} - ${p.total} - {p.fecha}\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()