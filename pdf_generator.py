from fpdf import FPDF
import os

def _ensure_dir(path):
    # Funcion interna para asegurar que el directorio de boletas exista
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def generar_boleta_pdf(pedido, nombre_archivo=None):
    # Valida que el pedido tenga items
    if not pedido.items:
        raise ValueError('No hay items en pedido')
    
    # Define el nombre del archivo si no se proporciona
    if nombre_archivo is None:
        nombre_archivo = 'boletas/boleta.pdf'
    _ensure_dir(nombre_archivo)

    # Creacion del objeto PDF
    pdf = FPDF()
    pdf.add_page()
    
    # --- Encabezado de la boleta ---
    pdf.set_font('Arial','B',16)
    pdf.cell(190,10,'Boleta de Pedido',0,1,'C')
    pdf.set_font('Arial','',12)
    pdf.ln(5)
    pdf.cell(0,5,'Restaurante - Temuco',0,1,'L')
    pdf.cell(0,5,'RUT 88888888-9',0,1,'L')
    pdf.ln(5)

    # --- Cabecera de la tabla de items ---
    pdf.set_font('Arial','B',12)
    pdf.cell(60,8,'Nombre',1)
    pdf.cell(30,8,'Cant.',1,0,'C')
    pdf.cell(40,8,'P.Unit',1,0,'R')
    pdf.cell(40,8,'Subtotal',1,1,'R')
    pdf.set_font('Arial','',12)

    # --- Contenido de la tabla de items ---
    subtotal_calculado = 0
    for it in pedido.items:
        pdf.cell(60,8,it.menu.nombre,1)
        pdf.cell(30,8,str(it.cantidad),1,0,'C')
        pdf.cell(40,8,f"${it.menu.precio:.0f}",1,0,'R')
        sub = it.calcular_subtotal()
        pdf.cell(40,8,f"${sub:.0f}",1,1,'R')
        subtotal_calculado += sub

    total = subtotal_calculado
    
    pdf.ln(5)
    
    # --- Fila del Total ---
    pdf.set_font('Arial','B',12)
    pdf.cell(50) # Espaciado para alinear a la derecha
    pdf.cell(40,8,'Total',1,0,'R')
    pdf.cell(40,8,f"${total:.0f}",1,1,'R')

    # --- Guardado del archivo PDF ---
    pdf.output(nombre_archivo)
    return nombre_archivo