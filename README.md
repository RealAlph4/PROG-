Características Principales:

    Gestión CRUD completa: Permite Crear, Leer, Actualizar y Eliminar (CRUD) las entidades principales del negocio: Clientes, Menús, Ingredientes y Pedidos.

    Control de Inventario Automático: Descuenta los ingredientes del stock en tiempo real al registrar un pedido y los repone si un pedido es eliminado.

    Interfaz Gráfica Moderna: Desarrollada con customtkinter para una experiencia de usuario amigable e intuitiva.

    Generación de Boletas: Crea un recibo detallado en formato PDF para cada venta realizada.

    Visualización de Datos: Genera gráficos estadísticos para analizar información clave, como los platos más vendidos.

Tecnologías Utilizadas:

    Lenguaje: Python

    Base de Datos: SQLite con el ORM SQLAlchemy.

    Interfaz Gráfica: customtkinter y tkinter.

    Generación de Gráficos: matplotlib.

    Generación de PDF: fpdf.

2. Guía de Uso

Requisitos Previos

Asegúrate de tener Python 3.10 o superior instalado. Luego, instala las bibliotecas necesarias ejecutando el siguiente comando en tu terminal:
Bash

pip install customtkinter fpdf matplotlib SQLAlchemy

Paso 1: Iniciar la Aplicación

    Navega hasta la carpeta raíz del proyecto (ORM_clientes/).

    Ejecuta el siguiente comando para iniciar la aplicación:
    Bash

    python app.py

    La primera vez que se ejecute, se creará automáticamente el archivo de base de datos restaurante.db.

Paso 2: Gestión de Ingredientes

Es el primer paso para configurar el restaurante.

    Ve a la pestaña "Ingredientes".

    Rellena los campos: "Nombre", "Tipo", "Cantidad" y "Unidad".

    Haz clic en "Agregar Ingrediente". El nuevo ingrediente aparecerá en la tabla inferior.

    Repite el proceso para todos los ingredientes de tu inventario.

Paso 3: Gestión de Menús

Con los ingredientes ya cargados, puedes crear los platos.

    Ve a la pestaña "Menús".

    Ingresa el "Nombre del plato", "Descripción" y "Precio".

    En la sección de recetas, selecciona un ingrediente del menú desplegable, define la cantidad necesaria para el plato y haz clic en "Añadir a Receta".

    Repite el paso anterior para todos los ingredientes del plato.

    Una vez que la receta esté completa, haz clic en "Crear Menú".

Paso 4: Gestión de Clientes

Registra a tus clientes antes de tomarles un pedido.

    Ve a la pestaña "Clientes".

    Ingresa el "Nombre" y "Correo" del cliente.

    Haz clic en "Agregar Cliente".

Paso 5: Crear un Pedido

Este es el flujo de venta principal.

    Ve a la pestaña "Pedidos".

    Selecciona un cliente del menú desplegable "Cliente".

    Selecciona un plato del menú desplegable "Menú", indica la cantidad y haz clic en "Añadir Item". El sistema verificará el stock antes de agregarlo.

    El producto se añadirá a la tabla del pedido actual. Puedes añadir más productos repitiendo el paso anterior.

    Cuando el pedido esté completo, haz clic en "Guardar Pedido". El stock de ingredientes se descontará automáticamente.

Paso 6: Administrar Pedidos y Boletas

En la misma pestaña de "Pedidos", puedes ver el "Historial de Pedidos".

    Generar Boleta: Selecciona un pedido del historial y haz clic en "Generar Boleta Seleccionada". Se creará un archivo PDF en la carpeta boletas/.

    Eliminar Pedido: Selecciona un pedido y haz clic en "Borrar Seleccionado". El pedido se eliminará y los ingredientes utilizados se devolverán al stock.

Paso 7: Visualizar Estadísticas

    Ve a la pestaña "Gráficos".

    Haz clic en "Generar Gráfico de Platos Más Vendidos".

    El sistema analizará el historial de pedidos y mostrará un gráfico de barras con los 10 platos más populares.
