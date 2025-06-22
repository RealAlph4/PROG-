import customtkinter as ctk
from tkinter import ttk, messagebox
import re
from datetime import datetime

# ---------- CRUD LAYERS ----------
from crud.cliente_crud import obtener_clientes, crear_cliente, eliminar_cliente
from crud.ingrediente_crud import (
    obtener_ingredientes,
    crear_ingrediente,
    eliminar_ingrediente,
)
from crud.menu_crud import (
    obtener_menus,
    crear_menu,
    eliminar_menu,
)
from crud.pedido_crud import crear_pedido, obtener_pedidos
from pdf_generator import generar_boleta_pdf

# ---------- DB ----------
from models import Base
from database import engine

Base.metadata.create_all(engine)

# ---------- APP ----------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Sistema de Gestión de Restaurante")
        self.geometry("1100x750")

        # Carrito tuplas: (menu_id, cantidad, precio, nombre)
        self.carrito: list[tuple[int, int, float, str]] = []

        # ---------- Tabs ----------
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=12, pady=12)

        self.tab_cli = self.tabview.add("Clientes")
        self.tab_ing = self.tabview.add("Ingredientes")
        self.tab_menu = self.tabview.add("Menús")
        self.tab_compra = self.tabview.add("Panel de Compra")
        self.tab_ped = self.tabview.add("Pedidos")

        # Build each tab
        self._build_clientes_tab()
        self._build_ingredientes_tab()
        self._build_menus_tab()
        self._build_compra_tab()
        self._build_pedidos_tab()

        # Initial loads
        self._reload_clientes()
        self._reload_ingredientes()
        self._reload_menus()
        self._reload_menus_list()
        self._reload_pedidos()

    # ========== CLIENTES ==========
    def _build_clientes_tab(self) -> None:
        frm = ctk.CTkFrame(self.tab_cli)
        frm.pack(fill="x", pady=6, padx=6)

        self.ent_cli_nom = ctk.CTkEntry(frm, placeholder_text="Nombre")
        self.ent_cli_nom.pack(side="left", padx=4, expand=True, fill="x")
        self.ent_cli_cor = ctk.CTkEntry(frm, placeholder_text="Correo")
        self.ent_cli_cor.pack(side="left", padx=4, expand=True, fill="x")
        ctk.CTkButton(frm, text="Agregar", command=self._add_cliente).pack(side="left", padx=4)

        cols = ("ID", "Nombre", "Correo")
        self.tv_cli = ttk.Treeview(self.tab_cli, columns=cols, show="headings")
        for col in cols:
            self.tv_cli.heading(col, text=col)
            self.tv_cli.column(col, anchor="center")
        self.tv_cli.pack(expand=True, fill="both", padx=6, pady=6)

        ctk.CTkButton(self.tab_cli, text="Eliminar seleccionado",
                      command=self._del_cliente).pack(anchor="e", padx=10, pady=4)

    def _reload_clientes(self) -> None:
        self.tv_cli.delete(*self.tv_cli.get_children())
        for c in obtener_clientes():
            self.tv_cli.insert("", "end", iid=str(c.id), values=(c.id, c.nombre, c.correo))

    def _add_cliente(self) -> None:
        nom, cor = self.ent_cli_nom.get().strip(), self.ent_cli_cor.get().strip()
        if not nom or not cor:
            messagebox.showerror("Error", "Completa todos los campos.")
            return
        if not re.match(r"^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$", cor):
            messagebox.showerror("Error", "Correo inválido.")
            return
        if crear_cliente(nom, cor):
            self._reload_clientes()
            self.ent_cli_nom.delete(0, "end")
            self.ent_cli_cor.delete(0, "end")
        else:
            messagebox.showwarning("Existe", "Correo ya registrado.")

    def _del_cliente(self) -> None:
        sel = self.tv_cli.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un cliente.")
            return
        eliminar_cliente(int(sel[0]))
        self._reload_clientes()

    # ========== INGREDIENTES ==========
    def _build_ingredientes_tab(self) -> None:
        frm = ctk.CTkFrame(self.tab_ing)
        frm.pack(fill="x", pady=6, padx=6)

        self.ent_ing_nom = ctk.CTkEntry(frm, placeholder_text="Nombre")
        self.ent_ing_nom.pack(side="left", padx=4, expand=True, fill="x")
        self.ent_ing_tipo = ctk.CTkEntry(frm, placeholder_text="Tipo")
        self.ent_ing_tipo.pack(side="left", padx=4, expand=True, fill="x")
        self.ent_ing_cant = ctk.CTkEntry(frm, placeholder_text="Cantidad", width=90)
        self.ent_ing_cant.pack(side="left", padx=4)
        self.ent_ing_uni = ctk.CTkEntry(frm, placeholder_text="Unidad (g,u,ml)", width=120)
        self.ent_ing_uni.pack(side="left", padx=4)

        ctk.CTkButton(frm, text="Agregar", command=self._add_ing).pack(side="left", padx=4)

        cols = ("ID", "Nombre", "Tipo", "Cantidad", "Unidad")
        self.tv_ing = ttk.Treeview(self.tab_ing, columns=cols, show="headings")
        for col in cols:
            self.tv_ing.heading(col, text=col)
            self.tv_ing.column(col, anchor="center")
        self.tv_ing.pack(expand=True, fill="both", padx=6, pady=6)

        ctk.CTkButton(self.tab_ing, text="Eliminar seleccionado",
                      command=self._del_ing).pack(anchor="e", padx=10, pady=4)

    def _reload_ingredientes(self) -> None:
        self.tv_ing.delete(*self.tv_ing.get_children())
        for ing in obtener_ingredientes():
            self.tv_ing.insert(
                "", "end", iid=str(ing.id),
                values=(ing.id, ing.nombre, ing.tipo, ing.cantidad, ing.unidad)
            )

    def _add_ing(self) -> None:
        nom, tipo, cant_txt, uni = (
            self.ent_ing_nom.get().strip(),
            self.ent_ing_tipo.get().strip(),
            self.ent_ing_cant.get().strip(),
            self.ent_ing_uni.get().strip(),
        )
        if not (nom and tipo and cant_txt and uni):
            messagebox.showerror("Error", "Completa los campos.")
            return
        try:
            cant = float(cant_txt)
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        crear_ingrediente(nom, tipo, cant, uni)
        self._reload_ingredientes()
        for e in (self.ent_ing_nom, self.ent_ing_tipo, self.ent_ing_cant, self.ent_ing_uni):
            e.delete(0, "end")

    def _del_ing(self) -> None:
        sel = self.tv_ing.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un ingrediente.")
            return
        eliminar_ingrediente(int(sel[0]))
        self._reload_ingredientes()

    # ========== MENÚS ==========
    def _build_menus_tab(self) -> None:
        frm = ctk.CTkFrame(self.tab_menu)
        frm.pack(fill="x", pady=6, padx=6)

        self.ent_menu_nom = ctk.CTkEntry(frm, placeholder_text="Nombre")
        self.ent_menu_nom.pack(side="left", padx=4, expand=True, fill="x")
        self.ent_menu_des = ctk.CTkEntry(frm, placeholder_text="Descripción")
        self.ent_menu_des.pack(side="left", padx=4, expand=True, fill="x")
        self.ent_menu_pre = ctk.CTkEntry(frm, placeholder_text="Precio", width=100)
        self.ent_menu_pre.pack(side="left", padx=4)
        ctk.CTkButton(frm, text="Agregar", command=self._add_menu).pack(side="left", padx=4)

        cols = ("ID", "Nombre", "Descripción", "Precio")
        self.tv_menu = ttk.Treeview(self.tab_menu, columns=cols, show="headings")
        for col in cols:
            self.tv_menu.heading(col, text=col)
            self.tv_menu.column(col, anchor="center")
        self.tv_menu.pack(expand=True, fill="both", padx=6, pady=6)

        ctk.CTkButton(self.tab_menu, text="Eliminar seleccionado",
                      command=self._del_menu).pack(anchor="e", padx=10, pady=4)

    def _reload_menus(self) -> None:
        self.tv_menu.delete(*self.tv_menu.get_children())
        for m in obtener_menus():
            self.tv_menu.insert(
                "", "end", iid=str(m.id),
                values=(m.id, m.nombre, m.descripcion, f"$ {m.precio:,.0f}")
            )

    def _add_menu(self) -> None:
        nom, des, pre_txt = (
            self.ent_menu_nom.get().strip(),
            self.ent_menu_des.get().strip(),
            self.ent_menu_pre.get().strip(),
        )
        if not (nom and des and pre_txt):
            messagebox.showerror("Error", "Completa los campos.")
            return
        try:
            pre = float(pre_txt)
        except ValueError:
            messagebox.showerror("Error", "Precio inválido.")
            return
        crear_menu(nom, des, pre)
        self._reload_menus()
        self._reload_menus_list()
        for e in (self.ent_menu_nom, self.ent_menu_des, self.ent_menu_pre):
            e.delete(0, "end")

    def _del_menu(self) -> None:
        sel = self.tv_menu.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un menú.")
            return
        eliminar_menu(int(sel[0]))
        self._reload_menus()
        self._reload_menus_list()

    # ========== PANEL COMPRA ==========
    def _build_compra_tab(self) -> None:
        left = ctk.CTkFrame(self.tab_compra)
        left.pack(side="left", fill="y", padx=6, pady=6)

        ctk.CTkLabel(left, text="Menús disponibles").pack()
        self.tv_menu_list = ttk.Treeview(
            left, columns=("ID", "Nombre", "Precio"), show="headings", height=20
        )
        for col in ("ID", "Nombre", "Precio"):
            self.tv_menu_list.heading(col, text=col)
            self.tv_menu_list.column(col, anchor="center")
        self.tv_menu_list.pack(fill="y", expand=True)

        frm_add = ctk.CTkFrame(left)
        frm_add.pack(fill="x", pady=4)
        self.ent_cant = ctk.CTkEntry(frm_add, width=80, placeholder_text="Cant.")
        self.ent_cant.pack(side="left", padx=3)
        ctk.CTkButton(frm_add, text="Agregar", command=self._add_to_cart).pack(side="left", padx=3)

        cart = ctk.CTkFrame(self.tab_compra)
        cart.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        cols = ("Nombre", "Cant", "Unit", "Sub")
        self.tv_cart = ttk.Treeview(cart, columns=cols, show="headings")
        for col in cols:
            self.tv_cart.heading(col, text=col)
            self.tv_cart.column(col, anchor="center")
        self.tv_cart.pack(expand=True, fill="both")

        self.lbl_total = ctk.CTkLabel(cart, text="Total: $0")
        self.lbl_total.pack(anchor="e", pady=4)
        ctk.CTkButton(cart, text="Boleta y Guardar", command=self._gen_boleta).pack(anchor="e", pady=4)

    def _reload_menus_list(self) -> None:
        self.tv_menu_list.delete(*self.tv_menu_list.get_children())
        for m in obtener_menus():
            self.tv_menu_list.insert(
                "", "end", iid=str(m.id), values=(m.id, m.nombre, f"$ {m.precio:,.0f}")
            )

    def _add_to_cart(self) -> None:
        sel = self.tv_menu_list.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Elige un menú.")
            return
        mid = int(sel[0])
        cant_txt = self.ent_cant.get().strip() or "1"
        if not cant_txt.isdigit() or int(cant_txt) <= 0:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        cant = int(cant_txt)
        for m in obtener_menus():
            if m.id == mid:
                self.carrito.append((mid, cant, m.precio, m.nombre))
                break
        self.ent_cant.delete(0, "end")
        self._refresh_cart()

    def _refresh_cart(self) -> None:
        self.tv_cart.delete(*self.tv_cart.get_children())
        total = 0
        for mid, cant, precio, nom in self.carrito:
            sub = cant * precio
            total += sub
            self.tv_cart.insert("", "end",
                                values=(nom, cant, f"$ {precio:,.0f}", f"$ {sub:,.0f}"))
        self.lbl_total.configure(text=f"Total: $ {total:,.0f}")

    def _gen_boleta(self) -> None:
        if not self.carrito:
            messagebox.showinfo("Carrito vacío", "Agrega menús.")
            return
        items = [(mid, cant) for mid, cant, _, _ in self.carrito]
        pedido = crear_pedido(None, items)
        ruta = f"boletas/boleta_{pedido.id}.pdf"
        messagebox.showinfo("Éxito", f"Pedido #{pedido.id} guardado.\\nBoleta: {ruta}")
        self.carrito.clear()
        self._refresh_cart()
        self._reload_pedidos()

    # ========== PEDIDOS ==========
    def _build_pedidos_tab(self) -> None:
        cols = ("ID", "Fecha", "Descripción", "Total")
        self.tv_ped = ttk.Treeview(self.tab_ped, columns=cols, show="headings")
        for col in cols:
            self.tv_ped.heading(col, text=col)
            self.tv_ped.column(col, anchor="center")
        self.tv_ped.pack(expand=True, fill="both", padx=6, pady=6)

    def _reload_pedidos(self) -> None:
        self.tv_ped.delete(*self.tv_ped.get_children())
        for p in obtener_pedidos():
            fecha = p.fecha.strftime("%Y-%m-%d %H:%M")
            self.tv_ped.insert(
                "", "end", values=(p.id, fecha, p.descripcion, f"$ {p.total:,.0f}")
            )


if __name__ == "__main__":
    App().mainloop()
