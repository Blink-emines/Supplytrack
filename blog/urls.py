# blog/urls.py
from django.urls import path
from . import views  # On importe tes vues ici

urlpatterns = [
    path('', views.dashboard_view, name='root'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('suivi-demandes/', views.suivi_view, name='suivi_demandes'),
    path('suivi/detail/<str:id_flux>/<str:id_ise>/<str:id_da>/<str:id_ao>/<str:id_cmd>/', views.detail_flux, name='detail_flux'),
    path('import/ise/', views.import_ise, name='import_ise'),
    path('import/da/', views.import_da, name='import_da'),
    path('import/ao/', views.import_ao, name='import_ao'),
    path('import/cmd/', views.import_cmd, name='import_cmd'),
    path('parametres/', views.parametres, name='parametres'),
    path('api/update-profile/', views.update_profile, name='update_profile'),
    path('analyses/', views.analyses, name='analyses'),
    path('import/history/', views.get_import_history, name='import_history'),
    path('help/', views.help, name='help'),
]
