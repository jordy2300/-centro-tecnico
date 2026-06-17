from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path('', views.panel, name='materiales_panel'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/<uuid:pk>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<uuid:pk>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitudes/<uuid:pk>/observacion/', views.editar_observacion, name='editar_observacion'),
    path('exportar/', views.exportar_excel_view, name='exportar_materiales'),
    path('cuadrillas/', views.gestion_cuadrillas, name='gestion_cuadrillas'),
    path('cuadrillas/crear/', views.crear_cuadrilla, name='crear_cuadrilla'),
    path('importar/', views.importar_materiales_view, name='importar_materiales'),
    # Admin alias for panel
    path('admin/', views.panel, name='panel_materiales_admin'),
    # Almacén
    path('almacen/', views.almacen_panel, name='almacen_panel'),
    path('almacen/<uuid:pk>/entregar/', views.almacen_entregar, name='almacen_entregar'),
    # Técnico
    path('tecnico/login/', views.tecnico_login, name='tecnico_login'),
    path('tecnico/logout/', views.tecnico_logout, name='tecnico_logout'),
    path('tecnico/', views.tecnico_solicitudes, name='tecnico_solicitudes'),
    path('tecnico/historial/', views.tecnico_historial, name='tecnico_historial'),
    path('tecnico/nueva/', views.tecnico_nueva_solicitud, name='tecnico_nueva_solicitud'),
    path('tecnico/<uuid:pk>/editar/', views.tecnico_editar_solicitud, name='tecnico_editar_solicitud'),
    # API
    path('api/materiales/', views.api_buscar_material, name='api_buscar_material'),
    path('exportar/plantilla/', views.exportar_plantilla_cuadrilla, name='exportar_plantilla'),
]
