from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Prodotto, Categoria

def homepage(request):
    prodotti_evidenza = Prodotto.objects.filter(
        in_evidenza=True, 
        disponibile=True
    )[:6]
    categorie = Categoria.objects.all()[:4]
    context = {
        'prodotti_evidenza': prodotti_evidenza,
        'categorie': categorie,
    }
    return render(request, 'prodotti/homepage.html', context)

class CatalogoListView(ListView):
    model = Prodotto
    template_name = 'prodotti/catalogo.html'
    context_object_name = 'prodotti'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Prodotto.objects.filter(disponibile=True)
        categoria_slug = self.request.GET.get('categoria')
        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorie'] = Categoria.objects.all()
        context['categoria_selezionata'] = self.request.GET.get('categoria', '')
        return context

class ProdottoDetailView(DetailView):
    model = Prodotto
    template_name = 'prodotti/prodotto_dettaglio.html'
    context_object_name = 'prodotto'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prodotti_correlati'] = Prodotto.objects.filter(
            categoria=self.object.categoria,
            disponibile=True
        ).exclude(id=self.object.id)[:4]
        return context
