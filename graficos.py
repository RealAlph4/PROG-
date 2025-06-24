import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from collections import Counter

# --- Imports para Gráficos ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importamos la función para obtener los datos que necesitamos
from crud.pedido_crud import obtener_pedidos

class GraficosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # --- Interfaz de la Pestaña de Gráficos ---
        # Frame para los controles (botones, etc.)
        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(pady=10, padx=10, fill="x")

        # Botón para generar el gráfico
        btn_generar = ctk.CTkButton(controls_frame, text="Generar Gráfico de Platos Más Vendidos", command=self.generar_grafico_platos)
        btn_generar.pack()

        # Frame donde se mostrará el gráfico
        chart_frame = ctk.CTkFrame(self)
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
        # Invertir la lista para que el más vendido quede arriba en gráficos horizontales
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