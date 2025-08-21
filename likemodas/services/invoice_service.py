# likemodas/services/invoice_service.py

import reflex as rx
from weasyprint import HTML
from datetime import datetime
import os
from ..models import PurchaseModel
from ..utils.formatting import format_to_cop

# Define los datos de tu empresa (el remitente)
SENDER_DETAILS = {
    "name": "Likemodas",
    "address": "Calle Falsa 123, Popayán, Cauca",
    "email": "ventas@likemodas.com",
    "nit": "900.123.456-7"
}

def generate_invoice_pdf(purchase: PurchaseModel) -> bytes:
    """
    Genera un archivo PDF para una factura a partir de los datos de una compra.
    """
    # Construimos las filas de la tabla de artículos
    items_html = ""
    for item in purchase.items:
        item_subtotal = item.price_at_purchase * item.quantity
        items_html += f"""
        <tr>
            <td>{item.quantity}</td>
            <td>{item.blog_post.title if item.blog_post else 'Producto no disponible'}</td>
            <td>{format_to_cop(item.price_at_purchase)}</td>
            <td>{format_to_cop(item_subtotal)}</td>
        </tr>
        """

    # Obtenemos la ruta absoluta del logo
    # Asume que tu logo está en assets/logo.png
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    logo_url = f"file:///{logo_path}" if os.path.exists(logo_path) else ""

    # Plantilla HTML para la factura
    html_template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); font-size: 16px; line-height: 24px; }}
            .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }}
            .header img {{ width: 100%; max-width: 150px; }}
            .header .invoice-details {{ text-align: right; }}
            .addresses {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
            .invoice-table {{ width: 100%; line-height: inherit; text-align: left; border-collapse: collapse; }}
            .invoice-table td, .invoice-table th {{ padding: 8px; vertical-align: top; }}
            .invoice-table th {{ background-color: #f2f2f2; font-weight: bold; }}
            .invoice-table tr.item td {{ border-bottom: 1px solid #eee; }}
            .totals {{ margin-top: 20px; text-align: right; }}
            .totals .total-row {{ font-weight: bold; }}
            h1, h2 {{ color: #000; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <div>
                    <img src="{logo_url}" alt="Logo">
                </div>
                <div class="invoice-details">
                    <h1>Factura #{purchase.id}</h1>
                    <p>
                        Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y')}<br>
                        Fecha de Compra: {purchase.purchase_date_formatted}
                    </p>
                </div>
            </div>
            <div class="addresses">
                <div>
                    <h2>Vendido por:</h2>
                    <p>
                        {SENDER_DETAILS['name']}<br>
                        NIT: {SENDER_DETAILS['nit']}<br>
                        {SENDER_DETAILS['address']}<br>
                        {SENDER_DETAILS['email']}
                    </p>
                </div>
                <div>
                    <h2>Facturado a:</h2>
                    <p>
                        {purchase.shipping_name}<br>
                        {purchase.shipping_address}, {purchase.shipping_neighborhood}<br>
                        {purchase.shipping_city}<br>
                        Tel: {purchase.shipping_phone}
                    </p>
                </div>
            </div>
            <table class="invoice-table">
                <thead>
                    <tr>
                        <th>Cantidad</th>
                        <th>Descripción</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            <div class="totals">
                <p class="total-row"><strong>Total: {format_to_cop(purchase.total_price)}</strong></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Generar el PDF
    pdf_bytes = HTML(string=html_template).write_pdf()
    return pdf_bytes