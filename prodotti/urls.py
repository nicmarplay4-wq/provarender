from django.urls import path
from . import views

app_name = 'prodotti'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('catalogo/', views.CatalogoListView.as_view(), name='catalogo'),
    path('prodotto/<slug:slug>/', views.ProdottoDetailView.as_view(), name='dettaglio'),
]
