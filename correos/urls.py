from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_correos, name='lista_correos'),
    path('nuevo/', views.nuevo_correo, name='nuevo_correo'),
    path('<int:pk>/editar/', views.editar_correo, name='editar_correo'),
    path('<int:pk>/eliminar/', views.eliminar_correo, name='eliminar_correo'),
    path('<int:pk>/estado/', views.cambiar_estado_rapido, name='cambiar_estado_correo'),
    path('<int:pk>/revision/', views.cambiar_revision, name='cambiar_revision_correo'),
    path('<int:pk>/', views.detalle_correo, name='detalle_correo'),
]
