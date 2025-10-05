from django.db import models
from django.core.validators import EmailValidator, RegexValidator

class Cliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    cognome = models.CharField(max_length=100, verbose_name="Cognome")
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name="Email"
    )
    telefono = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name="Telefono"
    )
    indirizzo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Indirizzo"
    )
    citta = models.CharField(max_length=100, blank=True, verbose_name="Città")
    cap = models.CharField(max_length=10, blank=True, verbose_name="CAP")
    note = models.TextField(blank=True, verbose_name="Note")
    data_registrazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ['cognome', 'nome']
    
    def __str__(self):
        return f"{self.cognome} {self.nome}"
    
    def get_nome_completo(self):
        return f"{self.nome} {self.cognome}"

class Appuntamento(models.Model):
    TIPO_CONSULENZA_CHOICES = [
        ('CONSULENZA', 'Consulenza Progettuale'),
        ('RILIEVO', 'Rilievo Misure'),
        ('PREVENTIVO', 'Discussione Preventivo'),
        ('ALTRO', 'Altro'),
    ]
    
    STATO_CHOICES = [
        ('RICHIESTO', 'Richiesto'),
        ('CONFERMATO', 'Confermato'),
        ('COMPLETATO', 'Completato'),
        ('ANNULLATO', 'Annullato'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='appuntamenti',
        verbose_name="Cliente"
    )
    data_ora = models.DateTimeField(verbose_name="Data e Ora")
    tipo_consulenza = models.CharField(
        max_length=20,
        choices=TIPO_CONSULENZA_CHOICES,
        default='CONSULENZA',
        verbose_name="Tipo Consulenza"
    )
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='RICHIESTO',
        verbose_name="Stato"
    )
    note = models.TextField(blank=True, verbose_name="Note")
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Appuntamento"
        verbose_name_plural = "Appuntamenti"
        ordering = ['-data_ora']
    
    def __str__(self):
        return f"{self.cliente} - {self.data_ora.strftime('%d/%m/%Y %H:%M')}"
