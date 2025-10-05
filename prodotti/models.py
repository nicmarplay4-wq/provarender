from django.db import models
from django.utils.text import slugify

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome Categoria")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descrizione = models.TextField(blank=True, verbose_name="Descrizione")
    ordine = models.IntegerField(default=0, verbose_name="Ordine di visualizzazione")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ['ordine', 'nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

class Prodotto(models.Model):
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='prodotti',
        verbose_name="Categoria"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome Prodotto")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    descrizione = models.TextField(verbose_name="Descrizione")
    specifiche_tecniche = models.TextField(blank=True, verbose_name="Specifiche Tecniche")
    prezzo_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Prezzo Base (€)"
    )
    disponibile = models.BooleanField(default=True, verbose_name="Disponibile")
    in_evidenza = models.BooleanField(default=False, verbose_name="In Evidenza")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"
        ordering = ['-in_evidenza', 'nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    def get_immagine_principale(self):
        immagine = self.immagini.first()
        return immagine.file_immagine.url if immagine else None

class ImmagineProdotto(models.Model):
    prodotto = models.ForeignKey(
        Prodotto,
        on_delete=models.CASCADE,
        related_name='immagini',
        verbose_name="Prodotto"
    )
    file_immagine = models.ImageField(
        upload_to='prodotti/%Y/%m/',
        verbose_name="Immagine"
    )
    alt_text = models.CharField(
        max_length=200,
        verbose_name="Testo alternativo",
        help_text="Descrizione dell'immagine per SEO e accessibilità"
    )
    ordine = models.IntegerField(default=0, verbose_name="Ordine")
    is_principale = models.BooleanField(
        default=False,
        verbose_name="Immagine Principale"
    )
    
    class Meta:
        verbose_name = "Immagine Prodotto"
        verbose_name_plural = "Immagini Prodotto"
        ordering = ['-is_principale', 'ordine']
    
    def __str__(self):
        return f"Immagine di {self.prodotto.nome}"
