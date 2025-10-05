from django.contrib import admin
from .models import Categoria, Prodotto, ImmagineProdotto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ordine']
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ['nome']
    list_editable = ['ordine']

class ImmagineInline(admin.TabularInline):
    model = ImmagineProdotto
    extra = 1
    fields = ['file_immagine', 'alt_text', 'ordine', 'is_principale']

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'prezzo_base', 'disponibile', 'in_evidenza']
    list_filter = ['categoria', 'disponibile', 'in_evidenza', 'data_creazione']
    search_fields = ['nome', 'descrizione']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['prezzo_base', 'disponibile', 'in_evidenza']
    inlines = [ImmagineInline]
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('categoria', 'nome', 'slug', 'descrizione')
        }),
        ('Dettagli Tecnici', {
            'fields': ('specifiche_tecniche', 'prezzo_base')
        }),
        ('Disponibilità', {
            'fields': ('disponibile', 'in_evidenza')
        }),
    )
    
    actions = ['marca_disponibile', 'marca_non_disponibile', 'marca_in_evidenza']
    
    @admin.action(description='Marca come disponibile')
    def marca_disponibile(self, request, queryset):
        updated = queryset.update(disponibile=True)
        self.message_user(request, f'{updated} prodotti marcati come disponibili.')
    
    @admin.action(description='Marca come non disponibile')
    def marca_non_disponibile(self, request, queryset):
        updated = queryset.update(disponibile=False)
        self.message_user(request, f'{updated} prodotti marcati come non disponibili.')
    
    @admin.action(description='Metti in evidenza')
    def marca_in_evidenza(self, request, queryset):
        updated = queryset.update(in_evidenza=True)
        self.message_user(request, f'{updated} prodotti messi in evidenza.')
