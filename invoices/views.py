from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from orders.models import Order
from .models import Invoice
from io import BytesIO


@login_required
def generate_invoice(request, order_id):
    """Generate PDF invoice for an order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permission
    if not request.user.is_superuser and order.user != request.user:
        return HttpResponse('Unauthorized', status=403)
    
    # Get or create invoice
    invoice, created = Invoice.objects.get_or_create(order=order)
    
    # Generate PDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=20
    )
    elements.append(Paragraph('IndiVibe', title_style))
    elements.append(Paragraph(f'Invoice: {invoice.invoice_number}', styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Order details
    elements.append(Paragraph(f'Order Number: {order.order_number}', styles['Normal']))
    elements.append(Paragraph(f'Date: {order.created_at.strftime("%d-%m-%Y")}', styles['Normal']))
    elements.append(Paragraph(f'Customer: {order.user.username}', styles['Normal']))
    if order.address:
        elements.append(Paragraph(f'Address: {order.address.full_address}', styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Items table
    table_data = [['Product', 'Qty', 'Price', 'Total']]
    for item in order.items.all():
        table_data.append([
            item.product_name,
            str(item.quantity),
            f'₹{item.price}',
            f'₹{item.total_price}'
        ])
    
    table_data.append(['', '', 'Subtotal:', f'₹{order.total_amount}'])
    if order.discount_amount > 0:
        table_data.append(['', '', 'Discount:', f'-₹{order.discount_amount}'])
    table_data.append(['', '', 'Total:', f'₹{order.final_amount}'])
    
    table = Table(table_data, colWidths=[3*inch, 0.75*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
        ('FONTNAME', (-2, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('Thank you for shopping with IndiVibe!', styles['Normal']))
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
    return response


@login_required
def download_invoice(request, invoice_id):
    """Download existing invoice PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if not request.user.is_superuser and invoice.order.user != request.user:
        return HttpResponse('Unauthorized', status=403)
    
    if invoice.pdf_file:
        return FileResponse(invoice.pdf_file.open(), as_attachment=True)
    
    # Generate if not exists
    return generate_invoice(request, invoice.order.id)
