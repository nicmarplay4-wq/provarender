from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Cliente, Appuntamento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cognome', 'nome', 'email', 'telefono', 'citta', 'data_registrazione']
    search_fields = ['nome', 'cognome', 'email', 'telefono']
    list_filter = ['citta', 'data_registrazione']
    fieldsets = (
        ('Informazioni Personali', {
            'fields': ('nome', 'cognome', 'email', 'telefono')
        }),
        ('Indirizzo', {
            'fields': ('indirizzo', 'citta', 'cap')
        }),
        ('Note', {
            'fields': ('note',)
        }),
    )

@admin.register(Appuntamento)
class AppuntamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'data_ora', 'tipo_consulenza', 'stato']
    list_filter = ['stato', 'tipo_consulenza', 'data_ora']
    search_fields = ['cliente__nome', 'cliente__cognome', 'note']
    list_editable = ['stato']
    date_hierarchy = 'data_ora'
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Dettagli Appuntamento', {
            'fields': ('data_ora', 'tipo_consulenza', 'stato', 'note')
        }),
    )
    
    actions = ['conferma_appuntamenti', 'invia_promemoria']
    
    @admin.action(description='Conferma appuntamenti selezionati')
    def conferma_appuntamenti(self, request, queryset):
        updated = queryset.filter(stato='RICHIESTO').update(stato='CONFERMATO')
        for appuntamento in queryset.filter(stato='CONFERMATO'):
            self._invia_email_conferma(appuntamento)
        self.message_user(request, f'{updated} appuntamenti confermati.')
    
    @admin.action(description='Invia promemoria email')
    def invia_promemoria(self, request, queryset):
        count = 0
        for appuntamento in queryset.filter(stato='CONFERMATO'):
            self._invia_email_promemoria(appuntamento)
            count += 1
        self.message_user(request, f'Promemoria inviati per {count} appuntamenti.')
    
    def _invia_email_conferma(self, appuntamento):
        subject = 'Conferma Appuntamento - Negozio Cucine'
        message = f"""
        Gentile {appuntamento.cliente.get_nome_completo()},
        
        Il suo appuntamento è stato confermato:
        
        Data e Ora: {appuntamento.data_ora.strftime('%d/%m/%Y alle %H:%M')}
        Tipo: {appuntamento.get_tipo_consulenza_display()}
        
        La aspettiamo presso il nostro showroom.
        
        Cordiali saluti,
        Negozio Cucine
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appuntamento.cliente.email],
            fail_silently=True,
        )
    
    def _invia_email_promemoria(self, appuntamento):
        subject = 'Promemoria Appuntamento - Negozio Cucine'
        message = f"""
        Gentile {appuntamento.cliente.get_nome_completo()},
        
        Le ricordiamo il suo appuntamento:
        
        Data e Ora: {appuntamento.data_ora.strftime('%d/%m/%Y alle %H:%M')}
        Tipo: {appuntamento.get_tipo_consulenza_display()}
        
        A presto,
        Negozio Cucine
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appuntamento.cliente.email],
            fail_silently=True,
        )
