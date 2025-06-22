import matplotlib.pyplot as plt

def mostrar_grafico_ventas_ficticio():
    fechas = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    ventas = [10, 25, 13, 20, 15]
    plt.bar(fechas, ventas)
    plt.title('Ventas semanales')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.show()