"""
Utils pour l'export des documents en PDF et Excel.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from django.utils import timezone


# ==========================================
# PDF EXPORTS
# ==========================================

def _get_base_style():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title2',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#4f5eff'),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
    ))
    styles.add(ParagraphStyle(
        name='Section',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1c2130'),
        spaceBefore=12,
        spaceAfter=6,
    ))
    return styles


def generate_product_list_pdf(products, language='fr'):
    """Génère un PDF de la liste des produits."""
    styles = _get_base_style()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    
    title = {
        'fr': 'Liste des Produits',
        'en': 'Product List',
        'zh-hans': '产品列表',
        'hi': 'उत्पाद सूची',
    }.get(language, 'Liste des Produits')
    
    subtitle = f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
    
    elements = [
        Paragraph(title, styles['Title2']),
        Paragraph(subtitle, styles['Subtitle']),
        Spacer(1, 15*mm),
    ]
    
    headers = ['Réf.', 'Nom', 'Catégorie', 'Prix Unitaire', 'Stock', 'Statut']
    data = [headers]
    
    for p in products:
        cat = p.categorie.nom if p.categorie else '-'
        status = 'Actif' if p.actif else 'Inactif'
        stock = str(p.quantite_totale)
        data.append([p.reference, p.nom, cat, f'{p.prix_unitaire} €', stock, status])
    
    table = Table(data, colWidths=[50, 80, 50, 40, 30, 35])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f5eff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e8ef')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafc')]),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_order_pdf(order, language='fr'):
    """Génère un PDF de la commande/facture."""
    styles = _get_base_style()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    
    title_map = {
        'fr': {'title': 'FACTURE', 'client': 'Client', 'date': 'Date', 'total': 'TOTAL'},
        'en': {'title': 'INVOICE', 'client': 'Customer', 'date': 'Date', 'total': 'TOTAL'},
        'zh-hans': {'title': '发票', 'client': '客户', 'date': '日期', 'total': '总计'},
        'hi': {'title': 'चालान', 'client': 'ग्राहक', 'date': 'दिनांक', 'total': 'कुल'},
    }
    t = title_map.get(language, title_map['fr'])
    
    elements = [
        Paragraph('Ava', styles['Title2']),
        Paragraph(f"{t['title']} #{order.pk}", styles['Heading1']),
        Spacer(1, 5*mm),
        Paragraph(f"<b>{t['client']}:</b> {order.client.nom}", styles['Normal']),
        Paragraph(f"<b>{t['date']}:</b> {order.cree_le.strftime('%d/%m/%Y')}", styles['Normal']),
        Spacer(1, 10*mm),
    ]
    
    headers = [t.get('product', 'Produit'), t.get('qty', 'Qté'), t.get('price', 'Prix'), t.get('subtotal', 'Total')]
    data = [headers]
    
    for ligne in order.lignes.all():
        data.append([
            ligne.produit.nom,
            str(ligne.quantite),
            f'{ligne.prix_unitaire} €',
            f'{ligne.sous_total} €',
        ])
    
    data.append(['', '', t['total'], f'{order.montant_total} €'])
    
    table = Table(data, colWidths=[100, 30, 50, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f5eff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e8ef')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4f5eff')),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_purchase_order_pdf(po, language='fr'):
    """Génère un PDF du bon de commande fournisseur."""
    styles = _get_base_style()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    
    elements = [
        Paragraph('Ava', styles['Title2']),
        Paragraph(f"BON DE COMMANDE #{po.reference}", styles['Heading1']),
        Spacer(1, 5*mm),
        Paragraph(f"<b>Fournisseur:</b> {po.fournisseur.nom}", styles['Normal']),
        Paragraph(f"<b>Date:</b> {po.cree_le.strftime('%d/%m/%Y')}", styles['Normal']),
        Paragraph(f"<b>Statut:</b> {po.get_statut_display()}", styles['Normal']),
        Spacer(1, 10*mm),
    ]
    
    headers = ['Produit', 'Qté commandée', 'Qté reçue', 'Prix', 'Total']
    data = [headers]
    
    for ligne in po.lignes.all():
        data.append([
            ligne.produit.nom,
            str(ligne.quantite_commandee),
            str(ligne.quantite_recue),
            f'{ligne.prix_unitaire} €',
            f'{ligne.montant_ligne} €',
        ])
    
    data.append(['', '', '', 'TOTAL', f'{po.montant_total} €'])
    
    table = Table(data, colWidths=[90, 40, 40, 45, 45])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f5eff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e8ef')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#4f5eff')),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_movement_pdf(movements, language='fr'):
    """Génère un PDF de l'historique des mouvements de stock."""
    styles = _get_base_style()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    
    elements = [
        Paragraph('Ava', styles['Title2']),
        Paragraph('Historique des Mouvements de Stock', styles['Heading1']),
        Paragraph(f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}", styles['Subtitle']),
        Spacer(1, 10*mm),
    ]
    
    headers = ['Date', 'Produit', 'Type', 'Qté', 'Entrepôt', 'Motif']
    data = [headers]
    
    for m in movements:
        type_display = {
            'entree': 'Entrée', 'sortie': 'Sortie',
            'ajustement': 'Ajustement', 'transfert': 'Transfert'
        }.get(m.type_mouvement, m.type_mouvement)
        data.append([
            m.cree_le.strftime('%d/%m/%Y'),
            m.produit.nom[:30],
            type_display,
            f'+{m.quantite}' if m.type_mouvement == 'entree' else f'-{m.quantite}',
            str(m.entrepot)[:20],
            m.motif[:25] if m.motif else '-',
        ])
    
    table = Table(data, colWidths=[40, 60, 40, 25, 40, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f5eff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e8ef')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafc')]),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


# ==========================================
# EXCEL EXPORTS
# ==========================================

def _get_xl_border():
    thin = Side(style='thin', color='e5e8ef')
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _get_xl_header_fill():
    return PatternFill(start_color='4f5eff', end_color='4f5eff', fill_type='solid')


def _get_xl_alt_fill():
    return PatternFill(start_color='f9fafc', end_color='f9fafc', fill_type='solid')


def generate_product_list_excel(products, language='fr'):
    """Génère un fichier Excel de la liste des produits."""
    wb = Workbook()
    ws = wb.active
    ws.title = {
        'fr': 'Produits', 'en': 'Products',
        'zh-hans': '产品', 'hi': 'उत्पाद'
    }.get(language, 'Produits')
    
    # En-têtes
    headers = {
        'fr': ['Référence', 'Nom', 'Catégorie', 'Unité', 'Prix Unitaire', 'Stock', 'Alerte', 'Actif'],
        'en': ['Reference', 'Name', 'Category', 'Unit', 'Unit Price', 'Stock', 'Alert', 'Active'],
        'zh-hans': ['参考', '名称', '类别', '单位', '单价', '库存', '警报', '活跃'],
        'hi': ['संदर्भ', 'नाम', 'श्रेणी', 'इकाई', 'इकाई मूल्य', 'स्टॉक', 'अलर्ट', 'सक्रिय'],
    }.get(language, headers)
    headers = ['Référence', 'Nom', 'Catégorie', 'Unité', 'Prix Unitaire', 'Stock', 'Alerte', 'Actif']
    
    ws.append(headers)
    
    # Style en-têtes
    for cell in ws[1]:
        cell.font = Font(bold=True, color='ffffff')
        cell.fill = _get_xl_header_fill()
        cell.alignment = Alignment(horizontal='center')
        cell.border = _get_xl_border()
    
    # Données
    for i, p in enumerate(products, 2):
        row = [
            p.reference,
            p.nom,
            p.categorie.nom if p.categorie else '',
            p.unite,
            float(p.prix_unitaire),
            p.quantite_totale,
            p.seuil_alerte,
            'Oui' if p.actif else 'Non',
        ]
        ws.append(row)
        
        fill = _get_xl_alt_fill() if i % 2 == 0 else PatternFill()
        for cell in ws[i]:
            cell.fill = fill
            cell.border = _get_xl_border()
    
    # Ajuster lesLargeurs
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 10
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 8
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def generate_order_excel(order, language='fr'):
    """Génère un fichier Excel de la commande."""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Commande_{order.pk}"
    
    # Info commande
    ws.append(['FACTURE', f'#{order.pk}'])
    ws.append(['Client', order.client.nom])
    ws.append(['Date', order.cree_le.strftime('%d/%m/%Y')])
    ws.append([])
    
    # En-têtes produits
    headers = ['Produit', 'Quantité', 'Prix Unitaire', 'Sous-total']
    ws.append(headers)
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True, color='ffffff')
        cell.fill = _get_xl_header_fill()
        cell.border = _get_xl_border()
    
    # Lignes
    for ligne in order.lignes.all():
        ws.append([
            ligne.produit.nom,
            ligne.quantite,
            float(ligne.prix_unitaire),
            float(ligne.sous_total),
        ])
    
    # Total
    ws.append([])
    ws.append(['TOTAL', '', '', float(order.montant_total)])
    ws[ws.max_row][0].font = Font(bold=True)
    ws[ws.max_row][3].font = Font(bold=True)
    
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def generate_purchase_order_excel(po, language='fr'):
    """Génère un fichier Excel du bon de commande."""
    wb = Workbook()
    ws = wb.active
    ws.title = f"BC_{po.reference}"
    
    ws.append(['BON DE COMMANDE', po.reference])
    ws.append(['Fournisseur', po.fournisseur.nom])
    ws.append(['Date', po.cree_le.strftime('%d/%m/%Y')])
    ws.append(['Statut', po.get_statut_display()])
    ws.append([])
    
    headers = ['Produit', 'Qté Commandée', 'Qté Reçue', 'Prix Unitaire', 'Total Ligne']
    ws.append(headers)
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True, color='ffffff')
        cell.fill = _get_xl_header_fill()
        cell.border = _get_xl_border()
    
    for ligne in po.lignes.all():
        ws.append([
            ligne.produit.nom,
            ligne.quantite_commandee,
            ligne.quantite_recue,
            float(ligne.prix_unitaire),
            float(ligne.montant_ligne),
        ])
    
    ws.append([])
    ws.append(['TOTAL', '', '', '', float(po.montant_total)])
    ws[ws.max_row][0].font = Font(bold=True)
    ws[ws.max_row][4].font = Font(bold=True)
    
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def generate_movement_excel(movements, language='fr'):
    """Génère un fichier Excel de l'historique des mouvements."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Mouvements'
    
    headers = ['Date', 'Produit', 'Entrepôt', 'Type', 'Quantité', 'Motif', 'Utilisateur']
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True, color='ffffff')
        cell.fill = _get_xl_header_fill()
        cell.border = _get_xl_border()
    
    for i, m in enumerate(movements, 2):
        type_display = {
            'entree': 'Entrée', 'sortie': 'Sortie',
            'ajustement': 'Ajustement', 'transfert': 'Transfert'
        }.get(m.type_mouvement, m.type_mouvement)
        ws.append([
            m.cree_le.strftime('%d/%m/%Y %H:%M'),
            m.produit.nom,
            str(m.entrepot),
            type_display,
            m.quantite,
            m.motif or '',
            str(m.effectue_par) if m.effectue_par else '',
        ])
        if i % 2 == 0:
            for cell in ws[i]:
                cell.fill = _get_xl_alt_fill()
                cell.border = _get_xl_border()
    
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 25
    ws.column_dimensions['G'].width = 15
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
