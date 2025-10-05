from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('prodotti.urls')),
    path('clienti/', include('clienti.urls')),
    path('preventivi/', include('preventivi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Amministrazione Negozio Cucine"
admin.site.site_title = "Admin Negozio Cucine"
admin.site.index_title = "Benvenuto nel Pannello Amministrativo"


