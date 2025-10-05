from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from clienti.models import Cliente
from prodotti.models import Prodotto

class Preventivo(models.Model):
    STATO_CHOICES = [
        ('BOZZA', 'Bozza'),
        ('INVIATO', 'Inviato'),
        ('ACCETTATO', 'Accettato'),
        ('RIFIUTATO', 'Rifiutato'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='preventivi',
        verbose_name="Cliente"
    )
    numero_preventivo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numero Preventivo"
    )
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='BOZZA',
        verbose_name="Stato"
    )
    totale_stimato = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Totale Stimato (€)"
    )
    sconto_percentuale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Sconto (%)"
    )
    note = models.TextField(blank=True, verbose_name="Note")
    validita_giorni = models.IntegerField(
        default=30,
        verbose_name="Validità (giorni)"
    )
    
    class Meta:
        verbose_name = "Preventivo"
        verbose_name_plural = "Preventivi"
        ordering = ['-data_creazione']
    
    def __str__(self):
        return f"Preventivo {self.numero_preventivo} - {self.cliente}"
    
    def save(self, *args, **kwargs):
        if not self.numero_preventivo:
            ultimo = Preventivo.objects.order_by('-id').first()
            if ultimo:
                numero = int(ultimo.numero_preventivo.split('-')[1]) + 1
            else:
                numero = 1
            self.numero_preventivo = f"PREV-{numero:05d}"
        super().save(*args, **kwargs)
    
    def calcola_totale(self):
        subtotale = sum(voce.get_totale() for voce in self.voci.all())
        sconto = subtotale * (self.sconto_percentuale / 100)
        return subtotale - sconto
    
    def aggiorna_totale(self):
        self.totale_stimato = self.calcola_totale()
        self.save(update_fields=['totale_stimato'])

class VocePreventivo(models.Model):
    preventivo = models.ForeignKey(
        Preventivo,
        on_delete=models.CASCADE,
        related_name='voci',
        verbose_name="Preventivo"
    )
    prodotto = models.ForeignKey(
        Prodotto,
        on_delete=models.PROTECT,
        verbose_name="Prodotto"
    )
    quantita = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantità"
    )
    prezzo_unitario_finale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prezzo Unitario (€)"
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Note"
    )
    ordine = models.IntegerField(default=0, verbose_name="Ordine")
    
    class Meta:
        verbose_name = "Voce Preventivo"
        verbose_name_plural = "Voci Preventivo"
        ordering = ['ordine', 'id']
    
    def __str__(self):
        return f"{self.prodotto.nome} x {self.quantita}"
    
    def save(self, *args, **kwargs):
        if not self.prezzo_unitario_finale:
            self.prezzo_unitario_finale = self.prodotto.prezzo_base
        super().save(*args, **kwargs)
        self.preventivo.aggiorna_totale()
    
    def delete(self, *args, **kwargs):
        preventivo = self.preventivo
        super().delete(*args, **kwargs)
        preventivo.aggiorna_totale()
    
    def get_totale(self):
        return self.quantita * self.prezzo_unitario_finale
