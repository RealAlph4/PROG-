# Sistema de Gestión de Restaurante

Este proyecto es una aplicación de escritorio desarrollada en Python como parte de la evaluación del curso de Programación II. El sistema está diseñado para facilitar la administración de un restaurante, permitiendo gestionar clientes, menús, ingredientes y pedidos de una forma centralizada e intuitiva.

## Características Principales

  * **Gestión CRUD Completa:** Permite crear, leer, actualizar y eliminar Clientes, Ingredientes y Menús de forma sencilla.
  * **Control de Inventario en Tiempo Real:** El stock de ingredientes se descuenta automáticamente al registrar un pedido y se repone si el pedido es eliminado, evitando ventas de productos sin stock.
  * **Generación de Boletas en PDF:** Crea un recibo detallado en formato PDF para cualquier venta realizada, que se almacena en la carpeta `boletas/`.
  * **Visualización de Datos:** Utiliza `matplotlib` para generar gráficos estadísticos que muestran los platos más vendidos, ayudando a la toma de decisiones del negocio.
  * **Interfaz Gráfica Intuitiva:** Desarrollada con `customtkinter` para ofrecer una experiencia de usuario moderna y fácil de usar.

## Tecnologías Utilizadas

  * **Lenguaje:** Python 3.10+
  * **Interfaz Gráfica:** `customtkinter`, `tkinter`
  * **Base de Datos y ORM:** SQLite a través de `SQLAlchemy`
  * **Generación de Gráficos:** `matplotlib`
  * **Generación de PDF:** `fpdf`

## Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu entorno local.

### 1\. Prerrequisitos

  * Tener instalado Python 3.10 o una versión superior.
  * Contar con un gestor de paquetes como `pip`.

### 2\. Instalación de Dependencias

Abre una terminal o consola en la carpeta raíz del proyecto y ejecuta el siguiente comando para instalar todas las bibliotecas necesarias:

```bash
pip install customtkinter SQLAlchemy matplotlib fpdf
```

### 3\. Ejecutar la Base de Datos

Una vez instaladas las dependencias, ejecuta el siguiente comando en la terminal para iniciar la base de datos:

```bash
python main.py
```
La primera vez que se ejecute, se creará automáticamente el archivo de la base de datos `restaurante.db`.

### 4\. Ejecutar la Aplicación

Ejecuta el siguiente comando en la terminal para iniciar el programa:

```bash
python app.py
```

## Guía de Uso

1.  **Añadir Ingredientes:** Ve a la pestaña **"Ingredientes"** para registrar los productos de tu inventario con su nombre, tipo, cantidad inicial y unidad de medida.

2.  **Crear Menús:** En la pestaña **"Menús"**, crea los platos que ofrece el restaurante. Asigna un nombre, descripción, precio y construye su receta añadiendo los ingredientes previamente registrados.

3.  **Registrar Clientes:** En la pestaña **"Clientes"**, añade a tus clientes ingresando su nombre y correo electrónico.

5.  **Crear un Pedido:**

      * Dirígete a la pestaña **"Pedidos"**.
      * Selecciona un cliente y un menú de las listas desplegables.
      * Indica la cantidad y haz clic en **"Añadir Item"**. El sistema validará que haya stock suficiente.
      * Cuando el pedido esté completo, presiona **"Guardar Pedido"**. El stock se descontará automáticamente.

6.  **Gestionar Pedidos y Reportes:**

      * En el **"Historial de Pedidos"**, puedes seleccionar cualquier pedido para:
          * **Generar su boleta en PDF** con el botón correspondiente.
          * **Eliminarlo**, lo que devolverá los ingredientes al inventario.
      * En la pestaña **"Gráficos"**, puedes generar una visualización de los platos más vendidos.
