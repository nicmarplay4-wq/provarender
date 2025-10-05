from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from .models import Preventivo, VocePreventivo

class VocePreventivoInline(admin.TabularInline):
    model = VocePreventivo
    extra = 1
    fields = ['prodotto', 'quantita', 'prezzo_unitario_finale', 'note', 'ordine']
    autocomplete_fields = ['prodotto']

@admin.register(Preventivo)
class PreventivoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_preventivo',
        'cliente',
        'data_creazione',
        'stato',
        'totale_stimato',
        'azioni_preventivo'
    ]
    list_filter = ['stato', 'data_creazione']
    search_fields = [
        'numero_preventivo',
        'cliente__nome',
        'cliente__cognome',
        'cliente__email'
    ]
    readonly_fields = ['numero_preventivo', 'totale_stimato', 'data_creazione']
    inlines = [VocePreventivoInline]
    autocomplete_fields = ['cliente']
    
    fieldsets = (
        ('Informazioni Cliente', {
            'fields': ('cliente', 'numero_preventivo')
        }),
        ('Stato e Importo', {
            'fields': ('stato', 'totale_stimato', 'sconto_percentuale')
        }),
        ('Dettagli', {
            'fields': ('validita_giorni', 'note', 'data_creazione')
        }),
    )
    
    actions = [
        'marca_come_inviato',
        'marca_come_accettato',
        'genera_pdf',
        'invia_email_preventivo'
    ]
    
    def azioni_preventivo(self, obj):
        pdf_url = reverse('admin:preventivi_preventivo_pdf', args=[obj.pk])
        email_url = reverse('admin:preventivi_preventivo_email', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">PDF</a>&nbsp;'
            '<a class="button" href="{}">Email</a>',
            pdf_url, email_url
        )
    azioni_preventivo.short_description = 'Azioni'
    
    @admin.action(description='Marca come Inviato')
    def marca_come_inviato(self, request, queryset):
        updated = queryset.update(stato='INVIATO')
        self.message_user(request, f'{updated} preventivi marcati come inviati.')
    
    @admin.action(description='Marca come Accettato')
    def marca_come_accettato(self, request, queryset):
        updated = queryset.update(stato='ACCETTATO')
        self.message_user(request, f'{updated} preventivi marcati come accettati.')
    
    @admin.action(description='Genera PDF')
    def genera_pdf(self, request, queryset):
        if queryset.count() == 1:
            preventivo = queryset.first()
            return self._genera_pdf_response(preventivo)
        else:
            self.message_user(request, 'Seleziona un solo preventivo per generare il PDF.')
    
    @admin.action(description='Invia Email con PDF')
    def invia_email_preventivo(self, request, queryset):
        count = 0
        for preventivo in queryset:
            self._invia_email_con_pdf(preventivo)
            preventivo.stato = 'INVIATO'
            preventivo.save()
            count += 1
        self.message_user(request, f'{count} preventivi inviati via email.')
    
    def _genera_pdf_reportlab(self, preventivo):
        """Genera PDF usando ReportLab"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        # Container per gli elementi del PDF
        elements = []
        styles = getSampleStyleSheet()
        
        # Stile personalizzato per il titolo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Titolo
        elements.append(Paragraph("PREVENTIVO", title_style))
        elements.append(Paragraph(f"N. {preventivo.numero_preventivo}", styles['Normal']))
        elements.append(Paragraph(f"Data: {preventivo.data_creazione.strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Dati Cliente
        elements.append(Paragraph("<b>Dati Cliente</b>", styles['Heading2']))
        cliente_info = f"""
        <b>Nome:</b> {preventivo.cliente.get_nome_completo()}<br/>
        <b>Email:</b> {preventivo.cliente.email}<br/>
        <b>Telefono:</b> {preventivo.cliente.telefono}<br/>
        """
        if preventivo.cliente.indirizzo:
            cliente_info += f"<b>Indirizzo:</b> {preventivo.cliente.indirizzo}, {preventivo.cliente.cap} {preventivo.cliente.citta}"
        
        elements.append(Paragraph(cliente_info, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tabella Prodotti
        elements.append(Paragraph("<b>Dettaglio Prodotti</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Dati tabella
        data = [['Prodotto', 'Qtà', 'Prezzo Unit.', 'Totale']]
        
        for voce in preventivo.voci.all():
            prodotto_info = f"{voce.prodotto.nome}"
            if voce.note:
                prodotto_info += f"\n{voce.note}"
            
            data.append([
                prodotto_info,
                str(voce.quantita),
                f"€ {voce.prezzo_unitario_finale}",
                f"€ {voce.get_totale()}"
            ])
        
        # Crea tabella
        table = Table(data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Sconto e Totale
        if preventivo.sconto_percentuale > 0:
            subtotale = preventivo.calcola_totale() + (preventivo.totale_stimato * preventivo.sconto_percentuale / 100)
            sconto_text = f"""
            <b>Subtotale:</b> € {subtotale:.2f}<br/>
            <b>Sconto {preventivo.sconto_percentuale}%:</b> - € {(subtotale - preventivo.totale_estimato):.2f}<br/>
            """
            elements.append(Paragraph(sconto_text, styles['Normal']))
        
        # Totale in grande
        totale_style = ParagraphStyle(
            'Totale',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=2  # Right
        )
        elements.append(Paragraph(f"<b>TOTALE: € {preventivo.totale_stimato}</b>", totale_style))
        
        # Note
        if preventivo.note:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("<b>Note</b>", styles['Heading2']))
            elements.append(Paragraph(preventivo.note, styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1  # Center
        )
        footer_text = f"""
        <b>Negozio Cucine</b><br/>
        Via Example 123, 00100 Roma<br/>
        Tel: +39 123 456 7890 | Email: info@negoziocucine.it<br/>
        P.IVA: 12345678900<br/>
        <br/>
        Il presente preventivo ha validità di <b>{preventivo.validita_giorni} giorni</b> dalla data di emissione.
        """
        elements.append(Paragraph(footer_text, footer_style))
        
        # Costruisci PDF
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def _genera_pdf_response(self, preventivo):
        """Genera e restituisce PDF come risposta HTTP"""
        pdf_buffer = self._genera_pdf_reportlab(preventivo)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="preventivo_{preventivo.numero_preventivo}.pdf"'
        return response
    
    def _invia_email_con_pdf(self, preventivo):
        """Invia email con PDF allegato"""
        pdf_buffer = self._genera_pdf_reportlab(preventivo)
        
        email = EmailMessage(
            subject=f'Preventivo {preventivo.numero_preventivo} - Negozio Cucine',
            body=f"""
            Gentile {preventivo.cliente.get_nome_completo()},
            
            In allegato trova il preventivo richiesto.
            
            Il preventivo ha validità di {preventivo.validita_giorni} giorni dalla data di emissione.
            
            Per qualsiasi chiarimento non esiti a contattarci.
            
            Cordiali saluti,
            Negozio Cucine
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[preventivo.cliente.email],
        )
        email.attach(
            f'preventivo_{preventivo.numero_preventivo}.pdf',
            pdf_buffer.read(),
            'application/pdf'
        )
        email.send()
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:preventivo_id>/pdf/',
                self.admin_site.admin_view(self.pdf_view),
                name='preventivi_preventivo_pdf',
            ),
            path(
                '<int:preventivo_id>/email/',
                self.admin_site.admin_view(self.email_view),
                name='preventivi_preventivo_email',
            ),
        ]
        return custom_urls + urls
    
    def pdf_view(self, request, preventivo_id):
        preventivo = Preventivo.objects.get(pk=preventivo_id)
        return self._genera_pdf_response(preventivo)
    
    def email_view(self, request, preventivo_id):
        preventivo = Preventivo.objects.get(pk=preventivo_id)
        self._invia_email_con_pdf(preventivo)
        preventivo.stato = 'INVIATO'
        preventivo.save()
        self.message_user(request, f'Preventivo {preventivo.numero_preventivo} inviato via email.')
        return HttpResponse(status=302, headers={'Location': request.META.get('HTTP_REFERER')})

@admin.register(VocePreventivo)
class VocePreventivoAdmin(admin.ModelAdmin):
    list_display = ['preventivo', 'prodotto', 'quantita', 'prezzo_unitario_finale', 'get_totale']
    list_filter = ['preventivo__stato']
    search_fields = ['preventivo__numero_preventivo', 'prodotto__nome']
    autocomplete_fields = ['preventivo', 'prodotto']
