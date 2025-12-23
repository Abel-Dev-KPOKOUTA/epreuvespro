from django.contrib import admin
from django.urls import path , include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('epreuves/', include('epreuves.urls', namespace='epreuves')),
    path('livres/', include('livres.urls', namespace='livres')),     
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('abonnements/', include('abonnements.urls', namespace='abonnements')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),  
    path('', include('core.urls', namespace='core')),   
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)